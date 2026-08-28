'use strict';

const PROCESS_STARTED_AT = Date.now();
const fs = require('node:fs');
const path = require('node:path');
const { TextDecoder } = require('node:util');

const MAX_BYTES = 1024 * 1024;
const INPUT_DEADLINE_MS = 1000;
const EVENTS = new Set(['SessionStart', 'UserPromptSubmit', 'SubagentStart']);
const SOURCES = {
  claude: new Set(['startup', 'clear', 'resume', 'compact', 'fork']),
  codex: new Set(['startup', 'clear', 'resume', 'compact']),
};
const MESSAGES = Object.freeze({
  unavailable: 'LeanClarity is unavailable for this hook event.',
  commandError: 'LeanClarity saved setting is unavailable. Existing contexts were not changed.',
  statusOn: 'LeanClarity saved setting: ON. Existing contexts are not retroactively changed. New hook contexts, including newly started subagents, use the saved setting. The main conversation fully switches in a new chat or after /clear.',
  statusOff: 'LeanClarity saved setting: OFF. Existing contexts are not retroactively changed. New hook contexts, including newly started subagents, use the saved setting. The main conversation fully switches in a new chat or after /clear.',
});

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function decodeUtf8(bytes) {
  return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
}

function decodeInput(raw) {
  if (!(raw instanceof Uint8Array) || raw.byteLength > MAX_BYTES) return null;
  try {
    const value = JSON.parse(decodeUtf8(raw));
    return isObject(value) ? value : null;
  } catch {
    return null;
  }
}

function parseEvent(value) {
  if (!isObject(value) || !EVENTS.has(value.hook_event_name)) return null;
  if (value.hook_event_name === 'SessionStart' && typeof value.source !== 'string') return null;
  if (value.hook_event_name === 'UserPromptSubmit' && typeof value.prompt !== 'string') return null;
  return value;
}

function parseCommand(prompt) {
  if (typeof prompt !== 'string') return null;
  const command = prompt.trim().toLowerCase();
  return command === 'leanclarity' || command === 'leanclarity on' || command === 'leanclarity off'
    ? command
    : null;
}

function has(env, key) {
  return Object.prototype.hasOwnProperty.call(env, key);
}

function validAbsolute(value) {
  return typeof value === 'string' && value.length > 0 && path.isAbsolute(value);
}

function resolveHostRoots(env) {
  const native = has(env, 'PLUGIN_ROOT') || has(env, 'PLUGIN_DATA');
  const root = native ? env.PLUGIN_ROOT : env.CLAUDE_PLUGIN_ROOT;
  const data = native ? env.PLUGIN_DATA : env.CLAUDE_PLUGIN_DATA;
  if (!validAbsolute(root) || !validAbsolute(data)) return null;
  return { host: native ? 'codex' : 'claude', pluginRoot: root, dataRoot: data };
}

function readRegular(file, io = fs) {
  let descriptor;
  try {
    const before = io.lstatSync(file);
    if (!before.isFile() || before.isSymbolicLink()) return { kind: 'unavailable' };
    descriptor = io.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW || 0));
    const opened = io.fstatSync(descriptor);
    if (!opened.isFile() || before.dev !== opened.dev || before.ino !== opened.ino) return { kind: 'unavailable' };
    if (opened.size > MAX_BYTES) return { kind: 'oversized' };

    const raw = Buffer.allocUnsafe(MAX_BYTES + 1);
    let length = 0;
    while (length < raw.length) {
      const count = io.readSync(descriptor, raw, length, raw.length - length, null);
      if (count === 0) break;
      length += count;
    }
    return length > MAX_BYTES
      ? { kind: 'oversized' }
      : { kind: 'ok', bytes: raw.subarray(0, length) };
  } catch {
    return { kind: 'unavailable' };
  } finally {
    if (descriptor !== undefined) {
      try { io.closeSync(descriptor); } catch { /* unavailable */ }
    }
  }
}

