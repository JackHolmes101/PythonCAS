import json
import pickle
import shutil
import logging
import logging.config
import cherrypy
from cherrypy.lib import static
from classes.session import Session
import os 
localDir = os.path.dirname(__file__) 
absDir = os.path.join(os.getcwd(), localDir) 

class Sessions:
    
    exposed = True

    def GET(self, id=None): # Get list of sessions in JSON
        if id is None:
            path = os.path.join(absDir, "sessions/sessionList.JSON") 
            return static.serve_file(path, "application/x-download",
            "attachment", os.path.basename(path)) 

        elif id is not None:
            with open("sessions/sessionList.JSON") as jsonData:
                # printing a JSON file
                decodedData = json.load(jsonData)
                tempList = decodedData["sessions"]
                # scan json and check to see if id matches with existing session
                for item in tempList:
                    #for entry in item:                        
                    if item['idNo'] == id:
                        if os.path.isfile(os.path.join("sessions/session_files/", id)): #check file exists
                            print('session:', id,'found')
                            # get pickled session file and serve to client
                            path = os.path.join(absDir, "sessions/session_files/%s" % id) 
                            return static.serve_file(path, "application/x-download",
                                    "attachment", os.path.basename(path))
                            #print('session file not found')
                    else:
                        print('session',id,'not found')
        else:
            return('No sessions with the ID %s' % id)

    def POST(self, myFile = None): # Add session object and update list of sessions 
        loadSesh=None
        print("still in upload...after while")
        # save uploaded file
        with open('upload', 'wb') as out_file:
            shutil.copyfileobj(myFile.file, out_file)
        out_file.close()
        print "finished copying in file"
        with open('upload', 'rb') as handle:
            # get attributes of pickled class so they can be written to the sessionList
            # and so that a proper name can be formed for the session file
            loadSesh = pickle.load(handle)
        handle.close()
        print "loading pickle file"
        with open("sessions/session_files/%s"%loadSesh.idNo,'wb') as session_file:
            pickle.dump(loadSesh, session_file)
        session_file.close()
        
        newEntry = {'idNo':loadSesh.idNo,
                    'title':loadSesh.curator,
                    'curator':loadSesh.title,
                    'genre':loadSesh.genre,
                    'tempo':loadSesh.tempo,
                    'key':loadSesh.key}
        print "newEntry:",newEntry
        
        # append new entry to json file
        print "appending to JSON"
        with open("sessions/sessionList.JSON") as jsonData:
            #printing a JSON file
            decodedData = json.load(jsonData)
            print (json.dumps(decodedData, indent = 4))
            #adding a value
            tempList = decodedData["sessions"]
            tempList.append(newEntry)
            session = {"sessions":tempList}
            print (json.dumps(session, indent = 4))
            jsonData.close()
            #write back to original file
            with open("sessions/sessionList.json", "w") as newFile:
                json.dump(session, newFile)
            newFile.close()

if __name__ == '__main__':
    cherrypy.config.update({'server.max_request_body_size':314572800})# maximum file size for a request to handle.
    cherrypy.tree.mount(
        Sessions(), '/api/sessions',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )

    cherrypy.engine.start()
    cherrypy.engine.block()
