
class Band(object):
    def __init__(self, name):
        self.id = None
        self.name = name

class Album(object):
    def __init__(self, band, name, year):
        self.id = None
        self.band = band
        self.name = name
        self.year = year #
        self.cddb_id = None

class Track(object):
    def __init__(self, album, number, title, dances):
        self.id = None
        self.album = album
        self.number = number
        self.title = title
        self.level = None
        self.dances = dances

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