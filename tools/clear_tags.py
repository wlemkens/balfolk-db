import os
import sys

import mysql.connector

from tools.common import *
from mutagen.id3 import ID3, TCON

def update_file(filename):
    track = extract_info_from_file(filename)
    if track:
        print("Clearing '{:}'".format(track.title))

        file = mutagen.File(filename)
        if "genre" in file.keys():
            file["genre"] = []
            file.save()
        else:
            file = ID3(filename)
            file.delall("TCON")
            file.save()


def process_collection(directory):
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            track = update_file(os.path.join(dirName, fname))
            if track:
                db += [track]


if __name__ == "__main__":
    process_collection(sys.argv[1])