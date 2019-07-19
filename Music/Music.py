
class Band(object):
    def __init__(self, name):
        self.id = None
        self.name = name

    def json(self):
        return { "id" : self.id, "name" : self.name}

class Album(object):
    def __init__(self, band, name, year, nb_tracks):
        self.id = None
        self.band = band
        self.name = name
        self.year = year #
        self.nb_tracks = nb_tracks

    def json(self):
        return { "id" : self.id, "band" : self.band.json(), "name" : self.name, "year" : self.year, "nb_tracks" : self.nb_tracks}

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
        return { "id" : self.id, "album" : self.album.json(), "title" : self.title, "level" : self.level, "dances" : dances_json, "band" : self.band.json()}

class Dance(object):
    def __init__(self, language, name):
        self.id = None
        self.language = language
        self.nameid = None
        self.name = name

    def json(self):
        return { "id" : self.id, "language" : self.language.json(), "name" : self.name, "nameid" : self.nameid}

class Language(object):
    def __init__(self, name):
        self.id = None
        self.name = name

    def json(self):
        return { "id" : self.id, "name" : self.name}

