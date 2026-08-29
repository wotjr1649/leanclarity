'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const crypto = require('node:crypto');
const { once } = require('node:events');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { TextDecoder } = require('node:util');

const root = path.resolve(__dirname, '..');
const runtimePath = path.join(root, 'hooks', 'leanclarity.cjs');
const runtime = require(runtimePath);
const candidateFiles = [
  '.claude-plugin/plugin.json',
  '.codex-plugin/plugin.json',
  'LICENSE',
  'README.md',
  'THIRD_PARTY_NOTICES.md',
  'hooks/hooks.json',
  'hooks/leanclarity.cjs',
  'policies/engineering.md',
  'policies/guidance.md',
];
// Marketplace catalogs that let the hosts install the candidate from this repository (Claude format, which
// Codex also reads as legacy-compatible, plus the Codex git catalog); never part of the candidate distribution.
const localCatalogs = {
  claude: '.claude-plugin/marketplace.json',
  codex: '.agents/plugins/marketplace.json',
};
const repositoryUrl = 'https://github.com/wotjr1649/leanclarity.git';
const policyPaths = {
  Engineering: path.join(root, 'policies', 'engineering.md'),
  Guidance: path.join(root, 'policies', 'guidance.md'),
};

function readPolicy(name) {
  const file = policyPaths[name];
  const stat = fs.lstatSync(file);
  assert.equal(stat.isFile(), true, `${name} policy must be a regular file`);
  assert.equal(stat.isSymbolicLink(), false, `${name} policy must not be a link`);
  assert.ok(stat.size <= 1024 * 1024, `${name} policy exceeds 1 MiB`);
  const text = new TextDecoder('utf-8', { fatal: true }).decode(fs.readFileSync(file));
  assert.ok(text.trim(), `${name} policy must not be empty`);
  assert.equal((text.match(/^# /gm) || []).length, 1, `${name} policy must have one top-level heading`);
  return text;
}

function occurrences(haystack, needle) {
  return haystack.split(needle).length - 1;
}

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex').toUpperCase();
}

function candidateIdentity() {
  const entries = candidateFiles.map((relative) => {
    const bytes = fs.readFileSync(path.join(root, relative));
    return { path: relative, bytes: bytes.length, sha256: sha256(bytes) };
  });
  const manifest = entries.map((entry) => `${entry.path}\t${entry.bytes}\t${entry.sha256}\n`).join('');
  return { entries, manifest, sha256: sha256(Buffer.from(manifest, 'utf8')) };
}

function walkFiles(relative) {
  const found = [];
  for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true })) {
    const child = path.posix.join(relative.replaceAll('\\', '/'), entry.name);
    if (entry.isDirectory()) found.push(...walkFiles(child));
    else found.push(child);
  }
  return found;
}

function walkDirectory(directory) {
  const found = [];
  const visit = (current) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const file = path.join(current, entry.name);
      if (entry.isDirectory()) visit(file);
      else {
        const bytes = fs.readFileSync(file);
        found.push({ path: path.relative(directory, file).replaceAll('\\', '/'), bytes: bytes.length, sha256: sha256(bytes) });
      }
    }
  };
  visit(directory);
  return found.sort((left, right) => left.path.localeCompare(right.path));
}

function makePlugin(t, { engineering = 'Engineering fixture', guidance = 'Guidance fixture' } = {}) {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'leanclarity phase2 '));
  const pluginRoot = path.join(base, 'plugin root');
  const dataRoot = path.join(base, 'plugin data');
  fs.mkdirSync(path.join(pluginRoot, 'policies'), { recursive: true });
  fs.mkdirSync(dataRoot);
  if (engineering !== null) fs.writeFileSync(path.join(pluginRoot, 'policies', 'engineering.md'), engineering);
  if (guidance !== null) fs.writeFileSync(path.join(pluginRoot, 'policies', 'guidance.md'), guidance);
  t.after(() => fs.rmSync(base, { recursive: true, force: true }));
  return { base, pluginRoot, dataRoot, engineering, guidance };
}

function claudeEnv(plugin) {
  return { CLAUDE_PLUGIN_ROOT: plugin.pluginRoot, CLAUDE_PLUGIN_DATA: plugin.dataRoot };
}

function codexEnv(plugin) {
  return { PLUGIN_ROOT: plugin.pluginRoot, PLUGIN_DATA: plugin.dataRoot };
}

function childEnv(extra = {}) {
  return Object.fromEntries(Object.entries({
    SystemRoot: process.env.SystemRoot,
    TEMP: process.env.TEMP,
    TMP: process.env.TMP,
    ...extra,
  }).filter(([, value]) => value !== undefined));
}

function runHook(input, env) {
  return childProcess.spawnSync(process.execPath, [runtimePath], {
    input,
    env: childEnv(env),
    encoding: 'utf8',
    timeout: 3000,
    windowsHide: true,
  });
}

async function waitForExit(child, timeoutMs) {
  const outcome = await Promise.race([
    once(child, 'exit').then(([code, signal]) => ({ code, signal })),
    new Promise((resolve) => setTimeout(() => resolve(null), timeoutMs)),
  ]);
  if (!outcome) child.kill();
  return outcome;
}

function failOnce(method, predicate = () => true, { after = false } = {}) {
  let failed = false;
  return new Proxy(fs, {
    get(target, property) {
      const original = target[property];
      if (property !== method || typeof original !== 'function') {
        return typeof original === 'function' ? original.bind(target) : original;
      }
      return (...args) => {
        if (!failed && predicate(...args)) {
          failed = true;
          if (after) original(...args);
          const error = new Error(`injected ${method} failure`);
          error.code = 'EIO';
          throw error;
        }
        return original(...args);
      };
    },
  });
}

