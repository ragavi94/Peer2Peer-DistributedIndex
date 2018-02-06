import socket
import threading
import csv
import time
import pickle
import sys,os
from threading import Thread
from socketserver import ThreadingMixIn
from datetime import datetime
import platform
import random

Host = ''
port = int(sys.argv[1])
host_name= sys.argv[2]
BUFFER_SIZE=2048
TTL_TIME=30
loc = os.path.dirname(sys.argv[0])+'\\RFC_Files\\'+host_name
print(loc)

class TTLThread(Thread):
	def __init__(self, ttl):
		Thread.__init__(self)
		self.ttl = ttl

	def run(self):
        #print('Sleeping for 30 seconds')
		while(self.ttl):
			time.sleep(1)
			self.ttl=self.ttl-1
			print('ttl:',self.ttl)
		
class peerThread(threading.Thread):
	def __init__(self,socket,clientIP):
		threading.Thread.__init__(self)
		self.lock=threading.Lock()
		print(self.lock)
		self.csocket=socket
		self.ip=clientIP[0]
		self.socket=clientIP[1]

		
	def run(self):
		print("Received connection request from:" + threading.currentThread().getName())
		getMessage = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
		print('From Client\n',getMessage)
		#host = getMessage[getMessage.index('Host ')+5:getMessage.index('<cr> <lf>\nOperating')]
		#print('host',Host)
		#loc='C:\\Users\\RAGAVI\\Desktop\\IP_Project\\RFC_Files\\'+host_name
		if 'GetRFC' in getMessage:
			keep_Alive = getMessage[getMessage.index('KEEP_ALIVE ')+11:]
			rfc_no= getMessage[getMessage.index('RFC_NO ')+7:getMessage.index(' <cr> <lf>\nKEEP_ALIVE')]
			#print('rfc no:',rfc_no)
			filename='rfc'+rfc_no+'.txt'
			#print(filename)
			try:
				f=open(loc+'\\'+filename,'rb')
			except:
				print('Unable to open file.Error')
				self.csocket.close()
			fileSize = os.stat(loc+'\\'+filename).st_size
			sendMessage = 'POST RFC Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) + '<cr> <lf>\nContent Length ' + str(fileSize)
			self.csocket.send(sendMessage.encode('utf-8'))
			print(sendMessage)
			self.csocket.recv(BUFFER_SIZE).decode('utf-8')
			l=f.read(BUFFER_SIZE)
			while(fileSize>0):
				self.csocket.send(l)
				#print('sent',repr(l))
				fileSize = fileSize - BUFFER_SIZE
				l=f.read(BUFFER_SIZE)
				#print(l)
			if((fileSize==0) or (fileSize<0)):
				f.close()
			#print('checking bfore keepAlive')
			while(keep_Alive == 'True'):
					print('waiting for rfc_no')
					getMessage = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
					rfc_no= getMessage[getMessage.index('RFC_NO ')+7:getMessage.index(' <cr> <lf>\nKEEP_ALIVE')]
					keep_Alive = getMessage[getMessage.index('KEEP_ALIVE ')+11:]
					#print('keep_Alive:',keep_Alive)
					filename='rfc'+rfc_no+'.txt'
					#print(filename)
					try:
						f=open(loc+'\\'+filename,'rb')
					except:
						print('Unable to open file.Error')
						self.csocket.close()
					fileSize = os.stat(loc+'\\'+filename).st_size
					sendMessage = 'POST RFC Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) + '\nContent Length ' + str(fileSize)
					self.csocket.send(sendMessage.encode('utf-8'))
					print(sendMessage)
					self.csocket.recv(BUFFER_SIZE).decode('utf-8')
					l=f.read(BUFFER_SIZE)
					while(fileSize>0):
						self.csocket.send(l)
						#print('sent',repr(l))
						fileSize = fileSize - BUFFER_SIZE
						#print(fileSize)
						l=f.read(BUFFER_SIZE)
						#print(l)
					if((fileSize==0) or (fileSize<0)):
						f.close()
				
			self.csocket.close()
			print('finished sending all files')
		elif 'RFCQuery' in getMessage:
			myRFCIndex=RFCList()
			with open(loc+'\\index_list.csv','r') as f:
				reader=csv.reader(f)
				for row in reader:
					#print(row)
					index=RFCIndex(row[0],row[1],row[2])
					myRFCIndex.add(index)
			f.close()
			#myRFCIndex.show()
			
			if(myRFCIndex.head!=None):
				sendMessage = 'POST RFCQuery Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
				print(sendMessage)
				self.csocket.send(sendMessage.encode('utf-8'))
				self.lock.acquire()
				self.csocket.send(pickle.dumps(myRFCIndex,pickle.HIGHEST_PROTOCOL))
				self.lock.release()
				self.csocket.close()
			else:
				sendMessage = 'POST RFCQuery NOT Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
				print(sendMessage)
class RFCIndex:
	def __init__(self,no=None,title_name=None,host_name=None):
		self.rfc_no=no
		self.title=title_name
		self.hostname=host_name
		if((self.hostname==None) or (self.hostname==host_name)):
			self.TTL=7200
		else:
			self.TTL=TTLThread(TTL_TIME)
			#self.TTL.start()
			#ttlthreads.append(self.TTL)
		
	def getrfc_no(self):
		return self.rfc_no
	def gettitle(self):
		return self.title
	def gethostname(self):
		return self.hostname


class RFCNode:
	def __init__(self,obj:RFCIndex):
		self.rfc_node=obj
		self.next=None
	
	def getNode(self):
		return self.rfc_node
	
	def setNode(self,obj:RFCIndex):
		self.rfc_node=obj

	def getNext(self):
		return self.next
	
	def setNext(self,newNext):
		self.next=newNext
		
class RFCList:
	def __init__(self):
		self.head=None
	
	def add(self,index):
		tmp=RFCNode(index)
		tmp.setNext(self.head)
		self.head=tmp
		print('index added to linkedList')
	
	def show(self):
		#rfc_index=RFCIndex()
		tmp=self.head
		while(tmp!=None):
			index=tmp.getNode()
			print(index.rfc_no,index.title,index.hostname)
			#print(index)
			tmp=tmp.getNext()
			
	def delete(self,index):
		tmp=self.head
		previous=None
		found=False
		while not found:
			rfc_index=tmp.getNode
			if(rfc_index == index):
				found=True
			else:
				previous=tmp
				tmp=tmp.getNext()
		if(previous==None):
			self.head=tmp.getNext()
		else:
			previous.setNext(tmp.getNext())


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((Host,port))
threads=[]
ttlthreads=[]


#index = RFCIndex('10','RFC1','Peer1')
#print(rfc_index.rfc_no, rfc_index.title, rfc_index.hostname)

			
while True:
	serverSocket.listen(6)
	print('listening')
	clientSocket, clientIP=serverSocket.accept()
	print(clientSocket)
	print(clientIP)
	new_peer=peerThread(clientSocket,clientIP)
	new_peer.start()
	threads.append(new_peer)

for t in threads:
	t.join()