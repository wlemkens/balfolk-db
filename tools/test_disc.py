from tools.common import disc_number
from Music.Music import Track, Band

def test_disc_number():
    assert disc_number("2") == 2
    assert disc_number("2/2") == 2
    assert disc_number("0") is None
    assert disc_number("") is None
    assert disc_number("disc two") is None

def test_disc_in_json():
    track = Track(None, 3, "Wals", [], Band("Naragonia"), "x.flac", -1)
    assert track.json()["disc"] is None
    track.disc = 2
    assert track.json()["disc"] == 2

if __name__ == "__main__":
    test_disc_number()
    test_disc_in_json()
    print("ok")