function spawnStateWriter(dataRoot, enabled) {
  const script = 'const runtime=require(process.argv[1]);process.exitCode=runtime.writeState(process.argv[2],process.argv[3]==="true")?0:2';
  return childProcess.spawn(process.execPath, ['-e', script, runtimePath, dataRoot, String(enabled)], {
    env: childEnv(),
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  });
}

test('canonical policy files are bounded strict UTF-8 regular files', () => {
  readPolicy('Engineering');
  readPolicy('Guidance');
});

test('policies preserve their separate contracts and required exceptions', () => {
  const engineering = readPolicy('Engineering');
  const guidance = readPolicy('Guidance');

  for (const required of [
    /execution flow/i,
    /existing project code[\s\S]*standard library[\s\S]*native platform[\s\S]*already-installed dependency[\s\S]*minimum new implementation/i,
    /root cause/i,
    /trust-boundary validation/i,
    /data-loss prevention/i,
    /accessibility/i,
    /smallest runnable check/i,
    /analysis, explanation, reporting, or review/i,
  ]) assert.match(engineering, required);

  for (const required of [
    /result, conclusion, or user action first/i,
    /numbered, bounded steps only/i,
    /separate tangent/i,
    /current phase[\s\S]*observed verification[\s\S]*remaining failures/i,
    /next action only when work remains/i,
    /explicit output formats/i,
    /every material finding/i,
    /never report a check as passing unless it was run and observed/i,
    /Confirm before a destructive effect/i,
    /blocking ambiguity/i,
    /repeated attempts fail/i,
  ]) assert.match(guidance, required);
});

test('policies exclude deprecated framing and rigid output machinery', () => {
  const policies = `${readPolicy('Engineering')}\n${readPolicy('Guidance')}`;
  for (const forbidden of [
    /\bADHD\b/i,
    /\bdiagnos(?:is|e|ed|ing)\b/i,
    /\btreatment\b/i,
    /\bdopamine\b/i,
    /\befficacy\b/i,
    /\b(?:lite|full|ultra)\s+(?:mode|tier|intensity)\b/i,
    /\bthree[- ]line\b/i,
    /\bcode[- ]first\b/i,
    /\b(?:maximum|max)\s+\d+\s+(?:items|bullets|steps)\b/i,
  ]) assert.doesNotMatch(policies, forbidden);
  assert.doesNotMatch(policies, /^---\s*$/m, 'canonical policies need no frontmatter or sentinel');
});

test('canonical Main and Subagent composition is exact and deduplicated', (t) => {
  const engineering = readPolicy('Engineering').trim();
  const guidance = readPolicy('Guidance').trim();
  const main = `${engineering}\n\n${guidance}\n`;
  const subagent = `${engineering}\n`;

  assert.equal(main, `${engineering}\n\n${guidance}\n`);
  assert.equal(subagent, `${engineering}\n`);
  assert.equal(occurrences(main, engineering), 1);
  assert.equal(occurrences(main, guidance), 1);
  assert.equal(occurrences(subagent, engineering), 1);
  assert.equal(occurrences(subagent, guidance), 0);

  for (const [name, text] of Object.entries({ Engineering: engineering, Guidance: guidance, Main: main, Subagent: subagent })) {
    t.diagnostic(`${name}: ${Buffer.byteLength(text, 'utf8')} UTF-8 bytes, ${[...text].length} code points`);
  }
});

test('strict input accepts one object and BOM, then rejects malformed values and bytes', () => {
  const object = { hook_event_name: 'UserPromptSubmit', prompt: 'hello' };
  const json = Buffer.from(JSON.stringify(object));
  assert.deepEqual(runtime.decodeInput(json), object);
  assert.deepEqual(runtime.decodeInput(Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), json])), object);
  for (const invalid of [
    Buffer.alloc(0),
    Buffer.from('{'),
    Buffer.from('null'),
    Buffer.from('[]'),
    Buffer.from('1'),
    Buffer.from([0xc3, 0x28]),
  ]) assert.equal(runtime.decodeInput(invalid), null);
});

test('strict input enforces the 1 MiB raw boundary including BOM', () => {
  const prefix = '{"hook_event_name":"UserPromptSubmit","prompt":"';
  const suffix = '"}';
  const exact = Buffer.from(prefix + 'x'.repeat(runtime.MAX_BYTES - prefix.length - suffix.length) + suffix);
  assert.equal(exact.length, runtime.MAX_BYTES);
  assert.ok(runtime.decodeInput(exact));
  assert.equal(runtime.decodeInput(Buffer.concat([exact, Buffer.from(' ')])), null);
});

test('event parser validates only supported event-specific fields', () => {
  assert.ok(runtime.parseEvent({ hook_event_name: 'SessionStart', source: 'startup' }));
  assert.ok(runtime.parseEvent({ hook_event_name: 'SubagentStart' }));
  assert.ok(runtime.parseEvent({ hook_event_name: 'UserPromptSubmit', prompt: '' }));
  for (const invalid of [
    {},
    { hook_event_name: 'Unknown' },
    { hook_event_name: 'SessionStart' },
    { hook_event_name: 'SessionStart', source: 1 },
    { hook_event_name: 'UserPromptSubmit' },
    { hook_event_name: 'UserPromptSubmit', prompt: null },
  ]) assert.equal(runtime.parseEvent(invalid), null);
});

test('native Codex roots take precedence and invalid native roots never fall back', (t) => {
  const plugin = makePlugin(t);
  assert.deepEqual(runtime.resolveHostRoots(claudeEnv(plugin)), {
    host: 'claude', pluginRoot: plugin.pluginRoot, dataRoot: plugin.dataRoot,
  });
  assert.deepEqual(runtime.resolveHostRoots(codexEnv(plugin)), {
    host: 'codex', pluginRoot: plugin.pluginRoot, dataRoot: plugin.dataRoot,
  });
  assert.equal(runtime.resolveHostRoots({
    ...claudeEnv(plugin), PLUGIN_ROOT: '', PLUGIN_DATA: plugin.dataRoot,
  }), null);
  assert.equal(runtime.resolveHostRoots({ CLAUDE_PLUGIN_ROOT: plugin.pluginRoot }), null);
  assert.equal(runtime.resolveHostRoots({}), null);
});

