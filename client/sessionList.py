from Tkinter import *
import tkFileDialog
import tkMessageBox
import ttk
import Pmw
import shutil
import json
import os
import requests

class SessionList:

    chosenSession = None
    
    def __init__(self, controller):
        self.root = Tk()
        self.controller = controller
        self.root.title('Collaborative Audio System')
        self.root.iconbitmap('../icons/mp.ico')
        self.request_Sessions()
        self.search_box_frame()
        self.session_list_frame()
        self.bottom_frame()
        self.populate_Session_List()
        self.root.protocol('WM_DELETE_WINDOW', self.close_player)
        self.root.mainloop()

    def search_box_frame(self):
        box_frame = Frame(self.root)

        title=StringVar()
        title.set("Sessions\n")
        labelTitle=Label(box_frame, textvariable=title, height=2, font="DejaVu 15")
        labelTitle.pack()

        text=StringVar()
        text.set("To start collaborating with other artists, select a session.\n" +
                 "To create a new session, press the 'Create session' button.\n")
        labelIntro=Label(box_frame, textvariable=text, height=3, font="DejaVu 10")
        labelIntro.pack(anchor=N)

        labelText=StringVar()
        labelText.set("Fill fields to filter sessions.")
        labelSearch=Label(box_frame, textvariable=labelText, height=1, font="DejaVu 10")
        labelSearch.pack(anchor=W)
        
        self.option = StringVar(box_frame)
        self.option.set("title") # default value
        self.optionmenu = OptionMenu(box_frame, self.option, "curator", "title", "genre", "tempo", "key")
        self.optionmenu.configure(width=20, font="DejaVu 10")
        self.optionmenu.pack(anchor=W)

        self.textbox = Entry(box_frame, font="DejaVu 10")
        self.textbox.insert(END,"enter parameter...\n")
        self.textbox.pack(anchor=W)
        box_frame.grid(row=1, column=2, sticky='n', padx=25, pady =18)

    def session_list_frame(self):
        list_frame = Frame(self.root)
        
        self.tree = ttk.Treeview(list_frame)
        style = ttk.Style()
        style.configure(".", font=('DejaVu', 10))
        style.configure("Treeview", background='#454545' ,foreground='#6ec7b4', font=('DejaVu', 10))
        style.configure("Treeview.Heading", background='#454545',foreground='#454545')
        ysb = ttk.Scrollbar(list_frame, command=self.tree.yview, orient=VERTICAL)
        xsb = ttk.Scrollbar(list_frame, command=self.tree.xview, orient=HORIZONTAL)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.configure(xscrollcommand=xsb.set)
        self.tree['columns']=("curator", "title", "genre", "tempo", "key")
        self.tree['show'] = 'headings'
        self.tree.column("curator", width=110)
        self.tree.column("title", width=110)
        self.tree.column("genre", width=80)
        self.tree.column("tempo", width=40)
        self.tree.column("key", width=40)
        self.tree.heading("curator", text="curator")
        self.tree.heading("title", text="title")
        self.tree.heading("genre", text="genre")
        self.tree.heading("tempo", text="tempo")
        self.tree.heading("key", text="key")
        self.tree.pack(anchor=N)
        
        list_frame.grid(row=2, column=2, padx=5, pady =0, sticky='n')

    def bottom_frame(self):
        bottom_frame = Frame(self.root)

        selectSessTxt = StringVar(bottom_frame)
        selectSessTxt.set("Select Session")
        selectSessBtn = Button(bottom_frame, textvariable=selectSessTxt, command=self.select_Session, borderwidth=10, padx=10)#, command=self.player.rewind)
        selectSessBtn.grid(row=2, column=0, padx=25, pady=10, sticky='w')

        createSessTxt = StringVar(bottom_frame)
        createSessTxt.set("Create Session")
        createSessBtn = Button(bottom_frame, textvariable=createSessTxt, command=self.create_Session, borderwidth=10, padx=10)#, command=self.player.rewind)
        createSessBtn.grid(row=2, column=2, padx=25, pady=10, sticky='e')

        bottom_frame.grid(row=3, column=2)

    def request_Sessions(self):
        response = requests.get('http://127.0.0.1:8080/api/sessions', stream=True)
        with open("sessionList.JSON", 'wb') as out_file:
            # shutil to copy raw data of request into sessionList file
            shutil.copyfileobj(response.raw, out_file)
        del response

        with open("sessionList.JSON") as jsonData:
            #printing a JSON file
            decodedData = json.load(jsonData)
            self.sessionList = decodedData["sessions"]

    def populate_Session_List(self):
        for key in self.sessionList:
            self.tree.insert("" , 0, text=key['idNo'],
                values=(key['curator'],
                        key['title'],
                        key['genre'],
                        key['tempo'],
                        key['key']))

    def select_Session(self):
        print "selecting session"
        curItem = self.tree.focus()

        print self.tree.item(curItem)
        chosenSess = self.tree.item(curItem)
        self.controller.selectedSession = chosenSess.get('text',None) #no entry is default value
        self.root.destroy()
        
    def create_Session(self):
        pass
        self.root.destroy()
        self.controller.selectedSession = None

    def close_player(self):
        # creates a message box when the application is closed
        decision=tkMessageBox.askokcancel("Quit", "Do you really want to quit?\n")
        if decision==True:
            self.controller.EXIT = True
            self.root.destroy()
        
if __name__ == '__main__':
    print 'selecting session'
    #Session()
