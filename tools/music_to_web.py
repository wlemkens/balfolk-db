import sys
import requests

from tools.common import *

"""
Program for sending data from a music collection to the online database
"""

def send_mp3_to_web(track, username, password, language):
    """
    Send an mp3 with ID3 data completely to the server where it will be processed
    :param track:       The track to be send
    :param username:    Username to log in on the server
    :param password:    Password to log in on the server
    :return:
    """
    # File might be too large
    data = {"username" : username, "password" : password, "language" : language}
    host = "localhost"
    url = "http://"+host+"/db/interface/add_mp3_to_db.php"
    file = read_for_db(track["filename"])
    files = {"track": ("tmp.mp3", file)}
    response = requests.post(url, data = data, files = files)
    print (str(response.content).replace("\\n","\n"))
    print("ok")


def send_samples(track, username, password, key, sample_count, id, sample_length):
    """
    Send some samples from the audio file to the server
    :param track:       Track to send the samples of
    :param username:    Username to log in on the server
    :param password:    Password to log in on the server
    :param key:         Key needed to be able to send the samples, comes from the server when the metadata was send
    :param sample_count: How many samples need to be send
    :param id:          The id of the track the samples are for. Comes from the server
    :param sample_length: How long the samples should be
    :return:
    """
    data = {"username":username,"password":password, "key" : key, "id" : id}
    host = "balfolk-db.be"
    url = "http://"+host+"/db/interface/add_sample_to_db.php"
    for i in range(sample_count):
        sample = get_random_part(track["filename"], sample_length)
        sample.export("tmp.mp3",format="mp3")
        file = read_for_db("tmp.mp3")
        files = {"sample": ("tmp.mp3", file)}
        response = requests.post(url, data = data, files=files)

def send_json_to_web(track, username, password, language):
    """
    Send metadata from a track to the server
    :param track:       Track to send the metadata of
    :param username:    Username to log in on the server
    :param password:    Password to log in on the server
    :param language:    Language the dances are in
    :return:
    """
    dances = None
    for dance in track["dances"]:
        if dances:
            dances += ", "+dance["name"]
        else:
            dances = dance["name"]
    print("Sending data for '{:}' by '{:}' ({:})".format(track["title"], track["band"]["name"], dances))
    data = {"username" : username, "password" : password, "track" : track, "language" : language}
    host = "balfolk-db.be"
    url = "http://"+host+"/db/interface/add_json_to_db.php"
    response = requests.post(url, json = data)
    reply_parts = str(response.content)[2:-1].split(" ");
    samples_needed = int(reply_parts[1])
    track_key = reply_parts[0]
    id = reply_parts[2]
    if samples_needed > 0:
        send_samples(track, username, password, track_key, samples_needed, id, 20)

def extract_info_from_collection(directory, language, username, password):
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
                send_json_to_web(track_json,username, password, language)

    print ("Found {:} dances".format(len(db)))
    return db

def printUsage(argv):
    print("Usage: {:} <collection-path> <genre-language> <username> <password>".format(argv[0]))
    print("    In which <genre-language> is defined in the database")
    print("    Most likely supported: Nederlands, Dutch, Néerlandais")
    print("                           Français, French, Frans")
    print("                           English, Engels, Englais")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        printUsage(sys.argv)
        exit(0)
    db = extract_info_from_collection(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