test('fixed policy loading composes Main all-or-nothing and Subagent Engineering only', (t) => {
  const plugin = makePlugin(t);
  const main = runtime.dispatch(
    { hook_event_name: 'SessionStart', source: 'startup' },
    { env: claudeEnv(plugin) },
  );
  assert.deepEqual(main, {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: `${plugin.engineering}\n\n${plugin.guidance}\n`,
    },
  });

  fs.writeFileSync(path.join(plugin.pluginRoot, 'policies', 'guidance.md'), Buffer.from([0xc3, 0x28]));
  const invalidMain = runtime.dispatch(
    { hook_event_name: 'SessionStart', source: 'clear' },
    { env: claudeEnv(plugin) },
  );
  assert.equal(invalidMain.hookSpecificOutput, undefined);
  assert.equal(typeof invalidMain.systemMessage, 'string');

  const subagent = runtime.dispatch(
    { hook_event_name: 'SubagentStart' },
    { env: claudeEnv(plugin) },
  );
  assert.equal(subagent.hookSpecificOutput.hookEventName, 'SubagentStart');
  assert.equal(subagent.hookSpecificOutput.additionalContext, `${plugin.engineering}\n`);
  assert.doesNotMatch(subagent.hookSpecificOutput.additionalContext, /Guidance fixture/);
});

test('policy loader rejects oversized, empty, linked, and non-regular sources', (t) => {
  const oversized = makePlugin(t);
  fs.writeFileSync(path.join(oversized.pluginRoot, 'policies', 'engineering.md'), Buffer.alloc(runtime.MAX_BYTES + 1, 0x61));
  assert.equal(runtime.loadPolicies(oversized.pluginRoot, false), null);

  const empty = makePlugin(t, { engineering: '  \r\n' });
  assert.equal(runtime.loadPolicies(empty.pluginRoot, false), null);

  const directory = makePlugin(t, { engineering: null });
  fs.mkdirSync(path.join(directory.pluginRoot, 'policies', 'engineering.md'));
  assert.equal(runtime.loadPolicies(directory.pluginRoot, false), null);

  const linked = makePlugin(t, { engineering: null });
  const target = path.join(linked.base, 'linked policy directory');
  fs.mkdirSync(target);
  fs.symlinkSync(target, path.join(linked.pluginRoot, 'policies', 'engineering.md'), 'junction');
  assert.equal(runtime.loadPolicies(linked.pluginRoot, false), null);
});

test('Claude and Codex SessionStart source allowlists remain host-specific', (t) => {
  const plugin = makePlugin(t);
  for (const source of ['startup', 'clear', 'resume', 'compact', 'fork']) {
    const result = runtime.dispatch({ hook_event_name: 'SessionStart', source }, { env: claudeEnv(plugin) });
    assert.equal(result.hookSpecificOutput.hookEventName, 'SessionStart');
  }
  for (const source of ['startup', 'clear', 'resume', 'compact']) {
    const result = runtime.dispatch({ hook_event_name: 'SessionStart', source }, { env: codexEnv(plugin) });
    assert.equal(result.hookSpecificOutput.hookEventName, 'SessionStart');
  }
  for (const source of ['fork', 'unknown']) {
    const result = runtime.dispatch({ hook_event_name: 'SessionStart', source }, { env: codexEnv(plugin) });
    assert.equal(result.hookSpecificOutput, undefined);
    assert.equal(typeof result.systemMessage, 'string');
  }
});

test('ordinary prompts are a zero-output no-op even when LeanClarity is unavailable', () => {
  assert.equal(runtime.dispatch({
    hook_event_name: 'UserPromptSubmit',
    prompt: 'ordinary prompt',
    transcript_path: 'ignored',
    session_id: 'ignored',
  }, { env: {} }), null);
});

test('emit writes one event-correct JSON object and fixed messages are bounded', () => {
  const writes = [];
  runtime.emit({ hookSpecificOutput: { hookEventName: 'SubagentStart', additionalContext: 'x\n' } }, {
    write(value) { writes.push(value); },
  });
  assert.equal(writes.length, 1);
  assert.equal(JSON.parse(writes[0]).hookSpecificOutput.hookEventName, 'SubagentStart');
  for (const message of Object.values(runtime.MESSAGES)) assert.ok(Buffer.byteLength(message, 'utf8') <= 512);
});

test('production entrypoint emits only one parseable JSON object for valid input', (t) => {
  const plugin = makePlugin(t);
  const result = runHook(JSON.stringify({ hook_event_name: 'SessionStart', source: 'startup' }), claudeEnv(plugin));
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '');
  const output = JSON.parse(result.stdout);
  assert.equal(output.hookSpecificOutput.hookEventName, 'SessionStart');
  assert.equal(output.hookSpecificOutput.additionalContext, `${plugin.engineering}\n\n${plugin.guidance}\n`);
  assert.equal(result.stdout.trim().split(/\r?\n/).length, 1);
});

test('production entrypoint fails open without unstructured stdout', () => {
  for (const input of ['', '{', 'null', Buffer.from([0xc3, 0x28])]) {
    const result = runHook(input, {});
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout, '');
    assert.equal(result.stderr, '');
  }
});

