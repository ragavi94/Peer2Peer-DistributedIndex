import socket
import pickle
import random
import time
from datetime import datetime
import platform

cookieList=[]
BUFFER_SIZE=2048
def setCookie():
	cookie = random.randint(1,50)
	while(cookie in cookieList):
		cookie = random.randint(1,50)
	cookieList.append(cookie)
	#print(cookieList)
	return cookie
	
class Peer:
        def __init__(self, host=None, port=None, cookie=None):
                self.hostname = host    
                self.port = port
                #print (self.cookie)
                self.cookie = cookie
                if self.cookie == None:
                    self.cookie = setCookie()
                    #print (self.cookie)
                    self.no_active = 0
                    #print('Cookie None Instance: ', self.no_active)
                else:
                    self.cookie = cookie #needs change
                    self.no_active = setInstance(self.hostname, myPeer_List)
                    #print('With cookie Instance: ', self.no_active)
                self.active_flag=True
                self.TTL = 7200
                self.recent_reg_dateTime = time.strftime("%H:%M:%S")
#cookieList=[]

class PeerNode:
        def __init__(self,obj:Peer):
                self.peer_obj=obj
                self.next=None
	
        def getpeer_obj(self):
                return self.peer_obj

        def getNext(self):
                return self.next

        def setpeer_obj(self,obj:Peer):
                self.peer_obj=obj

        def setNext(self,newnext):
                self.next = newnext

class PeerList:
        def __init__(self):
                self.head=None
	
        def add(self,peer):
                tmp=PeerNode(peer)
                tmp.setNext(self.head)
                self.head=tmp
                #print('Peer added to linkedlist')
        def show_nodes(self):
                tmp=self.head
                while(tmp!=None):
                    peer_obj=tmp.getpeer_obj()
                    print(peer_obj.hostname,peer_obj.port,peer_obj.cookie,peer_obj.active_flag,peer_obj.TTL,peer_obj.no_active,peer_obj.recent_reg_dateTime)
                    tmp=tmp.getNext()
        def delete(self,host):
                tmp=self.head
                previous=None
                found=False
                while not found:
                    rfc_index=tmp.getpeer_obj()
                    if(rfc_index.hostname == host):
                        found=True
                    else:
                        previous=tmp
                        tmp=tmp.getNext()
                if(previous==None):
                    self.head=tmp.getNext()
                else:
                    previous.setNext(tmp.getNext())


def found_func(list:PeerList,host):
	tmp= list.head
	found=False
	#if(tmp==None):
	#	print('No Peer has Registered yet')
	while tmp!=None:
		peer_obj=tmp.getpeer_obj()
		if(peer_obj.hostname==host):
			found=True
			tmp=tmp.getNext()
		else:
			tmp=tmp.getNext()
	return found
def cmpPeerLists(list:PeerList,host):
	list1=PeerList()
	found=found_func(list,host)
	#print('found:',found)
	tmp=list.head
	while tmp!= None:
		peer_obj=tmp.getpeer_obj()
		if(found==True and peer_obj.active_flag==True):
			#print('both found')
			list1.add(peer_obj)
			tmp=tmp.getNext()
		elif(found==True and peer_obj.active_flag==False):
			#print('Peer Left recently.Please register again with cookie to get list of active peers')
			tmp=tmp.getNext()
			
		else:
			#print('No Peer entry found.Please register to get list of Peers')
			tmp=tmp.getNext()
			
	list1.show_nodes()
	return list1


def setFlag(host, list:PeerList):
	list1=PeerList()
	tmp= list.head
	while tmp!= None:
		peer_obj=tmp.getpeer_obj()
		if(peer_obj.hostname == host):
			peer_obj.active_flag = False
			tmp=tmp.getNext()
		else:
			tmp=tmp.getNext()
		
	print(host + ' is now inactive\n')

def setInstance(host, list:PeerList):
        list1=PeerList()
        tmp= list.head
        while tmp!= None:
                peer_obj=tmp.getpeer_obj()
                if(peer_obj.hostname == host):
                        #print('Before incrementing: ', peer_obj.no_active)
                        peer_obj.no_active+=1
                        #print("After incrementing", peer_obj.no_active)
                        tmp=tmp.getNext()
                        return peer_obj.no_active
                else:
                        tmp=tmp.getNext()
        return 0
	
        

HOST,PORT = '',65500
listen_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
listen_socket.bind((HOST,PORT))
listen_socket.listen(6)

#peer_obj = Peer()
myPeer_List=PeerList()
myactivePeer_List=PeerList()
tobesent=PeerList()
print('RS Server listening on PORT '+ str(PORT))

while True:
		client_connection,client_address=listen_socket.accept()
		getMessage = client_connection.recv(BUFFER_SIZE).decode('utf-8')
		Host = getMessage[getMessage.index('Host')+5:getMessage.index(' <cr> <lf>\nPort')]
		Port = getMessage[getMessage.index('Port')+5:getMessage.index(' <cr> <lf>\nCookie')]
		Cookie = getMessage[getMessage.index('Cookie')+6:getMessage.index(' <cr> <lf>\nOperating')]
        #print ('Received message type from client: ', messageType)
		print('Received a request from ',Host)
		print('From Client\n',getMessage)
		if 'Register' in getMessage:
                #file = client_connection.makefile(mode='rb')
                #objectRecv = pickle.load(file)
                #print (objectRecv.hostname, objectRecv.port, objectRecv.cookie)
                #print(Cookie)
				if Cookie == ' None':
					peer_obj=Peer(Host, Port)
                    #print('Creating an object without cookie')
				else:
					peer_obj=Peer(Host, Port, Cookie)
                    #print('Creating an object with cookie')
                #print(peer_obj)
				myactivePeer_List=cmpPeerLists(myPeer_List,Host)
				if(found_func(myactivePeer_List,Host)== True):
					client_connection.close()
				else:
					myPeer_List.add(peer_obj)
					print('Peer successfully registered with the server')
					print('sending cookie information to the peer')
					sendMessage = 'POST peer-cookie ' + str(peer_obj.cookie) +' <cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) +' <cr> <lf>\n'
					#print('sending cookie information to the peer', peer_obj.cookie)
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.close()
		elif 'PQuery' in getMessage:
				#myPeer_List.show_nodes()
                #print('sending values to compare')
				PQueryList=cmpPeerLists(myPeer_List,Host)
				if(found_func(PQueryList,Host)== True):
					PQueryList.delete(Host)					
					sendMessage = 'POST PQuery Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.send(pickle.dumps(PQueryList,pickle.HIGHEST_PROTOCOL))
				else:
					sendMessage = 'POST PQuery Not Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.close()
		elif 'Leave' in getMessage:
				myactivePeer_List=cmpPeerLists(myPeer_List,Host)
				if(found_func(myactivePeer_List,Host)== True):
					setFlag(Host, myPeer_List)
					sendMessage = 'POST Leave Successful<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
					#client_connection.send("You are no longer part of P2P".encode('utf-8'))
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.close()
				else:
					client_connection.close()
		elif  'KeepAlive' in getMessage:
				sendMessage = 'POST Update TTL Successful<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
				client_connection.send(sendMessage.encode('utf-8'))
				print(sendMessage)
