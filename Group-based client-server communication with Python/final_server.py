import socket
import threading
from tkinter import messagebox
from tkinter import *

#the host and port of the server
host = '127.0.0.1'
port = 8888
s = None

clients = []
names = []
iDs = []
addresses = []

class serverInfo():
    def __init__(self):
        try:
            #setting up the server connection
            self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.server.bind((host,port))
            self.server.listen()

            t = threading.Thread(target=self.receive,daemon=True)
            t.start()
            startButton.config(text = "connected", state='disabled')
            
        except Exception as e:
            #error could occure due to insufficient 
            messagebox.showerror(title="ERROR!!!", message="Make sure you have this server turned on else where")


    def receive(self):
        while True:
            try:
                client, address = self.server.accept()
                iD = address[1] #use unique client port as id
                iDs.append(iD)
                addresses.append(address[0])
                
                showData.insert(END,"Connected with{}\n".format(str(address)))

                #Request And Store Name
                client.send('NAME is?'.encode('UTF-8'))#sent message to this partivular client
                name = client.recv(1024).decode('UTF-8')
                names.append(name)
                clients.append(client)
               
         
                showData.insert(END,"{}\n".format(names))
               
                #the current first client will be the coordinator
                client.send('COORDINATOR {}'.format(iDs[0]).encode('UTF-8'))

                #Print And Broadcast Name              
                showData.insert(END,"Name is {} id: {}\n".format(name,iD))
                self.broadcast("{}({}) joined!\n".format(name,iD).encode('UTF-8'))
                client.send('Connected to server!\n'.encode('UTF-8'))
                
                if len(names) == 1:
                    #inform the client that he/she is the coordinator if they are the first client in the server
                    self.broadcast(("you are the first user in this server\n").encode('UTF-8'))
                    self.broadcast(("you are the coordinator\n").encode('UTF-8'))
                    
                #running the fuction that will send out the info of current online member
                self.current_online(client)

                showData.see(END)
                
                # Start Handling Thread For Client
                thread = threading.Thread(target=self.handle, args=(client,),daemon=True)
                thread.start()
            except:
                break

    def current_online(self,client):
        #send out the list of currently online clients
        client.send('Current online user/s:\n'.encode('UTF-8'))
        users = len(iDs)
        for i in range(users):
            if i == 0:
                client.send("ID: {} Name: {} IP: {} Port: {} (Coordinator)\n".format(iDs[i], names[i], addresses[i],iDs[i]).encode('UTF-8'))
            else:
                client.send("ID: {} Name: {} IP: {} Port: {}\n".format(iDs[i], names[i], addresses[i],iDs[i]).encode('UTF-8'))


    def broadcast(self,message):
        #send message to everyone in the server
        for client in clients:
            client.send(message)

    def handle(self,client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                if message.decode('UTF-8') == "check status":
                    self.current_online(client)
                else:             
                    self.broadcast(message)
            except:
                # Removing And Closing Clients
                i = clients.index(client)
                
                clients.remove(client)
                client.close()
                
                name = names[i]
                iD = iDs[i]
                address = addresses[i]
                
                self.broadcast('{}({}) left!'.format(name,iD).encode('UTF-8'))
                showData.insert(END,'{} left!\n'.format(name))
                names.remove(name)
                iDs.remove(iD)
                addresses.remove(address)
                showData.see(END)
                 
                if len(iDs) != 0:
                    #keep updating the state of coordinator, so that the role of coordinator
                    #is transferred to the next client when the current coordinator left 
                    self.broadcast('COORDINATOR {} \n'.format(iDs[0]).encode('UTF-8'))
                    if i == 0:
                        #index of 0 meaning the current coordinator has left 
                        self.broadcast('{}({}) is now the new coordinator\n'.format(names[0],iDs[0]).encode('UTF-8'))
                
                showData.insert(END,"{}\n".format(names))
                break

def start():
    #starting up the server when teh connect bottom is clicked
    global s
    s = serverInfo()
    
#setting up the tkinter window
root = Tk()
root.title('Server')
root.geometry('300x320')
root.resizable(0,0)
startButton = Button(root,text='Start',command=start)
startButton.place(x=90,y=10)
Label(root,text='Host:{0} Port:{1}'.format(host,port)).place(x=60,y=40)
Label(root,text='*'*18 + 'CLIENT LIST' + '*'*18).place(x=0,y=60)
showData = Text(root,relief=GROOVE,bd=3)
showData.place(x=10,y=80,width=280,height=220)
root.mainloop()
