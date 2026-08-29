"""Delete stale records from the store.

This is the destructive path. Everything that reaches disk goes through
purge_records, so the guards live here rather than in each caller.
"""

from app import store


class PurgeRefused(Exception):
    """Raised instead of deleting when a guard is not satisfied."""


def select_stale(records, older_than_days, now=None):
    """Records whose age exceeds the cutoff."""
    return [r for r in records if store.age_days(r, now) > older_than_days]


def purge_records(path, older_than_days, dry_run=True, allow_full=False, now=None):
    """Delete records older than the cutoff.

    Returns the list of records that were (or would be) removed.

    Guards, in order:

    1. A cutoff of zero or less matches every record ever written. That is
       almost always a caller bug rather than an intent to wipe the store, so
       it is refused rather than executed.
    2. dry_run defaults to True. A caller that forgets the argument gets a
       preview, never a deletion.
    3. Deleting the entire store is a different operation from expiring stale
       rows. It needs allow_full, so it cannot happen by accident when the
       cutoff is merely older than every record present.
    """
    if older_than_days is None or older_than_days <= 0:
        raise PurgeRefused(
            "cutoff must be a positive number of days; "
            f"{older_than_days!r} would match every record"
        )

    records = store.load(path)
    doomed = select_stale(records, older_than_days, now)

    if records and len(doomed) == len(records) and not allow_full:
        raise PurgeRefused(
            f"cutoff would delete all {len(records)} records; "
            "pass allow_full=True to confirm a full wipe"
        )

    if dry_run:
        return doomed

    keep = [r for r in records if r not in doomed]
    store.save(path, keep)
    return doomed
