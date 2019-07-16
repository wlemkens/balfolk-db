import os
import sys

import mysql.connector

from tools.common import *
from mutagen.id3 import ID3, TCON

def update_file(filename, db, clear_genre):
    track = extract_info_from_file(filename)
    if track:
        find_dances(track, db)
        if len(track.dances) > 0:
            dances_str = track.dances[0].name
            for i in range(1, len(track.dances)):
                dances_str += ", "+track.dances[i].name

            print("Found '{:}' : '{:}'".format(track.title, dances_str))

            file = mutagen.File(filename)
            if "genre" in file.keys():
                file["genre"] = []
                for dance in track.dances:
                    if "genre" in file.keys():
                        file["genre"] += [dance.name]
                    else:
                        file["genre"] = [dance.name]
                file.save()
            else:
                file = ID3(filename)
                file.delall("TCON")
                for dance in track.dances:
                    file.add(TCON(encoding=3, text=dance.name))
                file.save()
        elif clear_genre:
            # We might want to purge unknown genres
            file = mutagen.File(filename)
            if "genre" in file.keys():
                file["genre"] = []
                file.save()
            else:
                file = ID3(filename)
                file.delall("TCON")
                file.save()


def process_collection(directory, purge):
    db = login_to_db()
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            track = update_file(os.path.join(dirName, fname), db, purge)
            if track:
                db += [track]


if __name__ == "__main__":
    purge = len(sys.argv) > 2 and sys.argv[2] == "purge"
    process_collection(sys.argv[1], purge)