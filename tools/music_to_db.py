import os
import sys
import mutagen
import mysql.connector

from Music.Music import *

def parse_dance(dance):
    return dance[0].replace("Folk", "").strip()

def getYear(date):
    if isinstance(date,mutagen.id3.ID3TimeStamp):
        return date.year
    if len(date) > 4:
        parts = date.split("-")
        if len(parts[0]) == 4:
            return int(parts[0])
        else:
            return int(parts[2])
    return int(date)

def extract_v1(file):
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
        genre = None
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
        track = Track(album, track_nb, file["title"][0], [dance], band)
        if "cddb-id" in file.keys():
            album.cddb_id = file["cddb-id"][0]
        return track
    return None

def hasTags(file, tags):
    for tag in tags:
        if not tag in file.keys():
            return False
    return True

def extract_v2(file):
    # band, track
    required_tags = ["TPE1", "TIT2"]
    #print(file)
    if hasTags(file, required_tags):
        artist = file["TPE1"].text[0]
        band = Band(artist)
        language = Language("Nederlands")
        genre = None
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
            # if len(file["totaltracks"]) > 0:
            #     total_tracks = file["totaltracks"][0]
            album = Album(band, file["TALB"].text[0], year, total_tracks)
        track_nb = -1
        if "TRCK" in file:
            track_nb = file["TRCK"].text[0]
        track = Track(album, track_nb, file["TIT2"].text[0], [dance], band)
        if "cddb-id" in file:
            album.cddb_id = file["cddb-id"]
        return track
    return None

def extract_info_from_file(path):
    if (os.path.splitext(path)[1] in [".mp3",".flac"]):
        file = mutagen.File(path)

        if file:
            if "artist" in file.keys() or "albumartist" in file.keys():
                return extract_v1(file)
            else:
                return extract_v2(file)

    return None

def extract_info_from_collection(directory):
    db = []
    print("Extracting ID3 info")
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            track = extract_info_from_file(os.path.join(dirName, fname))
            if track:
                db += [track]
    print ("Found {:} dances".format(len(db)))
    return db

def login_to_db():
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
    mydb = None
    if password:
        mydb = mysql.connector.connect(host = url, password = password, user = login, database = database)
        print("Logged in to {:}".format(url))
    else:
        print("No database login data")
    return mydb

def unflatten_data(flat_data):
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
    Updating tracks
    adding dances to the list
    :param track:
    :param db:
    :return:
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

def is_similar(track, db):
    cursor = db.cursor()
    sql = "SELECT * FROM tracks WHERE levenshtein(title, %s) <= %s"
    val = (track.title, len(track.title)*0.2)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    if len(result) > 0:
        track.id = result[0][0]
        return True
    return False

def store_band(band, db):
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

def insert_track(track, db):
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


def store_track(track, db):
    if track.id:
        update_track(track, db)
    elif is_similar(track, db):
        update_track(track, db)
    else:
        insert_track(track, db)

def export_to_db(data):
    bands, albums, languages, dances, tracks = unflatten_data(data)
    db = login_to_db()

    for track in tracks.values():
        store_track(track, db)



if __name__ == "__main__":
    db = extract_info_from_collection(sys.argv[1])
    export_to_db(db)