function readPolicy(file, io = fs) {
  const result = readRegular(file, io);
  if (result.kind !== 'ok') return null;
  try {
    const text = decodeUtf8(result.bytes).trim();
    return text || null;
  } catch {
    return null;
  }
}

function loadPolicies(pluginRoot, includeGuidance, io = fs) {
  const engineering = readPolicy(path.join(pluginRoot, 'policies', 'engineering.md'), io);
  if (!engineering) return null;
  if (!includeGuidance) return { engineering };
  const guidance = readPolicy(path.join(pluginRoot, 'policies', 'guidance.md'), io);
  return guidance ? { engineering, guidance } : null;
}

function composeMain(engineering, guidance) {
  return `${engineering.trim()}\n\n${guidance.trim()}\n`;
}

function composeSubagent(engineering) {
  return `${engineering.trim()}\n`;
}

function context(eventName, additionalContext) {
  return { hookSpecificOutput: { hookEventName: eventName, additionalContext } };
}

function diagnostic() {
  return { systemMessage: MESSAGES.unavailable };
}

function statePath(dataRoot) {
  return path.join(dataRoot, 'state.json');
}

function dataRootAvailable(dataRoot, io = fs) {
  try {
    return io.statSync(dataRoot).isDirectory();
  } catch {
    return false;
  }
}

function parseState(bytes) {
  try {
    const value = JSON.parse(decodeUtf8(bytes));
    const keys = isObject(value) ? Object.keys(value) : [];
    return keys.length === 1 && keys[0] === 'enabled' && typeof value.enabled === 'boolean'
      ? { enabled: value.enabled }
      : null;
  } catch {
    return null;
  }
}

function readState(dataRoot, io = fs) {
  if (!dataRootAvailable(dataRoot, io)) return { kind: 'unavailable' };
  const file = statePath(dataRoot);
  try {
    const stat = io.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink()) return { kind: 'unavailable' };
  } catch (error) {
    return error && error.code === 'ENOENT'
      ? { kind: 'absent', enabled: true }
      : { kind: 'unavailable' };
  }

  const result = readRegular(file, io);
  if (result.kind === 'unavailable') return result;
  if (result.kind === 'oversized') return { kind: 'corrupt' };
  const state = parseState(result.bytes);
  return state ? { kind: 'valid', enabled: state.enabled } : { kind: 'corrupt' };
}

function writeState(dataRoot, enabled, { io = fs, now = Date.now, pid = process.pid } = {}) {
  if (typeof enabled !== 'boolean') return false;
  const current = readState(dataRoot, io);
  if (current.kind === 'unavailable') return false;

  const target = statePath(dataRoot);
  let temporary;
  let descriptor;
  let owned = false;
  try {
    for (let attempt = 0; attempt < 16; attempt += 1) {
      const candidate = path.join(dataRoot, `.state.json.${pid}.${now()}.${attempt}.tmp`);
      try {
        descriptor = io.openSync(candidate, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL, 0o600);
        temporary = candidate;
        owned = true;
        break;
      } catch (error) {
        if (!error || error.code !== 'EEXIST') return false;
      }
    }
    if (descriptor === undefined) return false;

    const bytes = Buffer.from(`${JSON.stringify({ enabled })}\n`, 'utf8');
    let offset = 0;
    while (offset < bytes.length) {
      const count = io.writeSync(descriptor, bytes, offset, bytes.length - offset, null);
      if (count <= 0) throw new Error('state write did not progress');
      offset += count;
    }
    io.fsyncSync(descriptor);
    io.closeSync(descriptor);
    descriptor = undefined;
    io.renameSync(temporary, target);
    owned = false;

    const saved = readState(dataRoot, io);
    return saved.kind === 'valid' && saved.enabled === enabled;
  } catch {
    return false;
  } finally {
    if (descriptor !== undefined) {
      try { io.closeSync(descriptor); } catch { /* unavailable */ }
    }
    if (owned && temporary) {
      try { io.unlinkSync(temporary); } catch { /* task-owned cleanup failed */ }
    }
  }
}

