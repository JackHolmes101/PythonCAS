# This class acts as a container of the session wav file.
# The class allows the wav file to be coupled with metadata.
class Session:
    
    audioFile = None

    def __init__(self, idNo, title, curator, genre, key, tempo):
        self.idNo = idNo
        self.title = title
        self.curator = curator
        self.genre = genre
        self.key = key
        self.tempo = tempo