test('production entrypoint stops incomplete no-EOF input at the process deadline', { timeout: 3500 }, async (t) => {
  const plugin = makePlugin(t);
  const child = childProcess.spawn(process.execPath, [runtimePath], {
    env: childEnv(claudeEnv(plugin)),
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });
  let stdout = '';
  let stderr = '';
  child.stdout.setEncoding('utf8').on('data', (chunk) => { stdout += chunk; });
  child.stderr.setEncoding('utf8').on('data', (chunk) => { stderr += chunk; });
  child.stdin.on('error', () => {});
  const started = Date.now();
  child.stdin.write(JSON.stringify({ hook_event_name: 'SessionStart', source: 'startup' }));
  const outcome = await waitForExit(child, 2500);
  assert.ok(outcome, 'hook process exceeded its bounded deadline');
  assert.equal(outcome.code, 0);
  assert.equal(stdout, '');
  assert.equal(stderr, '');
  const elapsed = Date.now() - started;
  assert.ok(elapsed < 2200, `deadline took ${elapsed} ms`);
  t.diagnostic(`no-EOF process exited after ${elapsed} ms`);
});

test('import is side-effect free and does not start process I/O or a timer', { timeout: 2000 }, async () => {
  const child = childProcess.spawn(process.execPath, ['-e', 'require(process.argv[1])', runtimePath], {
    env: childEnv(),
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });
  child.stdin.on('error', () => {});
  const outcome = await waitForExit(child, 750);
  assert.ok(outcome, 'import kept the process alive');
  assert.equal(outcome.code, 0);
});

test('command parser accepts only the three normalized bare prompts', () => {
  for (const [prompt, expected] of [
    ['leanclarity', 'leanclarity'],
    ['  LEANCLARITY\r\n', 'leanclarity'],
    ['LeanClarity On', 'leanclarity on'],
    ['\tleanclarity OFF  ', 'leanclarity off'],
  ]) assert.equal(runtime.parseCommand(prompt), expected);

  for (const prompt of [
    '/leanclarity',
    'leanclarity status',
    'leanclarity on.',
    'leanclarity off now',
    'leanclarity\non',
    'please run leanclarity off',
    'leanclarity\u200bon',
    'ⅼeanclarity',
    '',
    '   ',
  ]) assert.equal(runtime.parseCommand(prompt), null, prompt);
  assert.equal(runtime.parseCommand(null), null);
});

test('absent state is default ON without a write, and deletion resets OFF to ON', (t) => {
  const plugin = makePlugin(t);
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'absent', enabled: true });
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), []);

  assert.equal(runtime.writeState(plugin.dataRoot, false), true);
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'valid', enabled: false });
  fs.unlinkSync(runtime.statePath(plugin.dataRoot));
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'absent', enabled: true });
});

test('state parser accepts exactly one boolean enabled key and rejects corrupt values', (t) => {
  const plugin = makePlugin(t);
  const file = runtime.statePath(plugin.dataRoot);
  for (const [text, enabled] of [
    ['{"enabled":true}', true],
    ['\r\n { "enabled" : false } \n', false],
  ]) {
    fs.writeFileSync(file, text);
    assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'valid', enabled });
  }

  for (const value of [
    '',
    '{',
    'null',
    '[]',
    '1',
    '{}',
    '{"enabled":1}',
    '{"enabled":true,"extra":1}',
    '{"extra":true}',
  ]) {
    fs.writeFileSync(file, value);
    assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'corrupt' }, value);
  }
  fs.writeFileSync(file, Buffer.from([0xc3, 0x28]));
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'corrupt' });
  fs.writeFileSync(file, Buffer.alloc(runtime.MAX_BYTES + 1, 0x20));
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'corrupt' });
});

test('a missing data-root directory is absent state that only a write creates', (t) => {
  const missing = makePlugin(t);
  fs.rmdirSync(missing.dataRoot);
  assert.deepEqual(runtime.readState(missing.dataRoot), { kind: 'absent', enabled: true });
  const main = runtime.dispatch({ hook_event_name: 'SessionStart', source: 'startup' }, { env: claudeEnv(missing) });
  assert.equal(main.hookSpecificOutput.hookEventName, 'SessionStart');
  assert.equal(runtime.dispatch({ hook_event_name: 'UserPromptSubmit', prompt: 'leanclarity' }, { env: claudeEnv(missing) }).reason, runtime.MESSAGES.statusOn);
  assert.equal(fs.existsSync(missing.dataRoot), false, 'reads must not create the data directory');

  assert.equal(runtime.writeState(missing.dataRoot, false), true);
  assert.equal(fs.statSync(missing.dataRoot).isDirectory(), true);
  assert.deepEqual(fs.readdirSync(missing.dataRoot), ['state.json']);
  assert.deepEqual(runtime.readState(missing.dataRoot), { kind: 'valid', enabled: false });

  const orphan = makePlugin(t);
  const deep = path.join(orphan.base, 'missing parent', 'plugin data');
  assert.deepEqual(runtime.readState(deep), { kind: 'absent', enabled: true });
  assert.equal(fs.existsSync(path.dirname(deep)), false, 'reads never create any level');
  assert.equal(runtime.dispatch({ hook_event_name: 'SessionStart', source: 'startup' }, { env: claudeEnv({ ...orphan, dataRoot: deep }) }).hookSpecificOutput.hookEventName, 'SessionStart');
  assert.equal(fs.existsSync(path.dirname(deep)), false, 'a lifecycle read never creates any level');

  assert.equal(runtime.writeState(deep, true), true);
  assert.equal(fs.statSync(deep).isDirectory(), true, 'a write creates the whole host-provided path');
  assert.deepEqual(runtime.readState(deep), { kind: 'valid', enabled: true });
  assert.equal(fs.existsSync(path.join(orphan.base, 'missing parent')), true);
  assert.deepEqual(fs.readdirSync(orphan.base).sort(), ['missing parent', 'plugin data', 'plugin root'].sort(),
    'nothing is created outside the host-provided data-root path');
});

