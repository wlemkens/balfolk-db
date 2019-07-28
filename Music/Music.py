
class Band(object):
    def __init__(self, name):
        self.id = None
        self.name = name

    def json(self):
        return { "id" : self.id, "name" : self.name}

    def flat_json(self):
        return { "band_name" : self.name}

class Album(object):
    def __init__(self, band, name, year, nb_tracks):
        self.id = None
        self.band = band
        self.name = name
        self.year = year #
        self.nb_tracks = nb_tracks

    def json(self):
        return { "id" : self.id, "band" : self.band.json(), "name" : self.name, "year" : self.year, "nb_tracks" : self.nb_tracks}

    def flat_json(self):
        band_json = {}
        band = self.band.json()
        for band_field in self.band.json().keys():
            band_json["album_"+band_field] = band[band_field]
        return { "album_name" : self.name, "album_year" : self.year, "album_nb_tracks" : self.nb_tracks, **band_json}

class Track(object):
    def __init__(self, album, number, title, dances, band, filename):
        self.id = None
        self.album = album
        self.number = number
        self.title = title
        self.level = None
        self.dances = dances
        self.band = band
        self.filename = filename

    def json(self):
        dances_json = []
        for dance in self.dances:
            if dance:
                dances_json += [dance.json()]
        return { "id" : self.id, "album" : self.album.json(), "title" : self.title, "level" : self.level, "dances" : dances_json, "band" : self.band.json(), "number" : self.number, "filename" : self.filename}

    def flat_json(self):
        dances_json = []
        for dance in self.dances:
            if dance:
                dances_json += [dance.flat_json()]
        return { "title" : self.title, "level" : self.level, "dances" : dances_json, "number" : self.number, "filename" : self.filename, **self.album.flat_json(), **self.band.flat_json()}

class Dance(object):
    def __init__(self, language, name):
        self.id = None
        self.language = language
        self.nameid = None
        self.name = name

    def json(self):
        return { "id" : self.id, "language" : self.language.json(), "name" : self.name, "nameid" : self.nameid}

    def flat_json(self):
        return self.name

class Language(object):
    def __init__(self, name):
        self.id = None
        self.name = name

    def json(self):
        return { "id" : self.id, "name" : self.name}

