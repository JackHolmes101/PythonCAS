# This class runs the application and passes session
# data between sessionList and sessionRecord.

import sessionList
import recordSession
from classes.audioHandler import AudioHandler
from classes.session import Session


class CASController:

    EXIT = False
    selectedSession = None # id of selected session
    
    def __init__(self):
        self.run()

    def run(self):
        while self.EXIT != True:
            sessList = sessionList.SessionList(self) #create session list
            if self.EXIT == True:
                break
            recordSess = recordSession.RecordSession(self)
            selectedSession = None

if __name__ == '__main__':
    application = CASController()
 