test('unavailable data roots and non-regular state targets are never repaired', (t) => {
  const file = makePlugin(t);
  fs.rmdirSync(file.dataRoot);
  fs.writeFileSync(file.dataRoot, '');
  assert.deepEqual(runtime.readState(file.dataRoot), { kind: 'unavailable' });
  assert.equal(runtime.writeState(file.dataRoot, true), false);
  assert.equal(fs.lstatSync(file.dataRoot).isFile(), true);

  const directory = makePlugin(t);
  fs.mkdirSync(runtime.statePath(directory.dataRoot));
  assert.deepEqual(runtime.readState(directory.dataRoot), { kind: 'unavailable' });
  assert.equal(runtime.writeState(directory.dataRoot, false), false);
  assert.equal(fs.lstatSync(runtime.statePath(directory.dataRoot)).isDirectory(), true);

  const linked = makePlugin(t);
  const target = path.join(linked.base, 'state target directory');
  fs.mkdirSync(target);
  fs.symlinkSync(target, runtime.statePath(linked.dataRoot), 'junction');
  assert.deepEqual(runtime.readState(linked.dataRoot), { kind: 'unavailable' });
  assert.equal(runtime.writeState(linked.dataRoot, true), false);
  assert.equal(fs.lstatSync(runtime.statePath(linked.dataRoot)).isSymbolicLink(), true);

  const rooted = makePlugin(t);
  fs.rmdirSync(rooted.dataRoot);
  const hostTarget = path.join(rooted.base, 'host data target');
  fs.mkdirSync(hostTarget);
  fs.symlinkSync(hostTarget, rooted.dataRoot, 'junction');
  assert.deepEqual(runtime.readState(rooted.dataRoot), { kind: 'absent', enabled: true });
  assert.equal(runtime.writeState(rooted.dataRoot, false), true);
  assert.deepEqual(runtime.readState(hostTarget), { kind: 'valid', enabled: false });
});

test('unreadable state I/O is unavailable and exact commands do not replace it', (t) => {
  const plugin = makePlugin(t);
  const file = runtime.statePath(plugin.dataRoot);
  fs.writeFileSync(file, '{"enabled":false}\n');
  const unreadable = () => failOnce('openSync', (candidate, flags) => (
    candidate === file && (flags & fs.constants.O_WRONLY) === 0
  ));
  assert.deepEqual(runtime.readState(plugin.dataRoot, unreadable()), { kind: 'unavailable' });
  assert.equal(runtime.writeState(plugin.dataRoot, true, { io: unreadable() }), false);
  assert.equal(fs.readFileSync(file, 'utf8'), '{"enabled":false}\n');
});

test('atomic state writes replace existing values and repair readable corruption', (t) => {
  const plugin = makePlugin(t);
  const file = runtime.statePath(plugin.dataRoot);
  fs.writeFileSync(file, '{broken');
  assert.equal(runtime.writeState(plugin.dataRoot, true), true);
  assert.equal(fs.readFileSync(file, 'utf8'), '{"enabled":true}\n');
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'valid', enabled: true });

  assert.equal(runtime.writeState(plugin.dataRoot, false), true);
  assert.equal(fs.readFileSync(file, 'utf8'), '{"enabled":false}\n');
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), ['state.json']);
});

test('every pre-replace failure preserves the old target and cleans its owned temp', async (t) => {
  const cases = [
    ['temp create', () => failOnce('openSync', (_file, flags) => (flags & fs.constants.O_EXCL) !== 0)],
    ['write', () => failOnce('writeSync')],
    ['sync', () => failOnce('fsyncSync')],
    ['close', () => {
      let closes = 0;
      return failOnce('closeSync', () => ++closes === 2);
    }],
    ['rename', () => failOnce('renameSync')],
  ];

  for (const [name, makeIo] of cases) {
    await t.test(name, (subtest) => {
      const plugin = makePlugin(subtest);
      const file = runtime.statePath(plugin.dataRoot);
      const before = '{"enabled":false}\n';
      fs.writeFileSync(file, before);
      assert.equal(runtime.writeState(plugin.dataRoot, true, { io: makeIo() }), false);
      assert.equal(fs.readFileSync(file, 'utf8'), before);
      assert.deepEqual(fs.readdirSync(plugin.dataRoot), ['state.json']);
    });
  }
});

test('readback failure reports failure without rollback claims or orphan temp files', (t) => {
  const plugin = makePlugin(t);
  const file = runtime.statePath(plugin.dataRoot);
  fs.writeFileSync(file, '{"enabled":false}\n');
  let targetStats = 0;
  const io = failOnce('lstatSync', (candidate) => candidate === file && ++targetStats === 3);
  assert.equal(runtime.writeState(plugin.dataRoot, true, { io }), false);
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'valid', enabled: true });
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), ['state.json']);
});

test('opposing concurrent writers leave one complete valid state and only claim verified readback', { timeout: 4000 }, async (t) => {
  const plugin = makePlugin(t);
  fs.writeFileSync(runtime.statePath(plugin.dataRoot), '{"enabled":true}\n');
  const children = [spawnStateWriter(plugin.dataRoot, true), spawnStateWriter(plugin.dataRoot, false)];
  const errors = ['', ''];
  children.forEach((child, index) => child.stderr.setEncoding('utf8').on('data', (chunk) => { errors[index] += chunk; }));
  const outcomes = await Promise.all(children.map((child) => once(child, 'exit').then(([code, signal]) => ({ code, signal }))));
  assert.ok(outcomes.every(({ code }) => code === 0 || code === 2), JSON.stringify({ outcomes, errors }));
  assert.ok(outcomes.some(({ code }) => code === 0), JSON.stringify({ outcomes, errors }));
  assert.equal(runtime.readState(plugin.dataRoot).kind, 'valid');
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), ['state.json']);
  t.diagnostic(`writer exit codes: ${outcomes.map(({ code }) => code).join(', ')}`);
});

