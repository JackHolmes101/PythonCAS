# This class resembles the GUI for recording and playing session data.
# The class itself doesn't carry out any of the audio operations,
# instead, these are performed by the audioHandler class.
# and instance of AudioHandler is created upon initialisation.

from Tkinter  import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
import ttk
import os
import time
import Pmw
import shutil
import requests
import cPickle as pickle
import player
import uuid
from classes.audioHandler import AudioHandler
from classes.session import Session

class RecordSession:
    newSession = True 
    selectedTake = '' # The file path to the selected take
    sessionData = None # The loaded session

    def __init__(self, controller):
        # initialisation ensures dependencies,
        # variables and GUI elements are set up
        self.aHandler = AudioHandler(self)
        self.controller = controller
        self.root = Tk() 
        self.root.title('Collaborative Audio System')
        self.root.iconbitmap('../icons/mp.ico')
        self.balloon = Pmw.Balloon(self.root)
        self.setup_Record_Session()
        self.create_title_frame()
        self.create_console_frame()
        self.create_button_frame()
        self.list_frame()
        self.create_bottom_frame()
        self.root.protocol('WM_DELETE_WINDOW', self.close_player)
        self.root.mainloop()

    def setup_Record_Session(self):
        # if new session
        if self.controller.selectedSession == None: 
            print "no session selected creating new session"
            self.remove_previous_content()
            newDialog = MyDialog(self.root)
            print newDialog.result
            print "title", newDialog.result[0]
            self.sessionData = Session(str(uuid.uuid4()), #creates unique identifier
                                       newDialog.result[0],
                                       newDialog.result[1],
                                       newDialog.result[2],
                                       newDialog.result[3],
                                       newDialog.result[4])
            print "session id", self.sessionData.idNo
        # the user selected a session
        else:
            self.newSession = False
            print 'selected session:', self.controller.selectedSession
            response = requests.get('http://127.0.0.1:8080/api/sessions/%s'% self.controller.selectedSession, stream=True)             
            # Process file from response object
            with open("session.pkl", 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            out_file.close()
            # unpickle session file
            with open("session.pkl", 'rb') as handle:
                self.sessionData = pickle.load(handle)
            handle.close()
            del response
            self.remove_previous_content()
            # load session wav into CWD
            # only open audio file if it exists in the session object
            if self.sessionData.audioFile != None:
                try:
                    with open("currentSession.wav", 'wb') as f:
                        f.write(self.sessionData.audioFile)
                    f.close()
                except Exception as e:
                    print "error:"(e)

    def create_title_frame(self):
        # Displays title of the session
        back_frame = Frame(self.root)
        
        self.backIcon = PhotoImage(file='../icons/back.gif')
        self.backbtn=Button(back_frame, text ='back', image=self.backIcon,
                        borderwidth=0, bd=0, command=self.back_to_session_list)
        self.backbtn.grid(row=0, column=0)
        back_frame.grid(row=0, column=1, pady=5, padx=5, sticky='sw')
        
        title_frame = Frame(self.root)       
        titleStr=StringVar()
        titleStr.set(self.sessionData.curator)
        self.labelTitle=Label(title_frame, textvariable=titleStr, height=2, font="DejaVu 15")
        self.labelTitle.grid(row=1, column=0)

        title_frame.configure(background = 'black')
        title_frame.grid(row=1, column=1,pady=5, columnspan=3)    
    
    def create_console_frame(self,state=None):
        # Console to display current status of the application
        cnslfrm = Frame(self.root, background='#454545')

        photo = PhotoImage(file='../icons/screen.gif')
        self.canvas = Canvas(cnslfrm, width=300, height=68, background='#454545' )
        self.canvas.image = photo
        self.canvas.grid(row=1)
        self.console = self.canvas.create_image(0, 0, anchor=NW, image=photo)

        if state == 'play':
            self.consoleText = self.canvas.create_text(25, 28, anchor=W, fill='#6ec7b4', font="DS-Digital 20", text="PLAYING")
            self.songname = self.canvas.create_text(25, 50, anchor=W, fill='#6ec7b4', font="DejaVu 10", text='')
            # disables record button
            self.recordbtn.config(state=DISABLED)
        elif state == 'record':
            self.consoleText = self.canvas.create_text(25, 28, anchor=W, fill='#FF0000', font="DS-Digital 20", text="RECORDING")
            self.songname = self.canvas.create_text(25, 50, anchor=W, fill='#6ec7b4', font="DejaVu 10", text='')
            # disables play button
            self.playbtn.config(state=DISABLED)
        elif state == None:# default state
            self.consoleText = self.canvas.create_text(25, 28, anchor=W, fill='#6ec7b4', font="DS-Digital 20", text="")
            self.songname = self.canvas.create_text(25, 50, anchor=W, fill='#6ec7b4', font="DejaVu 10", text='\"To get started press the record button..."')
            # enables both buttons
            self.create_button_frame()

        self.progressBar = ttk.Progressbar(cnslfrm, length =1, mode="determinate")
        self.progressBar.grid(row=2, columnspan=10, sticky='ew')

        cnslfrm.grid(row=2, column=1, sticky='s',pady=5, padx=20)    
    
    def create_button_frame(self):
        # Buttons to record and play
        buttonframe = Frame(self.root)

        self.recordIconNotActive = PhotoImage(file='../icons/recordIconNotActive.gif')
        self.recordIconActive = PhotoImage(file='../icons/recordIconActive.gif')
        self.recordbtn=Button(buttonframe, text ='notrecording', image=self.recordIconNotActive,
                                borderwidth=0, bd=0, pady=0, padx=0,
                                command=self.toggle_record)# button calls toggle_record()
        self.recordbtn.image = self.recordIconNotActive
        self.recordbtn.grid(row=3, column=2, sticky='s')
        self.balloon.bind(self.recordbtn, 'Record New Take')
             
        self.playicon = PhotoImage(file='../icons/playIcon.gif')
        self.stopicon = PhotoImage(file='../icons/stopIcon.gif')
        self.playbtn=Button(buttonframe, text ='playing', image=self.playicon,
                                borderwidth=0, bd=0, pady=0, padx=0,
                                command=self.toggle_play_stop)# button calls toggle_play_stop()
        self.playbtn.image = self.playicon
        self.playbtn.grid(row=3, column=3, sticky='s')
        self.balloon.bind(self.playbtn, 'Play Selected Take')
        
        buttonframe.grid(row=3, column=1, columnspan=5, sticky='n', pady=0, padx=20)
    
    def list_frame(self):
        # List to hold recorded takes
        list_frame = Frame(self.root)
        
        self.tree = ttk.Treeview(list_frame)
        style = ttk.Style()
        style.configure(".", font=('DejaVu', 10))
        style.configure("Treeview", background='#1f2321' ,foreground='#6ec7b4', font=('DejaVu', 10))
        style.configure("Treeview.Heading", background='#454545',foreground='#454545')
        ysb = ttk.Scrollbar(list_frame, command=self.tree.yview, orient=VERTICAL)
        xsb = ttk.Scrollbar(list_frame, command=self.tree.xview, orient=HORIZONTAL)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.configure(xscrollcommand=xsb.set)
        self.tree['columns']=("Take")
        self.tree['show'] = 'headings'
        self.tree.column("Take", width=300)
        self.tree.heading("Take", text="Take")
        self.tree.pack(anchor=N)
        
        list_frame.grid(row=4, column=1, padx=0, sticky='s', pady =10)

    def create_bottom_frame(self):
        # Bottom frame to simply hold 'upload' button
        bottomframe = Frame(self.root)

        uploadbtn=Button(bottomframe, borderwidth=0, width=20, padx=0, text='Upload Selected Take',
                            command=self.upload) # button calls upload()
        uploadbtn.grid(row=3, column=1, sticky='n')
        
        bottomframe.grid(row=5, column=1, sticky='n', padx=15, pady=25)
        
    def update_takes(self):
        # count the number of files in 'takes' directory to create names for takes
        path, dirs, files = os.walk("takes").next()
        file_count = len(files)
        #get file that was just recorded and update take list
        file_path = "takes/take%s.wav"%file_count
        shutil.copyfile("takes/recording.wav", file_path) # create new take file
        self.tree.insert("", 0, text=file_path, values=("take%s"%file_count)) # update take list
        self.recordbtn.config(text='notrecording', image=self.recordIconNotActive)

    def upload(self):
        # this function uploads the selected take to the server using a POST request
        # write take to session object
        with open(self.get_list_selection(), 'rb') as f:
            wav = f.read()
        f.close()
        setattr(self.sessionData,'audioFile',wav)
        # pickle sessionData class
        with open("sessions/session_files/%s"%self.sessionData.idNo, 'wb') as handle:
            pickle.dump(self.sessionData, handle)
        print self.sessionData.idNo
        files = open("sessions/session_files/%s"%self.sessionData.idNo, 'rb')
        url = 'http://127.0.0.1:8080/api/sessions/'
        r = requests.post(url, files={'myFile': files})
        print "file uploaded"

    def toggle_record(self):
        # toggle record functionality of the AudioHandler
        if self.recordbtn['text'] =='recording':
            self.recordbtn.config(text='notrecording', image=self.recordIconNotActive)
            self.aHandler.stopRecord()
            self.create_console_frame()
        elif self.recordbtn['text'] =='notrecording':
            self.recordbtn.config(text ='recording', image=self.recordIconActive)
            self.aHandler.record()
            self.create_console_frame('record')
  
    def toggle_play_stop(self):
        # toggle play functionality of the AudioHandler
        if self.playbtn['text'] =='playing':
            self.playbtn.config(text='notplaying', image=self.stopicon)
            # tells AudioHandler to play selected take
            self.selectedTake = self.get_list_selection()
            self.aHandler.play()
            self.create_console_frame('play')
        elif self.playbtn['text'] =='notplaying':
            self.playbtn.config(text ='playing', image=self.playicon)
            self.aHandler.stopPlay()
            self.create_console_frame()

    def update_play_button(self):
        # called by the AudioHandler to ensure that the play button and console changes accordingly 
        self.playbtn.config(text='playing', image=self.playicon)
        self.create_console_frame()
        
                      
    def get_list_selection(self):
        # returns the file path to the selected take
        curItem = self.tree.focus() # get currently selected item in treeview
        chosenSess = self.tree.item(curItem)
        chosenFile=chosenSess.get('text',None)
        return chosenFile
        
    def close_player(self):
        # creates a message box when the application is closed
        decision=tkMessageBox.askokcancel("Quit", "Do you really want to quit?\n"
            +" Any takes that haven't been uploaded"
            +" will be lost")
        if decision==False:
            try:
                self.aHandler.stopPlay()
            except:
                pass
        else:
            self.controller.EXIT = True
            self.root.destroy()

    def back_to_session_list(self):
            self.root.destroy()

    def remove_previous_content(self):
        #delete any files from previous sessions
        folder = 'takes'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        try:
            os.remove("currentSession.wav")
        except Exception as e:
            print(e)

class MyDialog(tkSimpleDialog.Dialog):
# Dialogue box to take new session details
    def body(self, master):
        Label(master, text="Create a new session", height=3, font="DejaVu 15").grid(row=0, columnspan=2)
        Label(master, text="Enter the details of the new session.").grid(row=1, columnspan=2, padx=10, pady=10)
        Label(master, text="Title:").grid(row=2)
        Label(master, text="Curator:").grid(row=3)
        Label(master, text="Genre:").grid(row=4)
        Label(master, text="Tempo:").grid(row=5)
        Label(master, text="Key:").grid(row=6)

        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)
        self.e4 = Entry(master)
        sharp = unichr(9837)
        self.var = StringVar(master)
        self.var.set("unspecified")
        self.e5 = OptionMenu(master,self.var,
                             "A", "A"+sharp,
                             "B", "B"+sharp,
                             "C", "C"+sharp,
                             "D", "D"+sharp,
                             "E", "E"+sharp,
                             "F", "F"+sharp,
                             "G", "G"+sharp)

        self.e1.grid(row=2, column=1)
        self.e2.grid(row=3, column=1)
        self.e3.grid(row=4, column=1)
        self.e4.grid(row=5, column=1)
        self.e5.grid(row=6, column=1)
        return self.e1 # initial focus

    def validate(self):
        #basic validation checks field for appropriate values
        try:
            title= str(self.e1.get())
            curator = str(self.e2.get())
            genre = str(self.e3.get())
            tempo = float(self.e4.get())
            key = self.var.get()
            if not title or not curator or not genre or not tempo or not key:
                tkMessageBox.showwarning(
                "Bad input",
                "Missing values, please try again"
                )
                return 0
            self.result = curator, title, genre, key, tempo
            return 1
        except ValueError:
            tkMessageBox.showwarning(
                "Bad input",
                "Illegal values, please try again"
            )
            return 0

    def apply(self):
        pass
        
if __name__ == '__main__':
    print "record session"

