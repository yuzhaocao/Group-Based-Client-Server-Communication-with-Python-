import socket
import threading
import os
import time
from datetime import datetime
from tkinter import *
from tkinter import messagebox


class ClientCode():
    def __init__(self):
        #creating a TCP socket
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.name = ''

    def connect(self,name,host,port):
        try:
            #setting up connection
            self.name = name
            self.client.connect((host,int(port)))

            th = threading.Thread(target=con.receive,daemon=True)
            th.start()
        
            connectButton.config(state='disabled')
            sendButton.config(state='activ')

            th = threading.Thread(target=con.timer,daemon=True)
            th.start()#starting timer
            
            
                
            iD = (self.client.getsockname())[1] #get client's port 
            self.iD = iD

            global clientID
            clientID = iD
            
            
        except Exception as e:
            #insufficient connection
            messagebox.showerror(title="ERROR!!!", message="Make sure you have the server turned on and have entered everything correctly")


    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('UTF-8')
                message_first = message.split()[0]
                #use the first word of message as a command from the server
                if message_first == 'NAME':
                    #requesting name
                    self.client.send(self.name.encode('UTF-8'))
                    
                elif message_first == 'COORDINATOR':
                    #setting up coordinator
                    iD = message.split()[1]
                    check_coordinator(iD)
                    
                else:
                    #display messages
                    messageText.insert(END,message + '\n')
                    messageText.see(END)
            except:
                #closing the server causing
                #the connection of server and client corrupted
                print('An error occured')
                self.client.close()
                break

    def write(self):
        #exxtracting message from text box andd send message to the server
        message = '{}>-{}({}): {}'.format(datetime.now().strftime('%H:%M:%S'),self.name,self.iD,sendEntry.get())
        self.client.send(message.encode('UTF-8'))
        sendEntry.delete(0,'end')

    def status(self):
        #requesting status info from server
        message = "check status"
        self.client.send(message.encode('UTF-8'))
        

    def timer(self):
        #inactive for x amount of time will terminate the program
        global x
        x = 120

        #movement detection
        root.bind('<Key>',reset)
        root.bind("<Button-1>", reset)
        root.bind("<Button-2>", reset)

        #time countdown
        while x!=0:
            x-=1
            time.sleep(1)
        os._exit(0)


def conn():
    #collecting info and prepare for connection
    name = nameEntry.get()
    host = hostEntry.get()
    port = portEntry.get()
    
    if (len(name) and len(host) and len(port)) < 1:
        messagebox.showerror(title="ERROR!!!", message="make sure you have entered your name, the host address and the port you will listen to")
    else:
        con.connect(name,host,port)
        

def send():
    #activate when send bottom is clicked
    th = threading.Thread(target=con.write,daemon=True)
    th.start()
    
    
def check_status():
    #activate when check status bottom is clicked
    th = threading.Thread(target=con.status,daemon=True)
    th.start()

    

def check_coordinator(iD):
    #checking who is the coordinator
    #if the current user is the coodinator
    # check status bottom will be generated
    
    global coordinator
    coordinator = False
    
    if str(clientID) == str(iD):
        coordinator = True
        
    if coordinator == True:
        sendButton = Button(root,text='Check\nStatus',command=check_status)
        sendButton.place(x=348,y=42,height=40)

        
def handler(event):
    #Use Ctrl-C to exit
    os._exit(0)

def reset(event):
    #resetting the timer when detecting movement from user
    global x
    x = 120
        
        
    
  

con = ClientCode()

#setting up tkinter window
root = Tk()
root.title('Client')
root.geometry('400x400')
root.resizable(0,0)

Label(root,text='NAME').place(x=0,y=10,width=50,height=25)
nameEntry = Entry(root)
nameEntry.place(x=55,y=10,width=285,height=25)

Label(root,text='HOST').place(x=0,y=35,width=50,height=25)
hostEntry = Entry(root)
hostEntry.place(x=55,y=35,width=285,height=25)

Label(root,text='PORT').place(x=0,y=60,width=50,height=25)
portEntry = Entry(root)
portEntry.place(x=55,y=60,width=285,height=25)

connectButton = Button(root,text='Connect',command=conn)
connectButton.place(x=340,y=10,height=25)
Label(root,text='-------------------------------Use Ctrl-C to exit------------------------------').place(x=0,y=85)
messageText = Text(root,relief=GROOVE,bd=3)
messageText.place(x=1,y=110,width=400,height=225)
sendEntry = Entry(root,relief=GROOVE,bd=3)
sendEntry.place(x=1,y=340,width=350,height=40)
sendButton = Button(root,text='Send',command=send)
sendButton.place(x=355,y=340,height=40)
sendButton.config(state='disabled')


root.after(500)  # time in ms.
root.bind_all('<Control-c>', handler) # input to exit


root.mainloop()
