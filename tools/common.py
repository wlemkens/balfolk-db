import os
import mutagen
from pydub import AudioSegment
import random
import json

from Music.Music import *
from mutagen.id3 import ID3, TCON, TBPM
import requests
import re

global supportedExtensions
supportedExtensions = [".mp3", ".flac"]

global host
host = "https://balfolk-db.eu"
# host = "http://balfolkdb-test"

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def parse_dance(danceList):
    '''
    Try to sanitize the dances
    :param dance:   The string to be sanitized
    :return:        The sanitized string
    '''

    # My genre tags contain "Folk" in front of the dance
    result = []
    for subDanceList in danceList:
        dances = subDanceList.split(";")
        for dance in dances:
            result += [lreplace("Folk ", "", dance).strip()]
    return result

def getYear(date):
    '''
    Convert the different ways we can get the date into a integer containing the year
    Currently supports:
    - year string
    - yyyy-mm-dd string
    - dd-mm-yyyy string
    - mutagen ID3Timestamp
    :param date: The date to be converted
    :return:     The year as integer
    '''
    if isinstance(date,mutagen.id3.ID3TimeStamp):
        return date.year
    if len(date) > 4:
        parts = date.split("-")
        if len(parts[0]) == 4:
            return int(parts[0])
        else:
            return int(parts[2])
    return int(date)

def parse_title_dance(title, dances, language):
    p = re.compile("\(.*\)")
    m = p.search(title)
    if m:
        dance = m.group()[1:-1].lower()
        if dance in dances:
            return [Dance(language, dance)]
    return []

def extract_v1(file, filename, dance_list, lang):
    '''
    Extract the music info from one of the two formats we can get the tags
    :param file: The opened mutagen file to analyse
    :param filename: The filename of the file to be analysed
    :return:     A Track with the ID3 info or None if not information was available
    '''
    artist = None
    albumartist = None
    if "artist" in file.keys():
        artist = file["artist"][0]
    if "albumartist" in file.keys():
        albumartist = file["albumartist"][0]
    if artist or albumartist:
        band = Band(artist)
        albumband = None
        if albumartist:
            albumband = Band(albumartist)
        language = Language(lang)
        dances = []
        if "genre" in file.keys():
            genres = parse_dance(file["genre"])
            for genre in genres:
                dances += [Dance(language, genre)]
        if len(dances) == 0:
            dances = parse_title_dance(file["title"][0], dance_list, language)
        bpm = -1
        if "bpm" in file.keys():
            bpm = file["bpm"]
        year = None
        if "year" in file:
            year = getYear(file["year"][0])
        elif "date" in file:
            year = getYear(file["date"][0])
        album = None
        if "album" in file.keys():
            total_tracks = -1
            if "totaltracks" in file.keys():
                total_tracks = file["totaltracks"][0]
            album = Album(albumband, file["album"][0], year, total_tracks)
        track_nb = -1
        if "tracknumber" in file.keys():
            track_nb = file["tracknumber"][0]
        track = Track(album, track_nb, file["title"][0], dances, band, filename, bpm)
        return track
    return None

def hasTags(file, tags):
    '''
    Returns if a audio file has all the requested tags
    :param file: The file to check the tags for
    :param tags: The tags to be checked
    :return: True if all the tags are present in the file
    '''
    for tag in tags:
        if not tag in file.keys():
            return False
    return True

def extract_v2(file, filename, dance_list, lang):
    '''
    Extract the music info from the other of the two formats we can get the tags
    :param file: The opened mutagen file to analyse
    :param filename: The filename of the file to be analysed
    :return:     A Track with the ID3 info or None if not information was available
    '''
    # band, track title
    required_tags = ["TPE1", "TIT2"]
    if hasTags(file, required_tags):
        artist = file["TPE1"].text[0]
        band = Band(artist)
        language = Language(lang)
        dances = []
        if "TCON" in file.keys():
            genres = parse_dance(file["TCON"].text)
            for genre in genres:
                dances += [Dance(language, genre)]
        if len(dances) == 0:
            dances = parse_title_dance(file["TIT2"].text[0], dance_list, language)
        bpm = -1
        if "TBPM" in file.keys():
            bpm = file["TBPM"].text[0]
        year = None
        if "TDRC" in file.keys():
            year = getYear(file["TDRC"].text[0])
        album = None
        if "TALB" in file.keys():
            total_tracks = -1
            album = Album(band, file["TALB"].text[0], year, total_tracks)
        track_nb = -1
        if "TRCK" in file.keys():
            track_nb = file["TRCK"].text[0]
        track = Track(album, track_nb, file["TIT2"].text[0], dances, band, filename, bpm)
        return track
    return None

def read_for_db(filename):
    '''
    Read a file so it can be transmitted to the database
    :param filename: The file to read
    :return:         The binary data from the file
    '''
    with open(filename, 'rb') as file:
        binaryData = file.read()
        return binaryData

