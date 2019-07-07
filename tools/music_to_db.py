import os
import sys
import mutagen
from mutagen.id3 import ID3

from Music.Music import *

def parse_dance(dance):
    return dance[0].replace("Folk ", "")

def extract_v1(file):
    artist = None
    if "artist" in file.keys():
        artist = file["artist"][0]
    if "albumartist" in file.keys():
        artist = file["albumartist"][0]
    if artist and "genre" in file.keys():
        band = Band(artist)
        language = Language("Nederlands")
        genre = None
        if "genre" in file.keys():
            genre = parse_dance(file["genre"])
        dance = Dance(language, genre)
        year = None
        if "year" in file:
            year = file["year"][0]
        elif "date" in file:
            year = file["date"][0]
        album = None
        if "album" in file.keys():
            album = Album(band, file["album"][0], year)
        track = Track(album, file["tracknumber"][0], file["title"][0], [dance])
        if "cddb-id" in file.keys():
            album.cddb_id = file["cddb-id"][0]
        return track
    return None

def hasTags(file, tags):
    for tag in tags:
        if not tag in file.keys():
            return False
    return True

def extract_v2(file):
    # band, track
    required_tags = ["TPE1", "TIT2"]
    #print(file)
    if hasTags(file, required_tags):
        artist = file["TPE1"].text
        band = Band(artist)
        language = Language("Nederlands")
        genre = None
        if "TCON" in file.keys():
            genre = parse_dance(file["TCON"].text)
        dance = Dance(language, genre)
        year = None
        if "TDRC" in file:
            year = file["TDRC"].text
        album = None
        if "TALB" in file.keys():
            album = Album(band, file["TALB"].text, year)
        track_nb = None
        if "TRCK" in file:
            track_nb = file["TRCK"].text
        track = Track(album, track_nb, file["TIT2"].text, [dance])
        if "cddb-id" in file:
            album.cddb_id = file["cddb-id"]
        return track
    return None

def extract_info_from_file(path):
    if (os.path.splitext(path)[1] in [".mp3",".flac"]):
        file = mutagen.File(path)

        if file:
            if "artist" in file.keys():
                return extract_v1(file)
            else:
                return extract_v2(file)

    return None

def extract_info_from_collection(directory):
    db = []
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            track = extract_info_from_file(os.path.join(dirName, fname))
            if track:
                db += [track]
    return db

def export_to_db(db):
    print ("Found {:} dances".format(len(db)))

if __name__ == "__main__":
    db = extract_info_from_collection(sys.argv[1])
    export_to_db(db)