import sys

from tools.common import *
import tempfile

"""
Program for sending data from a music collection to the online database
"""
# global host
# host = "https://balfolk-db.eu"
# host = "http://balfolkdb-test"


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
    global host
    # host = "localhost"
    url = host+"/db/interface/add_mp3_to_db.php"
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
    global host
    data = {"username":username,"password":password, "key" : key, "id" : id}
    url = host+"/db/interface/add_sample_to_db.php"
    tmpFilename = os.path.join(tempfile.gettempdir(), "tmp.mp3")
    for i in range(sample_count):
        sample = get_random_part(track["filename"], sample_length)
        if sample:
            sample.export(tmpFilename,format="mp3")
            file = read_for_db(tmpFilename)
            files = {"sample": ("tmp.mp3", file)}
            response = requests.post(url, data = data, files=files)
            os.unlink(tmpFilename)

def send_json_to_web(track, username, password, language):
    """
    Send metadata from a track to the server
    :param track:       Track to send the metadata of
    :param username:    Username to log in on the server
    :param password:    Password to log in on the server
    :param language:    Language the dances are in
    :return:
    """
    global host
    dances = None
    for dance in track["dances"]:
        if dances:
            dances += ", "+dance["name"]
        else:
            dances = dance["name"]
    album = ""
    if "name" in track["album"]:
        album = track["album"]["name"]
    print("Sending data for '{:}' by '{:}' on '{:}' ({:})".format(track["title"], track["band"]["name"], album, dances))
    data = {"username" : username, "password" : password, "track" : track, "language" : language}
    url = host+"/db/interface/add_json_to_db.php"
    headers = {'Content-type': 'application/json', 'charset':'UTF-8'}
    response = requests.post(url, json = data, headers = headers)
    print (str(response.content).replace("\\n","\n"))
    reply_parts = str(response.content)[2:-1].split(" ");
    if reply_parts[1].isdigit():
        samples_needed = int(reply_parts[1])
        track_key = reply_parts[0]
        id = reply_parts[2]
        if id == 0:
            return "Failed to submit track '{:}' from band '{:}' on album '{:}'".format(track["title"], track["band"]["name"], album)
        if samples_needed > 0:
            send_samples(track, username, password, track_key, samples_needed, id, 20)
    else:
        return str(response.content)
    return None

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
            try:
                track = extract_info_from_file(filename)
                if track:
                    track_json = track.json()
                    send_json_to_web(track_json,username, password, language)
            except Exception as e:
                print("Error : {:}")

    print ("Found {:} dances".format(len(db)))
    return db

def printUsage(argv):
    print("Usage: {:} <collection-path> <genre-language> <username> <password>".format(argv[0]))
    print("    In which <genre-language> is defined in the database")
    print("    Most likely supported: Nederlands, Dutch, Néerlandais")
    print("                           Français, French, Frans")
    print("                           English, Engels, Englais")
    print("This application will send the ID3 meta data to the server and will also send some")
    print("samples of music not yet known to the server to allow the determination of the dance.")
    print("No complete audio track will be stored on the server.")

def checkAuth(username, password):
    data = {"username" : username, "password" : password}
    url = host+"/db/interface/check_auth.php"
    # url = host+"/interface/check_auth.php"
    headers = {'Content-type': 'application/json', 'charset':'UTF-8'}
    response = requests.post(url, json = data, headers = headers)
    print (str(response.content).replace("\\n","\n"))
    return int(response.content)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        printUsage(sys.argv)
        exit(0)
    db = extract_info_from_collection(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
