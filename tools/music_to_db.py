import os
import sys
import mutagen
import mysql.connector
from pydub import AudioSegment
import random

from Music.Music import *
from tools.common import *


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
                db += [track]
    print ("Found {:} dances".format(len(db)))
    return db

def unflatten_data(flat_data):
    '''
    Convert the list of all the tracks containing dupplicate entries (ablums, bands, ...) to a tree
    with no dupplicate entries
    :param flat_data: List containing dupplicate data
    :return:          Dictionary of tracks without dupplicate data
    '''
    print("Restructuring data")
    bands = {}
    albums = {}
    languages = {}
    dances = {}
    tracks = {}
    for flat_track in flat_data:
        if flat_track.album:
            if flat_track.album.band:
                if not flat_track.album.band.name in bands.keys():
                    bands[flat_track.album.band.name] = flat_track.album.band
                else:
                    flat_track.album.band = bands[flat_track.album.band.name]
                track_id = flat_track.album.band.name+"/"+flat_track.album.name+"/"+flat_track.title
                tracks[track_id] = flat_track
            else:
                track_id = flat_track.band.name+"/"+flat_track.album.name+"/"+flat_track.title
                tracks[track_id] = flat_track

            if not flat_track.album.name in albums:
                albums[flat_track.album.name] = flat_track.album
            else:
                flat_track.album = albums[flat_track.album.name]

        else:
            track_id = flat_track.band.name+"/"+flat_track.title
            tracks[track_id] = flat_track

        for dance in flat_track.dances:
            if dance:
                if not dance.name in dances:
                    dances[dance.name] = dance
                    if dance.language:
                        if not dance.language.name in languages:
                            languages[dance.language.name] = dance.language
                        else:
                            dance.language = languages[dance.language.name]
                else:
                    dance = dances[dance.name]
    print("Found {:} valid tracks".format(len(tracks)))
    return bands, albums, languages, dances, tracks

def store_language(language, db):
    '''
    Insert the language in the database if not yet present
    :param language: Language to be added
    :param db:       database connection to store in
    language.id will be set to the new or existing id of the language entry in the database
    '''
    if not language.id:
        cursor = db.cursor()

        sql = "SELECT * FROM languages WHERE name = %s"
        val = (language.name, )
        cursor.execute(sql, val)
        result = cursor.fetchall()
        if len(result) == 0:
            sql = "INSERT INTO languages (name) VALUES (%s)"
            cursor.execute(sql, val)
            db.commit()
            language.id = cursor.lastrowid
        else:
            language.id = result[0][0]

def store_dance(dance, db):
    '''
    Insert the dance in the database if not yet present
    Update the id of the Dance to the new or existing id
    Since there is no way to automatically determine if the dance is a different name for the same dance, all dances
    are considered a new dance (danceid will be the same as the id)
    :param dance: Dance to be inserted
    :param db:       database connection to store in
    '''
    cursor = db.cursor()
    if dance and not dance.id:
        sql = "SELECT * FROM dances WHERE levenshtein(name, %s) <= %s"
        val = (dance.name, len(dance.name)*0.3)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        if len(result) == 0:
            store_language(dance.language, db)
            sql = "INSERT INTO dances (name, languageid) VALUES (%s, %s)"
            val = (dance.name, dance.language.id)
            cursor.execute(sql, val)
            db.commit()
            dance.nameid = cursor.lastrowid
            dance.id = dance.nameid
            sql = "UPDATE dances set id = %s WHERE nameid = %s"
            val = (dance.nameid, dance.nameid)
            cursor.execute(sql, val)
            db.commit()
        else:
            dance.id = result[0][0]



def update_track(track, db):
    '''
    Add the dances of an existing track to the database if they are not already registered
    :param track:   Track to add the dances from
    :param db:      database to store to
    '''
    cursor = db.cursor()

    for dance in track.dances:
        if dance:
            store_dance(dance, db)

            sql = "SELECT * FROM tracks_dances WHERE trackid = %s AND danceid = %s"
            val = (track.id, dance.id)
            cursor.execute(sql, val)
            result = cursor.fetchall()
            if len(result) == 0:
                sql = "INSERT INTO tracks_dances (trackid, danceid) VALUES (%s, %s)"
                cursor.execute(sql, val)
                db.commit()
    store_samples(track, db, 4)


