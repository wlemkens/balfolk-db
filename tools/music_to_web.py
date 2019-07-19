import urllib.request
import json
import sys
import requests

from tools.common import *


def send_to_web(track, username, password):
    data = {'track': track, "username":username,"password":password}
    url = "http://balfolk-db.be/db/add_to_db.php"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(url, headers=headers,json=data)
    print (response.content)


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
            track = extract_info_from_file(os.path.join(dirName, fname))
            if track:
                track_json = track.json()
                send_to_web(track_json,"wim","test")

    print ("Found {:} dances".format(len(db)))
    return db


if __name__ == "__main__":
    db = extract_info_from_collection(sys.argv[1])