function commandResult(reason) {
  return { decision: 'block', reason };
}

function handleCommand(command, dataRoot, io = fs) {
  if (!dataRoot) return commandResult(MESSAGES.commandError);
  if (command === 'leanclarity') {
    const state = readState(dataRoot, io);
    return commandResult(state.kind === 'valid' || state.kind === 'absent'
      ? (state.enabled ? MESSAGES.statusOn : MESSAGES.statusOff)
      : MESSAGES.commandError);
  }

  const enabled = command === 'leanclarity on';
  return commandResult(writeState(dataRoot, enabled, { io })
    ? (enabled ? MESSAGES.statusOn : MESSAGES.statusOff)
    : MESSAGES.commandError);
}

function dispatch(value, { env = process.env, io = fs } = {}) {
  const event = parseEvent(value);
  if (!event) return null;

  if (event.hook_event_name === 'UserPromptSubmit') {
    const command = parseCommand(event.prompt);
    if (!command) return null;
    const roots = resolveHostRoots(env);
    return handleCommand(command, roots && roots.dataRoot, io);
  }

  const roots = resolveHostRoots(env);
  if (!roots) return diagnostic();

  if (event.hook_event_name === 'SessionStart') {
    if (!SOURCES[roots.host].has(event.source)) return diagnostic();
    const state = readState(roots.dataRoot, io);
    if (state.kind !== 'valid' && state.kind !== 'absent') return diagnostic();
    if (!state.enabled) return null;
    const policies = loadPolicies(roots.pluginRoot, true, io);
    return policies ? context('SessionStart', composeMain(policies.engineering, policies.guidance)) : diagnostic();
  }

  const state = readState(roots.dataRoot, io);
  if (state.kind !== 'valid' && state.kind !== 'absent') return diagnostic();
  if (!state.enabled) return null;
  const policies = loadPolicies(roots.pluginRoot, false, io);
  return policies ? context('SubagentStart', composeSubagent(policies.engineering)) : diagnostic();
}

function readStdin(input, { startedAt = PROCESS_STARTED_AT, now = Date.now } = {}) {
  return new Promise((resolve) => {
    const chunks = [];
    let length = 0;
    let settled = false;
    let timer;

    const finish = (result, destroy = false) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      input.removeListener('data', onData);
      input.removeListener('end', onEnd);
      input.removeListener('error', onError);
      if (typeof input.pause === 'function') input.pause();
      if (destroy && typeof input.destroy === 'function') input.destroy();
      resolve(result);
    };
    const onData = (chunk) => {
      const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
      length += bytes.length;
      if (length > MAX_BYTES) finish(null, true);
      else chunks.push(bytes);
    };
    const onEnd = () => finish(Buffer.concat(chunks, length));
    const onError = () => finish(null);

    input.on('data', onData);
    input.once('end', onEnd);
    input.once('error', onError);
    timer = setTimeout(() => finish(null, true), Math.max(0, INPUT_DEADLINE_MS - (now() - startedAt)));
    if (typeof input.resume === 'function') input.resume();
  });
}

function emit(result, output = process.stdout) {
  if (result) output.write(`${JSON.stringify(result)}\n`);
}

async function runProcess({ input = process.stdin, output = process.stdout, env = process.env, startedAt = PROCESS_STARTED_AT } = {}) {
  try {
    const raw = await readStdin(input, { startedAt });
    if (!raw) return;
    const decoded = decodeInput(raw);
    if (!decoded) return;
    emit(dispatch(decoded, { env }), output);
  } catch {
    // Hook failures are fail-open and produce no unstructured stdout.
  }
}

if (require.main === module) void runProcess();

module.exports = {
  INPUT_DEADLINE_MS,
  MAX_BYTES,
  MESSAGES,
  composeMain,
  composeSubagent,
  decodeInput,
  dispatch,
  emit,
  loadPolicies,
  parseCommand,
  parseEvent,
  readPolicy,
  readState,
  readStdin,
  resolveHostRoots,
  runProcess,
  statePath,
  writeState,
};