test('lifecycle hooks reread Saved setting and keep Main/Subagent policy scope exact', (t) => {
  const plugin = makePlugin(t);
  const mainEvent = { hook_event_name: 'SessionStart', source: 'startup' };
  const subagentEvent = { hook_event_name: 'SubagentStart' };
  assert.equal(runtime.dispatch(mainEvent, { env: claudeEnv(plugin) }).hookSpecificOutput.hookEventName, 'SessionStart');
  assert.equal(runtime.dispatch(subagentEvent, { env: claudeEnv(plugin) }).hookSpecificOutput.hookEventName, 'SubagentStart');

  assert.equal(runtime.writeState(plugin.dataRoot, false), true);
  assert.equal(runtime.dispatch(mainEvent, { env: claudeEnv(plugin) }), null);
  assert.equal(runtime.dispatch(subagentEvent, { env: claudeEnv(plugin) }), null);

  fs.writeFileSync(runtime.statePath(plugin.dataRoot), '{broken');
  assert.equal(typeof runtime.dispatch(mainEvent, { env: claudeEnv(plugin) }).systemMessage, 'string');
  assert.equal(typeof runtime.dispatch(subagentEvent, { env: claudeEnv(plugin) }).systemMessage, 'string');
});

test('exact commands always block and report only Saved setting boundaries', (t) => {
  const plugin = makePlugin(t);
  const env = claudeEnv(plugin);
  const command = (prompt) => runtime.dispatch({ hook_event_name: 'UserPromptSubmit', prompt }, { env });

  const initial = command('leanclarity');
  assert.equal(initial.decision, 'block');
  assert.equal(initial.reason, runtime.MESSAGES.statusOn);
  assert.doesNotMatch(initial.reason, /Current|Desired/);

  const off = command(' LEANCLARITY OFF ');
  assert.equal(off.decision, 'block');
  assert.equal(off.reason, runtime.MESSAGES.statusOff);
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'valid', enabled: false });

  const on = command('leanclarity on');
  assert.equal(on.decision, 'block');
  assert.equal(on.reason, runtime.MESSAGES.statusOn);
  assert.deepEqual(runtime.readState(plugin.dataRoot), { kind: 'valid', enabled: true });

  fs.writeFileSync(runtime.statePath(plugin.dataRoot), '{broken');
  const error = command('leanclarity');
  assert.deepEqual(error, { decision: 'block', reason: runtime.MESSAGES.commandError });
  assert.deepEqual(runtime.dispatch({ hook_event_name: 'UserPromptSubmit', prompt: 'leanclarity off' }, { env: {} }), {
    decision: 'block', reason: runtime.MESSAGES.commandError,
  });
});

test('ordinary near-match prompts remain fail-open with zero state mutation', (t) => {
  const plugin = makePlugin(t);
  const before = fs.readdirSync(plugin.dataRoot);
  for (const prompt of ['/leanclarity', 'leanclarity status', 'leanclarity on.', 'leanclarity\noff']) {
    assert.equal(runtime.dispatch({ hook_event_name: 'UserPromptSubmit', prompt }, { env: claudeEnv(plugin) }), null);
  }
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), before);
});

test('process command handling blocks recognized prompts without echo or hidden persistence', (t) => {
  const plugin = makePlugin(t);
  const input = JSON.stringify({
    hook_event_name: 'UserPromptSubmit',
    prompt: 'leanclarity off',
    session_id: 'synthetic-session-marker',
    transcript_path: 'synthetic-transcript-marker',
    cwd: 'synthetic-cwd-marker',
  });
  const result = runHook(input, claudeEnv(plugin));
  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.deepEqual(output, { decision: 'block', reason: runtime.MESSAGES.statusOff });
  const state = fs.readFileSync(runtime.statePath(plugin.dataRoot), 'utf8');
  assert.equal(state, '{"enabled":false}\n');
  assert.doesNotMatch(result.stdout + state, /synthetic-|leanclarity off/i);
});

test('failed state commands block with a fixed error and never claim success', (t) => {
  const plugin = makePlugin(t);
  const file = runtime.statePath(plugin.dataRoot);
  fs.writeFileSync(file, '{"enabled":false}\n');
  const result = runtime.dispatch(
    { hook_event_name: 'UserPromptSubmit', prompt: 'leanclarity on' },
    { env: claudeEnv(plugin), io: failOnce('renameSync') },
  );
  assert.deepEqual(result, { decision: 'block', reason: runtime.MESSAGES.commandError });
  assert.equal(fs.readFileSync(file, 'utf8'), '{"enabled":false}\n');
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), ['state.json']);
});

test('Claude and Codex manifests contain matching minimal identity metadata', () => {
  const claude = JSON.parse(fs.readFileSync(path.join(root, '.claude-plugin', 'plugin.json'), 'utf8'));
  const codex = JSON.parse(fs.readFileSync(path.join(root, '.codex-plugin', 'plugin.json'), 'utf8'));
  for (const field of ['name', 'version', 'description', 'license']) assert.equal(claude[field], codex[field]);
  assert.equal(claude.name, 'leanclarity');
  assert.equal(claude.displayName, 'LeanClarity');
  assert.equal(claude.version, '1.0.2');
  assert.equal(claude.license, 'MIT');
  assert.deepEqual(claude.author, { name: 'LeanClarity contributors' });
  assert.deepEqual(codex.author, claude.author);
  assert.deepEqual(Object.keys(codex).sort(), ['author', 'description', 'license', 'name', 'version']);
  assert.equal('hooks' in claude || 'hooks' in codex, false);
});

