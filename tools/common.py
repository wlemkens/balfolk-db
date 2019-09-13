import os
import mysql.connector
import mutagen
from pydub import AudioSegment
import random
import json

from Music.Music import *
from mutagen.id3 import ID3, TCON, TBPM
import requests

global supportedExtensions
supportedExtensions = [".mp3", ".flac"]

global host
host = "balfolk-db.eu"
# host = "localhost"

def find_dances(track, db):
    '''
    Check if a track already exists in the database, allowing for some misspellings
    :param track: Track to check
    :param db:
    :return: True if the track already exists, the id of the Track will be set to the first found similar entry
             False if no similar track could be found
    '''
    cursor = db.cursor()
    sql = "SELECT * FROM tracks WHERE levenshtein(title, %s) <= %s"
    val = (track.title, len(track.title)*0.2)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    track.dances = []
    if len(result) > 0:
        languageid = 1
        track.id = result[0][0]
        sql = "SELECT name, MIN(nameid) FROM dances AS d INNER JOIN tracks_dances AS td ON d.id = td.danceid WHERE td.trackid = %s AND d.languageid = %s"
        val = (track.id, languageid)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        for res in result:
            if res[0]:
                # Might return None, so only add if there is an actual entry
                track.dances += [Dance(languageid ,res[0])]
        return True
    return False


def find_id(track, db):
    '''
    Check if a track already exists in the database, allowing for some misspellings
    :param track: Track to check
    :param db:
    :return: True if the track already exists, the id of the Track will be set to the first found similar entry
             False if no similar track could be found
    '''
    cursor = db.cursor()
    sql = "SELECT * FROM tracks WHERE levenshtein(title, %s) <= %s"
    val = (track.title, len(track.title)*0.2)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    if len(result) > 0:
        track.id = result[0][0]
        return True
    return False

# def find_dances(track, db):
#     '''
#     Check if a track already exists in the database, allowing for some misspellings
#     :param track: Track to check
#     :param db:
#     :return: True if the track already exists, the id of the Track will be set to the first found similar entry
#              False if no similar track could be found
#     '''
#     cursor = db.cursor()
#     sql = "SELECT danceid FROM tracks_dances WHERE trackid = %s"
#     val = (track.id, )
#     cursor.execute(sql, val)
#     result = cursor.fetchall()
#     if len(result) > 0:
#         track.id = result[0][0]
#         return True
#     return False

def login_to_db():
    '''
    Try to login to the database using the credentials found in login.db
    :return: the dabase connection
    '''
    login = None
    password = None
    url = None
    with open("login.db") as f:
        i = 0
        for line in f:
            if i == 0:
                url = line.replace("\n","")
            if i == 1:
                login = line.replace("\n","")
            if i == 2:
                password = line.replace("\n","")
            if i == 3:
                database = line.replace("\n","")
            i += 1
    db = None
    if password:
        db = mysql.connector.connect(host = url, password = password, user = login, database = database)
        print("Logged in to {:}".format(url))
    else:
        print("No database login data")
    return db

def parse_dance(dance):
    '''
    Try to sanitize the dances
    :param dance:   The string to be sanitized
    :return:        The sanitized string
    '''

    # My genre tags contain "Folk" in front of the dance
    return dance[0].replace("Folk", "").strip()

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

def extract_v1(file, filename):
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
        language = Language("Nederlands")
        dance = None
        if "genre" in file.keys():
            genre = parse_dance(file["genre"])
            if genre:
                dance = Dance(language, genre)
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
        track = Track(album, track_nb, file["title"][0], [dance], band, filename, bpm)
        return track
    return None

def hasTags(file, tags):
    for tag in tags:
        if not tag in file.keys():
            return False
    return True

def extract_v2(file, filename):
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
        language = Language("Nederlands")
        dance = None
        if "TCON" in file.keys():
            genre = parse_dance(file["TCON"].text)
            if genre:
                dance = Dance(language, genre)
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
        if "TRCK" in file:
            track_nb = file["TRCK"].text[0]
        track = Track(album, track_nb, file["TIT2"].text[0], [dance], band, filename, bpm)
        return track
    return None

def read_for_db(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
        return binaryData

def extract_info_from_file(path):
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
                return extract_v1(file, path)
            else:
                return extract_v2(file, path)

    return None

def get_random_part(track, part_length):
    sound = AudioSegment.from_file(track)
    start = 0
    end = len(sound) - part_length * 1000
    part_start = random.randrange(start, end)
    part_end = part_start + part_length * 1000
    return sound[part_start:part_end]

def getFileList(directory):
    global supportedExtensions
    filenameList = []
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            ext = os.path.splitext(fname)
            if (ext[1] in supportedExtensions):
                filename = os.path.join(dirName, fname)
                filenameList += [filename]
    return filenameList

def getTraks(fileList):
    tracks = []
    for filename in fileList:
        track = extract_info_from_file(filename)
        if track:
            tracks += [track]
    return tracks;

def clearFile(filename):
    # We might want to purge unknown genres
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
    url = "http://"+host+"/db/interface/query_db.php"
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