def store_band(band, db):
    '''
    Insert the band in the databse if not yet present
    Updates the id of the Band to the new or existing id
    :param band: The Band to be inserted
    :param db:   database connection to store in
    '''
    if band and not band.id:
        cursor = db.cursor()
        sql = "SELECT * FROM bands WHERE levenshtein(name, %s) <= %s"
        val = (band.name, len(band.name)*0.2)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        if len(result) > 0:
            band.id = result[0][0]
        else:
            sql = "INSERT INTO bands (name, description) VALUES (%s, %s)"
            val = (band.name, "")
            cursor.execute(sql, val)
            db.commit()
            band.id = cursor.lastrowid



def store_album(album, db):
    '''
    Inserts a Album into the database if not yet present
    Updates the id to the new or existing entry
    :param album: Album to be inserted
    :param db:    database to sotre in
    '''
    if album:
        store_band(album.band, db)

        if not album.id:
            cursor = db.cursor()
            sql = "SELECT * FROM albums WHERE levenshtein(name, %s) <= %s"
            val = (album.name, len(album.name)*0.2)
            cursor.execute(sql, val)
            result = cursor.fetchall()
            if len(result) > 0:
                if not album.band or album.band.id == result[0][1]:
                    album.id = result[0][0]
            if not album.id:
                if album.band:
                    sql = "INSERT INTO albums (name, bandid, year, nb_tracks) VALUES (%s, %s, %s, %s)"
                    val = (album.name, album.band.id, album.year, album.nb_tracks)
                    cursor.execute(sql, val)
                    db.commit()
                    album.id = cursor.lastrowid
                else:
                    sql = "INSERT INTO albums (name, year, nb_tracks) VALUES (%s, %s, %s)"
                    val = (album.name, album.year, album.nb_tracks)
                    cursor.execute(sql, val)
                    db.commit()
                    album.id = cursor.lastrowid

def read_for_db(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
        return binaryData

def store_samples(track, db, nb_samples):
    cursor = db.cursor()
    sql = "SELECT * FROM samples WHERE trackid = %s"
    val = (track.id, )
    cursor.execute(sql, val)
    result = cursor.fetchall()
    to_be_added_count = nb_samples - len(result)
    for i in range(to_be_added_count):
        sample = get_random_part(track.filename, 20)
        sample.export("tmp.mp3",format="mp3")
        file_for_db = read_for_db("tmp.mp3")
        sql = "INSERT INTO samples (trackid, data) VALUES (%s, %s)"
        val = (track.id, file_for_db)
        cursor.execute(sql, val)
        db.commit()



def insert_track(track, db):
    '''
    Inserts a track into the database if it doesn't exist yet
    Updates the id to the new or existing entry
    Also inserts the album, band and dances if needed
    :param track: Track to be added
    :param db:    database to store in
    '''
    store_album(track.album, db)
    store_band(track.band, db)

    if not track.id:
        cursor = db.cursor()
        sql = "SELECT * FROM tracks WHERE levenshtein(title, %s) <= %s"
        val = (track.title, len(track.title)*0.2)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        if len(result) > 0:
            track.id = result[0][0]
        else:
            if track.album:
                sql = "INSERT INTO tracks (title, bandid, albumid, number) VALUES (%s, %s, %s, %s)"
                print ("track:",track.title, track.band.id, track.album.id, track.number)
                val = (track.title, track.band.id, track.album.id, track.number)
                cursor.execute(sql, val)
                db.commit()
                track.id = cursor.lastrowid
            else:
                sql = "INSERT INTO tracks (title, bandid, number) VALUES (%s, %s, %s)"
                print ("track:",track.title, track.band.id, track.number)
                val = (track.title, track.band.id, track.number)
                cursor.execute(sql, val)
                db.commit()
                track.id = cursor.lastrowid

    update_track(track, db)


def store_track(track, db):
    '''
    Stores a Track if it doesn't exist yet
    :param track: Track to be added
    :param db:    database to add in
    '''
    if track.id:
        update_track(track, db)
    elif find_id(track, db):
        update_track(track, db)
    else:
        insert_track(track, db)

def export_to_db(data):
    '''
    Exports the (flat) data to the database
    :param data: Flat data to be exported
    '''
    bands, albums, languages, dances, tracks = unflatten_data(data)
    db = login_to_db()

    for track in tracks.values():
        store_track(track, db)

def get_random_part(track, part_length):
    sound = AudioSegment.from_file(track)
    start = 0
    end = len(sound) - part_length * 1000
    part_start = random.randrange(start, end)
    part_end = part_start + part_length * 1000
    return sound[part_start:part_end]

if __name__ == "__main__":
    db = extract_info_from_collection(sys.argv[1])
    export_to_db(db)