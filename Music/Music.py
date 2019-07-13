
class Band(object):
    def __init__(self, name):
        self.id = None
        self.name = name

class Album(object):
    def __init__(self, band, name, year, nb_tracks):
        self.id = None
        self.band = band
        self.name = name
        self.year = year #
        self.nb_tracks = nb_tracks
        self.cddb_id = None

class Track(object):
    def __init__(self, album, number, title, dances, band):
        self.id = None
        self.album = album
        self.number = number
        self.title = title
        self.level = None
        self.dances = dances
        self.band = band

class Dance(object):
    def __init__(self, language, name):
        self.id = None
        self.language = language
        self.nameid = None
        self.name = name

class Language(object):
    def __init__(self, name):
        self.id = None
        self.name = name