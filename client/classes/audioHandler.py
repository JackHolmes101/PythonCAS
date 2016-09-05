# This class is used by RecordSession to carry out audio
# related tasks such as record and play.

import sounddevice as sd
import soundfile as sf
import numpy
import wave
import pydub
from pydub import AudioSegment
import pyaudio
import sys
from threading import Thread
import wave

class AudioHandler:
    parent = None # this is the recordSession
    duration = 0.0
    stop_rec = False
    stop_play = False
    myRecording = None

    def __init__(self, recordSession):
        self.parent = recordSession

    def stopRecord(self):
        # called by 
        self.stop_rec = True

    def stopPlay(self):
        self.stop_play = True
        
    def record(self):
        # record operation is carried out in its own thread to
        # allow the RecordSession GUI to continue operating.
        record_thread = Thread(target=self.tRecord)
        record_thread.start()
        
    def play(self):
        # play operation is carried out in its own thread to
        # allow the RecordSession GUI to continue operating.
        play_thread = Thread(target=self.tPlay)
        play_thread.start()
    
    def tRecord(self):
        # record operations carried out in thread
        try:
            self.stop_rec = False
            channels = 2
            fs = 44100
            duration = 300
            filename = "takes/recording.wav"
            myRecording=[]
            sd.default.samplerate = fs
            sd.default.channels = channels
            # if it is a newly created session
            if self.parent.newSession:
                print "newSession:",self.parent.newSession
                # just record without backing (as it doesn't exist yet)
                myRecording = sd.rec(duration * fs, samplerate=fs)
            else:
                # if it is an existing session, play existing session
                # in background while recording
                with open("currentSession.wav", 'rb') as f:
                        data, fs = sf.read(f)
                myRecording = sd.playrec(data, fs, channels=channels)
            while self.stop_rec == False:
                # waits for recording to be stopped by button in RecordSession
                pass
            sd.stop()                    
            print "finished recording"
            sf.write(filename, myRecording, fs) # writes array to defined file
            #tell parent to update
            #self.parent.update_takes()
            sys.exit() # access exit code below
        except SystemExit as e:
            # in case of thread exit/stop record
            # - cleans thread up safely, prevents loss of recording
            print "beginning exit!"
            sd.stop()
            if self.parent.newSession: # if it is a newly created session
                # write out array to file
                print "writing array to new file"
                sf.write(filename, myRecording, fs)
                self.parent.update_takes()
            else: # if it is an existing session
                # merge with backing track
                print "merging audio"
                recording = AudioSegment.from_file(filename)
                backing = AudioSegment.from_file("currentSession.wav")
                mergedFile = recording.overlay(backing)
                mergedFile.export("combined.wav", format='wav')
                self.parent.update_takes()

    def tPlay(self):
        # used to play selected takes in RecordSession
        # play operations carried out in thread
        try:
            self.stop_play=False
            # if there isn't a take selected
            if self.parent.selectedTake == '':
                print "no take selected to play..."
                if self.parent.newSession:
                    # if it is newly created, return-there is nothing to play
                    print "new session:",self.parent.newSession
                    self.parent.update_play_button()
                    return
                else:
                    print "playing session track"
                    #load array to access existing session track
                    with open("currentSession.wav", 'rb') as f:
                        data, samplerate = sf.read(f)
                        sd.play(data, samplerate)
                    while self.stop_play == False:
                        pass                        
            else:
                # play selected take
                print "playing"
                with open(self.parent.selectedTake, 'rb') as f:
                    data, samplerate = sf.read(f)
                    sd.play(data, samplerate)
                while self.stop_play == False:
                    pass
            sys.exit() # access exit code below
        except SystemExit as e: # in case of thread exit/stop play - cleans thread up safely
            print("finished playing")
            sd.stop()
            #tell parent to update play button
            self.parent.update_play_button()
            print("closing play thread")

if __name__ == '__main__':
    print "audioHandler"
