import os
import mysql.connector
import mutagen
from pydub import AudioSegment
import random

from Music.Music import *

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
    if artist and "genre" in file.keys():
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
        track = Track(album, track_nb, file["title"][0], [dance], band, filename)
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
        track = Track(album, track_nb, file["TIT2"].text[0], [dance], band, filename)
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

