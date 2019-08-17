"""
This program gets the info from the online database and replaces the ID3 genre tags from the given database with the
online genres
"""

import sys
import requests

from tools.common import *
from mutagen.id3 import ID3, TCON, TBPM

def find_dances_online(track, language):
    """
    Query the online database and add the found dances to the track data
    :param track:   Track to look up the dances for
    :param language:  Language to get the dance names in
    :return:        If the track is found in the database
    """
    print("Querying for '{:}' by '{:}'".format(track.title, track.band.name))
    data = {"track":track.json(), "language":language}
    host = "balfolk-db.be"
    host = "localhost"
    url = "http://"+host+"/db/interface/query_db.php"
    response = requests.post(url, json = data)
    print (str(response.content).replace("\\n","\n"))

    track.dances = []
    if len(str(response.content))>3:
        found = int(str(response.content)[2:3])
        parts = str(response.content)[3:-1].split(";")
        dances = parts[:-1];
        if (parts[-1]):
            track.bpm = int(parts[-1])
        for dance_str in dances:
            dance = Dance(None, dance_str)
            track.dances += [dance]
        return found
    return False

def update_file(filename, language, clear_genre):
    """
    Update the audio file with the new found dances (in the genre field)
    :param filename:    The filename of the audio file
    :param language:  Language to get the dance names in
    :param clear_genre: If we need to clear the genre in the file if no data is found
    :return: track, found, dances_found:
                    track: The track with data from the file and dances from the database
                    found: If the track was known by the online database
                    dances_found: If any dance data was found for the track
    """
    found = False
    dances_found = False
    track = extract_info_from_file(filename)
    if track:
        found = find_dances_online(track, language)
        if len(track.dances) > 0:
            dances_found = True
            dances_str = track.dances[0].name
            for i in range(1, len(track.dances)):
                dances_str += ", "+track.dances[i].name

            print("Found '{:} by {:}' : '{:}'".format(track.title, track.band.name, dances_str))

            file = mutagen.File(filename)
            if "genre" in file.keys():
                file["genre"] = []
                for dance in track.dances:
                    if "genre" in file.keys():
                        file["genre"] += [dance.name]
                    else:
                        file["genre"] = [dance.name]
                if track.bpm > 0:
                    file["bpm"] = track.bpm
                file.save()
            else:
                file = ID3(filename)
                file.delall("TCON")
                for dance in track.dances:
                    file.add(TCON(encoding=3, text=dance.name))
                if track.bpm > 0:
                    file.delall("TBPM")
                    file.add(TBPM(track.bpm))

            file.save()
        else:
            if clear_genre:
                # We might want to purge unknown genres
                file = mutagen.File(filename)
                if "genre" in file.keys():
                    file["genre"] = []
                    file.save()
                else:
                    file = ID3(filename)
                    file.delall("TCON")
                    file.save()
            print("No data found for {:} by {:}".format(track.title, track.band.name))
    return track, found, dances_found


def process_collection(directory, language, purge):
    """
    Process the collection found under the given directory. All subdirectories are processed too.
    :param directory: Directory to process
    :param language:  Language to get the dance names in
    :param purge:     Clear the genre field if no dance data is found
    :return:
    """
    updated_data_list = []
    unknown_data_list = []
    missing_data_list = []
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            track, found, dances_found = update_file(os.path.join(dirName, fname), language, purge)
            if found:
                if dances_found:
                    updated_data_list += [track]
                else:
                    unknown_data_list += [track]
            else:
                missing_data_list += [track]
    print("Found {:} matches with dance data, {:} without dance data, and {:} tracks were unknown to the database".format(len(updated_data_list), len(unknown_data_list), len(missing_data_list)))

def printUsage(argv):
    print("Usage: {:} <collection-path> <genre-language> [purge]".format(argv[0]))
    print("    In which <genre-language> is defined in the database")
    print("    Most likely supported: Nederlands, Dutch, Néerlandais")
    print("                           Français, French, Frans")
    print("                           English, Engels, Englais")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        printUsage(sys.argv)
        exit(0)
    purge = len(sys.argv) > 3 and sys.argv[3] == "purge"
    process_collection(sys.argv[1], sys.argv[2], purge)