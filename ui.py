from tkinter import *
from tkinter import messagebox
from threading import Thread
import time
import os
import sys

class ui:
    def __init__(self,textMode=False):
        self.textMode = textMode
        self.stop = False
    def run(self):
        if self.textMode == False:
            self.uiThread = Thread(target=self.window)
            self.uiThread.daemon = True
            self.uiThread.start()
            time.sleep(0.5)

    def window(self):
        if self.textMode == False:
            self.root = Tk()
            datafile = 'data/videosorter/icon.ico'
            if not hasattr(sys, "frozen"):   # not packed
                datafile = os.path.join(os.path.dirname(__file__), datafile)
            else:
                datafile = os.path.join(sys.prefix, datafile)
            self.root.iconbitmap(datafile)
            self.root.title("VideoSorter")
            self.text = Text(self.root, height=10, width=100)
            self.text.pack()
            self.root.protocol("WM_DELETE_WINDOW", lambda: self.close())
            self.root.mainloop()

    def close(self,sig="",frame=""):
        self.addText("Finishing current step")
        self.stop = True

    def addText(self,text):
        if self.textMode == False:
            self.text.insert(END,text+"\n")
            self.text.see(END)
        else:
            print(text+"\n")

    def askDialog(self,title,content):
        if self.textMode == False:
            return messagebox.askyesno(title, content)
        else:
            validInput = False
            while validInput == False:
                answer = input(content+" Y/N\n").lower()
                if answer == "y":
                    return True
                elif answer == "n":
                    return False

    def informationDialog(self,title,content):
        if self.textMode == False:
            return messagebox.showinfo(title,content)
        else:
            print(content)

    def inputDialog(self,title,content,button):
        if self.textMode == False:
            window=popupWindow(self.root,title,content,button)
            self.root.wait_window(window.top)
            return window.value
        else:
            return input(content+"\n")

class popupWindow(object):
    def __init__(self,master,title,content,button):

        top=self.top=Toplevel(master)
        top.overrideredirect(1)
        top.resizable(width=False, height=False)
        w = 300
        h = 80

        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()

        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        top.geometry('%dx%d+%d+%d' % (w, h, x, y))
        top.title(title)
        self.l = Label(top,text=content)
        self.l.pack()
        self.e = Entry(top)
        self.e.bind("<Return>", self.cleanup)
        self.e.pack()
        self.b = Button(top,text= button, command= self.cleanup)
        self.b.pack()
    def cleanup(self,event=""):
        self.value=self.e.get()
        self.top.destroy()
