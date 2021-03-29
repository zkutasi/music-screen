





class UnifiedData(object):
    AUDIO = 'Audio'
    ELSE = 'Else'

    def __init__(self, trackname, artist, album, label, image_url, nowplaying_type):
        self.trackname = trackname
        self.artist = artist
        self.album = album
        self.image_url = image_url
        self.image_present = True
        self.nowplaying_type = nowplaying_type
        if image_url == None:
            self.image_present = False
        self.label = label

    def nowplaying_audio(self):
        return self.nowplaying_type == UnifiedData.AUDIO

    def nowplaying_nonaudio(self):
        return self.nowplaying_type == UnifiedData.ELSE

    def __eq__(self, other):
        if isinstance(other, UnifiedData):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return str(self.__dict__)