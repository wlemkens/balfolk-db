# TODO

Issues found while debugging the 2026-08-09 synchronization failures, left unfixed on
purpose. Nothing here is blocking; each entry says why it was skipped.

## Server (`../server/balfolkdb/www`, not under version control)

- **`Album::updateByName` leaves the object without an id** — `data_structure/Track.php:840`.
  Same shape as the `Band` bug fixed on 2026-08-09: `hasSimilar()` proves a row exists,
  `updateByName()` returns true without loading its id. `tracks.albumid` is nullable, so
  instead of crashing the track is just saved with no album. Fix is the same one line
  (`$this->tryToLoad()`), but it changes what gets written, so it wants a deliberate test.

- **`Dance::updateByName` has the same shape and *can* crash** — `data_structure/Track.php:957`.
  `tracks_dances.danceid` is NOT NULL, so an id-less dance would fail the way the band did.
  Not fixed because `Dance` keys off `nameid` rather than `id` and the semantics were not
  verified. Reproduce with a genre tag that fuzzy-matches an existing dance but is not an
  exact hit.

- **Band matching merges too eagerly** — `hasSimilar()`/`tryToLoad()` in
  `data_structure/Track.php:605-690` use a 0.7 fulltext tolerance. During testing
  `Zzq Testband Secundum` was silently absorbed into `Zzq Testband Novum`. Pre-existing;
  the band fix only made it visible instead of fatal. Decide whether the tolerance is right
  before deleting anything by band name.

- **`loadFromQuery` binds before storing** — `data_structure/Track.php:194, 621, 752`.
  `bind_result()` is called before `store_result()`. It works today; the documented order is
  the other way round and the current one is fragile.

- **Throttling fails open** — `interface/mbid.php:73-77`. When the lock file cannot be
  opened, `musicbrainzThrottle()` returns silently and the MusicBrainz rate limit stops
  being enforced for every caller. This also makes `tests/test_mbid.php:29` fail under
  `docker exec`, where `/tmp/musicbrainz_last_call` is owned by www-data.

- **Sample uploads are never checked** — `interface/add_sample_to_db.php` replies are
  discarded by the client (see below), so a rejected sample looks like a success.

## Client (`tools/`)

- **`send_samples` ignores the response** — `music_to_web.py:35-58`. Every other endpoint
  call checks what came back; this one does not, so a failed sample upload is invisible.

- **Reply parsing is positional and brittle** — `music_to_web.py:85`. The endpoint's answer
  is parsed with `str(response.content)[2:-1].split(" ")` and validated only by
  "three parts, second is a digit". Any stray output from php shifts it. Returning JSON from
  `add_json_to_db.php` and parsing that would remove the whole class of problem.

- **`extract_info_from_collection` calls `extract_info_from_file` with one argument** —
  `music_to_web.py:118`, but the function has taken three since the dance list was added.
  Only reachable through the `__main__` CLI at the bottom of the file, and the surrounding
  `except` hides it. The same handler prints the literal `"Error : {:}"` — the format call
  is missing (`music_to_web.py:121`).

- **The worker thread touches Tk directly** — `music_wizard.py:344, 360, 376`.
  `uploadTracks`/`downloadTracks` call `app.setLabel` from the sync thread while every meter
  update around them goes through `app.queueFunction`. It has not misbehaved, but the
  inconsistency is the kind that bites under load.

- **Bare `except:` hides real failures** — `common.py:300` (and `385`). Any error reading a
  file becomes `Failed to load file '<path>'` on stdout with no reason and no log line.
  A 41907 file scan returned no track for 90 of them, and there is no way to tell which
  were genuinely untagged and which hit an error.

- **Regex is not a raw string** — `common.py:163`. `re.compile("\(.*\)")` raises a
  `SyntaxWarning` on every run. One character: make it `r"\(.*\)"`.

- **The log only grows** — `music_wizard.py:407`. `~/music_wizard.log` is opened in append
  mode at `DEBUG`, which includes one urllib3 line per HTTP request. Roughly 3 lines per
  track per run. Fine so far; revisit if a support log ever arrives too big to read.

## Housekeeping

- **Test data in the dev database.** User `wiztest` (id 72, password `wiztest123`) plus
  40 tracks, 24 bands, 32 albums and 4 samples added by it. Tracks 11876 (`Testwals`,
  attributed to Naragonia) and 11881 (`Secundum Wals`) are synthetic; the rest came from
  `~/Music/balfolk-source-data`. Delete by id, not by name, because of the fuzzy band
  merging above.

- **Confirm who deployed to production.** `track_details_by_mbid.php` on balfolk-db.eu
  started answering with the fixed `{"status":...}` shape partway through 2026-08-09,
  which was not done from this machine.