def extract_info_from_file(path, dance_list, language):
    '''
    Extract the info from the mp3 or flac file
    :param path: filename
    :return:     None if not enough info was found
                 A Track containing the found info otherwise
    '''
    if (os.path.splitext(path)[1] in [".mp3",".flac"]):
        file = mutagen.File(path)

        if file:
            if "artist" in file.keys() or "albumartist" in file.keys():
                return extract_v1(file, path, dance_list, language)
            else:
                return extract_v2(file, path, dance_list, language)

    return None

def get_random_part(track, part_length):
    '''
    Get a random sample from the given track
    :param track:       The filename to get the sample from
    :param part_length: How long the sample should be
    :return:            A Audiosegment width length close to the specified length (sampling will cause a small difference)
    '''
    sound = AudioSegment.from_file(track)
    start = 0
    end = len(sound) - part_length * 1000
    part_start = random.randrange(start, end)
    part_end = part_start + part_length * 1000
    return sound[part_start:part_end]

def getFileList(directory):
    '''
    Get a list of the supported files in the given directory and underlying directories
    :param directory: Root directory to get the supported files from
    :return:          A list of paths for the supported files
    '''
    global supportedExtensions
    filenameList = []
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            ext = os.path.splitext(fname)
            if (ext[1] in supportedExtensions):
                filename = os.path.join(dirName, fname)
                filenameList += [filename]
    return filenameList

def getTracks(fileList):
    '''
    OBSOLETE IT SEEMS
    Parse all the info of the tracks
    :param fileList: A list of file names to get the info for
    :return:         A list of tracks with id3 info
    '''
    tracks = []
    dance_list = get_dance_list()
    for filename in fileList:
        track = extract_info_from_file(filename, dance_list)
        if track:
            tracks += [track]
    return tracks;

def clearFile(filename):
    '''
    Clear all the genre tags of the file
    :param filename:
    '''
    file = mutagen.File(filename)
    if "genre" in file.keys():
        file["genre"] = []
        file.save()
    else:
        file = ID3(filename)
        file.delall("TCON")
        file.save()

def update_file(filename, language, clear_genre, append_genre):
    """
    Update the audio file with the new found dances (in the genre field)
    :param filename:    The filename of the audio file
    :param language:  Language to get the dance names in
    :param clear_genre: If we need to clear the genre in the file if no data is found
    :param append_genre:If we need to append the new genre (dance) to the existing list of genres
    :return: track, found, dances_found:
                    track: The track with data from the file and dances from the database
                    found: If the track was known by the online database
                    dances_found: If any dance data was found for the track
    """
    found = False
    dances_found = False
    dance_list = get_dance_list()
    track = extract_info_from_file(filename, dance_list, language)
    if track:
        found = find_dances_online(track, language)
        if len(track.dances) > 0:
            dances_found = True
            dances_str = track.dances[0].name
            for i in range(1, len(track.dances)):
                dances_str += ", "+track.dances[i].name

            print("Found '{:} by {:}' : '{:}'".format(track.title, track.band.name, dances_str))

            file = mutagen.File(filename)
            if "title" in file.keys():
                if not append_genre:
                    file["genre"] = []
                for dance in track.dances:
                    if not "genre" in file.keys():
                        file["genre"] = [dance.name]
                    elif not dance.name in file["genre"]:
                            file["genre"] += [dance.name]
                if track.bpm > 0:
                    file["bpm"] = str(track.bpm)
                file.save()
            else:
                file = ID3(filename)
                if not append_genre:
                    file.delall("TCON")
                for dance in track.dances:
                    if not "TCON" in file.keys() or not dance in file["TCON"]:
                        file.add(TCON(encoding=3, text=dance.name))
                if track.bpm > 0:
                    file.delall("TBPM")
                    file.add(TBPM(encoding=3, text=[track.bpm]))


            file.save()
        else:
            if clear_genre:
                # We might want to purge unknown genres
                file = mutagen.File(filename)
                if "title" in file.keys():
                    file["genre"] = []
                    file.save()
                else:
                    file = ID3(filename)
                    file.delall("TCON")
                    file.save()
            print("No data found for {:} by {:}".format(track.title, track.band.name))
    return track, found, dances_found

def find_dances_online(track, language):
    """
    Query the online database and add the found dances to the track data
    :param track:   Track to look up the dances for
    :param language:  Language to get the dance names in
    :return:        If the track is found in the database
    """
    global host
    print("Querying for '{:}' by '{:}'".format(track.title, track.band.name))
    data = {"track":track.json(), "language":language}
    url = host+"/db/interface/query_db.php"
    response = requests.post(url, json = data)
    # print (str(response.content).replace("\\n","\n"))
    response_text = str(response.text)
    response_data = json.loads(response_text)

    track.dances = []
    found = response_data["status"]
    if found > 0:
        if "dances" in response_data.keys():
            dances = response_data["dances"]
            bpm = response_data["bpm"]
            if bpm > 0:
                track.bpm = bpm
            for dance_str in dances:
                dance = Dance(None, dance_str)
                track.dances += [dance]
    return found

def get_dance_list():
    url = host+"/db/interface/dances_all.php"
    response = requests.post(url)
# print (str(response.content).replace("\\n","\n"))
    response_text = str(response.text)
    response_data = json.loads(response_text)
    return [dance.lower() for dance in response_data]
