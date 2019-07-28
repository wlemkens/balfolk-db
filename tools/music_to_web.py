import urllib.request
import json
import sys
import requests

from tools.common import *


def send_mp3_to_web(track, username, password):
    data = {"username":username,"password":password}
    host = "localhost"
    url = "http://"+host+"/db/interface/add_mp3_to_db.php"
    file = read_for_db(track["filename"])
    files = {"track": ("tmp.mp3", file)}
    response = requests.post(url, data = data, files=files)
    print (str(response.content).replace("\\n","\n"))
    # print (str(response.content))
    print("ok")

def send_samples(track, username, password, key, sample_count, id, sample_length):
    data = {"username":username,"password":password, "key" : key, "id" : id}
    host = "localhost"
    url = "http://"+host+"/db/interface/add_sample_to_db.php"
    for i in range(sample_count):
        sample = get_random_part(track["filename"], sample_length)
        sample.export("tmp.mp3",format="mp3")
        file = read_for_db("tmp.mp3")
        files = {"sample": ("tmp.mp3", file)}
        response = requests.post(url, data = data, files=files)

def send_json_to_web(track, username, password):
    dances = None
    for dance in track["dances"]:
        if dances:
            dances += ", "+dance["name"]
        else:
            dances = dance["name"]
    print("Sending data for '{:}' by '{:}' ({:})".format(track["title"], track["band"]["name"], dances))
    data = {"username":username,"password":password, "track":track}
    host = "balfolk-db.be"
    host = "localhost"
    url = "http://"+host+"/db/interface/add_json_to_db.php"
    response = requests.post(url, json = data)
    reply_parts = str(response.content)[2:-1].split(" ");
    samples_needed = int(reply_parts[1])
    track_key = reply_parts[0]
    id = reply_parts[2]
    if samples_needed > 0:
        send_samples(track, username, password, track_key, samples_needed, id, 20)

def extract_info_from_collection(directory, username, password):
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
                track_json = track.json()
                send_json_to_web(track_json,username, password)

    print ("Found {:} dances".format(len(db)))
    return db


if __name__ == "__main__":
    db = extract_info_from_collection(sys.argv[1], sys.argv[2], sys.argv[3])