test('shared hook map registers exactly three synchronous handlers on one CJS path', () => {
  const map = JSON.parse(fs.readFileSync(path.join(root, 'hooks', 'hooks.json'), 'utf8'));
  assert.deepEqual(Object.keys(map), ['hooks']);
  assert.deepEqual(Object.keys(map.hooks).sort(), ['SessionStart', 'SubagentStart', 'UserPromptSubmit']);
  const handlers = Object.values(map.hooks).map((groups) => {
    assert.equal(groups.length, 1);
    assert.deepEqual(Object.keys(groups[0]), ['hooks']);
    assert.equal(groups[0].hooks.length, 1);
    return groups[0].hooks[0];
  });
  assert.equal(new Set(handlers.map(({ command }) => command)).size, 1);
  for (const handler of handlers) assert.deepEqual(handler, {
    type: 'command',
    command: 'node "${CLAUDE_PLUGIN_ROOT}/hooks/leanclarity.cjs"',
    timeout: 5,
  });
  assert.equal(fs.existsSync(runtimePath), true);
});

test('operator documentation matches commands, state, lifecycle, failures, and support scope', () => {
  const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');
  for (const required of [
    /model-interpreted guidance/i,
    /leanclarity\nleanclarity on\nleanclarity off/,
    /trim\(\)[\s\S]*toLowerCase\(\)/,
    /defaults to `ON` when `state\.json` is absent/i,
    /Deleting that host's state resets[\s\S]*ON/i,
    /clean Main boundary/i,
    /inherited boundaries/i,
    /newly started subagent/i,
    /ordinary prompt remains fail-open/i,
    /Main policy injection is all-or-nothing/i,
    /no network, telemetry/i,
    /Windows 11 x64/i,
    /portable-by-design but not release-validated/i,
    /does not detect, migrate, disable, or delete LeanCue, Ponytail, or i-have-adhd/i,
  ]) assert.match(readme, required);
  assert.doesNotMatch(readme, /HOST INTEGRATION GO\s*=\s*GO|RELEASE GO\s*=\s*GO|COMPLETE GO\s*=\s*GO/i);
  assert.doesNotMatch(readme, /function dispatch|require\(['"]node:fs/);
});

test('MIT license and both complete pinned upstream notices are present', () => {
  const license = fs.readFileSync(path.join(root, 'LICENSE'), 'utf8');
  const notices = fs.readFileSync(path.join(root, 'THIRD_PARTY_NOTICES.md'), 'utf8');
  assert.match(license, /^MIT License/);
  assert.match(license, /Copyright \(c\) 2026 LeanClarity contributors/);
  for (const required of [
    'https://github.com/DietrichGebert/ponytail',
    '2ed6c52c9d7e5e56942508591085fd45dea277d3',
    'Copyright (c) 2026 DietrichGebert',
    'policies/engineering.md',
    'https://github.com/ayghri/i-have-adhd',
    'cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c',
    'Copyright (c) 2026 Ayoub Ghriss',
    'policies/guidance.md',
  ]) assert.ok(notices.includes(required), required);
  assert.equal(occurrences(notices, 'Permission is hereby granted, free of charge'), 2);
  assert.equal(occurrences(notices, 'THE SOFTWARE IS PROVIDED "AS IS"'), 2);
  assert.doesNotMatch(notices, /function dispatch|require\(['"]node:fs/);
});

test('package surface contains no speculative dependency or integration artifacts', () => {
  for (const forbidden of [
    'package.json',
    'node_modules',
    'skills',
    '.mcp.json',
    '.app.json',
    'install.js',
    'statusline.json',
  ]) assert.equal(fs.existsSync(path.join(root, forbidden)), false, forbidden);
});

test('candidate distribution is the exact declared regular-file byte set', (t) => {
  const actual = [
    ...walkFiles('.claude-plugin'),
    ...walkFiles('.codex-plugin'),
    ...walkFiles('hooks'),
    ...walkFiles('policies'),
    'README.md',
    'LICENSE',
    'THIRD_PARTY_NOTICES.md',
  ].sort().filter((relative) => !Object.values(localCatalogs).includes(relative));
  assert.deepEqual(actual, [...candidateFiles].sort());
  for (const relative of actual) {
    const stat = fs.lstatSync(path.join(root, relative));
    assert.equal(stat.isFile(), true, relative);
    assert.equal(stat.isSymbolicLink(), false, relative);
  }

  const identity = candidateIdentity();
  for (const entry of identity.entries) t.diagnostic(`${entry.path}\t${entry.bytes}\t${entry.sha256}`);
  t.diagnostic(`Candidate SHA-256: ${identity.sha256}`);
});

test('marketplace catalogs name only the candidate plugin and stay out of the distribution', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, '.claude-plugin', 'plugin.json'), 'utf8'));

  const claude = JSON.parse(fs.readFileSync(path.join(root, localCatalogs.claude), 'utf8'));
  assert.equal(claude.name, 'leanclarity');
  assert.deepEqual(claude.plugins.map(({ name, source, description }) => ({ name, source, description })), [
    { name: manifest.name, source: './', description: manifest.description },
  ]);
  assert.equal('$schema' in claude, false, 'catalog must not reference an unresolvable schema URL');

  const codex = JSON.parse(fs.readFileSync(path.join(root, localCatalogs.codex), 'utf8'));
  assert.equal(codex.name, 'leanclarity');
  assert.deepEqual(codex.plugins.map(({ name, source, policy }) => ({ name, source, policy })), [{
    name: manifest.name,
    source: { source: 'url', url: repositoryUrl, ref: 'main' },
    policy: { installation: 'AVAILABLE', authentication: 'ON_INSTALL' },
  }]);

  for (const relative of Object.values(localCatalogs)) assert.equal(candidateFiles.includes(relative), false, relative);
});

test('production runtime contains no prohibited execution, egress, persistence, or fallback surface', () => {
  const source = fs.readFileSync(runtimePath, 'utf8');
  for (const forbidden of [
    /child_process/,
    /\beval\s*\(/,
    /\bFunction\s*\(/,
    /\bimport\s*\(/,
    /require\(['"]node:(?:http|https|net|tls|dgram|dns|sqlite)/,
    /\bfetch\s*\(/,
    /\bWebSocket\b/,
    /\b(?:database|telemetry|analytics|registry)\b/i,
    /\b(?:transcript|session_id)\b/i,
    /process\.cwd\s*\(/,
    /os\.homedir\s*\(/,
  ]) assert.doesNotMatch(source, forbidden);
  assert.deepEqual([...source.matchAll(/require\(['"](node:[^'"]+)/g)].map((match) => match[1]).sort(), [
    'node:fs',
    'node:path',
    'node:util',
  ]);
});

test('state commands mutate only host plugin data and never the plugin root', (t) => {
  const plugin = makePlugin(t);
  const before = walkDirectory(plugin.pluginRoot);
  const result = runtime.dispatch(
    { hook_event_name: 'UserPromptSubmit', prompt: 'leanclarity off' },
    { env: claudeEnv(plugin) },
  );
  assert.equal(result.reason, runtime.MESSAGES.statusOff);
  assert.deepEqual(walkDirectory(plugin.pluginRoot), before);
  assert.deepEqual(fs.readdirSync(plugin.dataRoot), ['state.json']);
});

test('candidate JSON parses and LeanClarity local Markdown links resolve', () => {
  for (const relative of ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'hooks/hooks.json']) {
    assert.doesNotThrow(() => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8')), relative);
  }

  for (const relative of [
    'README.md',
    'INSTALL.md',
    'THIRD_PARTY_NOTICES.md',
    'policies/engineering.md',
    'policies/guidance.md',
    'docs/specs/LeanClarity_v1.0_SPEC.md',
    'docs/plans/LeanClarity_v1.0_PLAN.md',
    'docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md',
  ]) {
    const source = fs.readFileSync(path.join(root, relative), 'utf8');
    for (const match of source.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
      const target = match[1].split('#', 1)[0];
      if (!target || /^[a-z]+:/i.test(target)) continue;
      assert.equal(fs.existsSync(path.resolve(root, path.dirname(relative), target)), true, `${relative} -> ${target}`);
    }
  }
});

test('BOM counts inside the 1 MiB limit and a second BOM is invalid', () => {
  const bom = Buffer.from([0xef, 0xbb, 0xbf]);
  const prefix = '{"hook_event_name":"UserPromptSubmit","prompt":"';
  const suffix = '"}';
  const json = Buffer.from(prefix + 'x'.repeat(runtime.MAX_BYTES - bom.length - prefix.length - suffix.length) + suffix);
  const exact = Buffer.concat([bom, json]);
  assert.equal(exact.length, runtime.MAX_BYTES);
  assert.ok(runtime.decodeInput(exact));
  assert.equal(runtime.decodeInput(Buffer.concat([bom, bom, Buffer.from('{}')])), null);
});

test('production entrypoint rejects 1 MiB plus one byte before dispatch', () => {
  const prefix = '{"hook_event_name":"UserPromptSubmit","prompt":"';
  const suffix = '"}';
  const oversized = Buffer.from(prefix + 'x'.repeat(runtime.MAX_BYTES + 1 - prefix.length - suffix.length) + suffix);
  const result = runHook(oversized, {});
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr, '');
});

test('partial no-EOF input also terminates without output at the process deadline', { timeout: 3500 }, async (t) => {
  const child = childProcess.spawn(process.execPath, [runtimePath], {
    env: childEnv(),
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });
  let stdout = '';
  let stderr = '';
  child.stdout.setEncoding('utf8').on('data', (chunk) => { stdout += chunk; });
  child.stderr.setEncoding('utf8').on('data', (chunk) => { stderr += chunk; });
  child.stdin.on('error', () => {});
  const started = Date.now();
  child.stdin.write('{"hook_event_name":"SessionStart"');
  const outcome = await waitForExit(child, 2500);
  assert.ok(outcome, 'partial hook process exceeded its bounded deadline');
  assert.equal(outcome.code, 0);
  assert.equal(stdout, '');
  assert.equal(stderr, '');
  const elapsed = Date.now() - started;
  assert.ok(elapsed < 2200, `deadline took ${elapsed} ms`);
  t.diagnostic(`partial no-EOF process exited after ${elapsed} ms`);
});

test('GO evidence matches the frozen candidate and keeps downstream gates unclaimed', () => {
  const evidence = fs.readFileSync(path.join(root, 'docs', 'evidence', 'LeanClarity_v1.0_GO_EVIDENCE.md'), 'utf8');
  const identity = candidateIdentity();
  assert.ok(evidence.includes(identity.sha256));
  for (const entry of identity.entries) {
    assert.ok(evidence.includes(`| \`${entry.path}\` | ${entry.bytes} | \`${entry.sha256}\` |`), entry.path);
  }

  const requirementSection = evidence.slice(
    evidence.indexOf('## Requirement results'),
    evidence.indexOf('## Deterministic local results'),
  );
  const rows = [...requirementSection.matchAll(/^\| `((?:LCL)-[A-Z]+-[0-9]{3})` \|.*\| (PASS|FAIL|BLOCKED|NOT RUN|HOLD|N\/A) \|/gm)];
  assert.equal(rows.length, 24);
  assert.equal(new Set(rows.map((match) => match[1])).size, 24);
  assert.equal(rows.filter((match) => match[2] === 'PASS').length, 22);
  assert.equal(rows.filter((match) => match[2] === 'NOT RUN').length, 2);
  assert.match(evidence, /IMPLEMENTATION GO: `GO`/);
  assert.match(evidence, /HOST INTEGRATION GO: `NOT VERIFIED`/);
  assert.match(evidence, /RELEASE GO: `NOT VERIFIED`/);
  assert.match(evidence, /COMPLETE GO: `NOT GRANTED`/);
  assert.doesNotMatch(evidence, /HOST INTEGRATION GO: `GO`|RELEASE GO: `GO`|COMPLETE GO: `GO`/);
});
