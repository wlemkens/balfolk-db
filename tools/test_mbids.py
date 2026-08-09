"""Self-check for MusicBrainz id reading and lookup routing.
Run: venv/bin/python -m tools.test_mbids"""
from Music.Music import Band, Track
from tools import common


class _FakeFile:
    def __init__(self, tags):
        self.tags = tags


class _FakeResponse:
    def __init__(self, payload):
        self.text = common.json.dumps(payload)

    def json(self):
        return common.json.loads(self.text)


def _track(mbid=None):
    track = Track(None, 1, "Scottish", [], Band("Naragonia"), "f.mp3", -1)
    track.mbid = mbid
    return track


def _lookup_calls(track, mb_hit, db_replies):
    """Run find_dances_online with the network stubbed out, return the urls it hit"""
    urls = []

    def fake_post(url, **kwargs):
        urls.append(url)
        return _FakeResponse(db_replies.pop(0))

    common.musicbrainz_lookup = lambda title, artist: mb_hit
    common.post_with_retries = fake_post
    common.find_dances_online(track, "Nederlands")
    return urls


def _run():
    common.mutagen.File = lambda path, easy=False: _FakeFile({
        "musicbrainz_trackid": ["rec-1"],
        "musicbrainz_albumid": ["rel-1"],
        "musicbrainz_artistid": ["art-1"],
        "title": ["irrelevant"],
    })
    assert common.read_mbids("x.mp3") == {"mbid": "rec-1", "album_mbid": "rel-1",
                                          "artist_mbid": "art-1"}

    # untagged file -> empty dict, so json() keeps None everywhere
    common.mutagen.File = lambda path, easy=False: _FakeFile({})
    assert common.read_mbids("x.mp3") == {}

    # unreadable file -> empty dict, never a crash
    def boom(path, easy=False):
        raise IOError("nope")
    common.mutagen.File = boom
    assert common.read_mbids("x.mp3") == {}

    # search hit above the score threshold is used, a weak one is not
    common.requests.get = lambda url, **kw: _FakeResponse({"recordings": [{"id": "rec-9", "score": 95}]})
    assert common.musicbrainz_lookup("Scottish", "Naragonia") == "rec-9"
    common.requests.get = lambda url, **kw: _FakeResponse({"recordings": [{"id": "rec-9", "score": 40}]})
    assert common.musicbrainz_lookup("Scottish", "Naragonia") is None
    common.requests.get = lambda url, **kw: _FakeResponse({})
    assert common.musicbrainz_lookup("Scottish", "Naragonia") is None

    # tagged file: matched by mbid, name query never used
    hit = {"status": 1, "dances": ["Scottish"], "bpm": 100}
    miss = {"status": 0}
    urls = _lookup_calls(_track("rec-1"), None, [hit])
    assert urls == [common.host + "/interface/track_details_by_mbid.php"], urls

    # untagged file with a MusicBrainz match: same mbid path, id kept for the upload
    track = _track()
    urls = _lookup_calls(track, "rec-2", [hit])
    assert urls == [common.host + "/interface/track_details_by_mbid.php"], urls
    assert track.mbid == "rec-2"
    assert [d.name for d in track.dances] == ["Scottish"] and track.bpm == 100

    # no mbid anywhere: old name based path
    urls = _lookup_calls(_track(), None, [hit])
    assert urls == [common.host + "/interface/query_db.php"], urls

    # mbid unknown to the server: falls through to the old path
    urls = _lookup_calls(_track("rec-3"), None, [miss, hit])
    assert urls == [common.host + "/interface/track_details_by_mbid.php",
                    common.host + "/interface/query_db.php"], urls

    print("mbid reading and lookup routing: all checks passed")


if __name__ == "__main__":
    _run()
