





class UnifiedData(object):
    def __init__(self, trackname, artist, album, label, image_url, nowplaying):
        self.trackname = trackname
        self.artist = artist
        self.album = album
        self.image_url = image_url
        self.image_present = True
        self.nowplaying = nowplaying
        if image_url == None:
            self.image_present = False
        self.label = label

    def __eq__(self, other):
        if isinstance(other, UnifiedData):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return str(self.__dict__)