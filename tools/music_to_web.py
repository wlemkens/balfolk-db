import urllib.request
import json
import sys
import requests

from tools.common import *


def send_to_web(track, username, password):
    data = {"username":username,"password":password, **track}
    url = "http://balfolk-db.be/db/interface/add_to_db.php"
    headers = {'Content-type': 'application/octet-stream'}
    file = read_for_db("tmp.mp3")
    files = {"image": ("tmp.mp3", file)}
    response = requests.post(url, data = data, files=files)
    print (response.content)
    print("ok")


def extract_info_from_collection(directory):
    '''
    Extract the info from all music found in the given directory and underlying subdirectories
    :param directory: The root of the library path
    :return:          A list with all the found Tracks
    '''
    db = []
    print("Extracting ID3 info")
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            filename = os.path.join(dirName, fname)
            track = extract_info_from_file(filename)
            if track:
                track_json = track.flat_json()
                send_to_web(track_json,"wim","test")

    print ("Found {:} dances".format(len(db)))
    return db


if __name__ == "__main__":
    db = extract_info_from_collection(sys.argv[1])
