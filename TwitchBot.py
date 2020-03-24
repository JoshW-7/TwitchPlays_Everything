import string
import os
import socket
import time
import re

from Settings import HOST, PORT, PASS, IDENT, CHANNEL
from colorama import init as ColoramaInit
from colorama import Fore, Back, Style

timeSendLast = 0.1
durationLastChecked = 0
messagesSent = 0

def send_message(s, message, color="WHITE"):

	global timeSendLast
	global messagesSent

	messageTemp = "PRIVMSG #" + CHANNEL + " :" + message + "\r\n"

	# The message rate is in messages / duration since last message sent
	messageRate = 1 / (time.clock() - timeSendLast)
	while messageRate > 1: messageRate = 1 / (time.clock() - timeSendLast)

	timeSendLast = time.clock()
	s.send(messageTemp.encode('utf-8'))
	messagesSent += 1

	message = messageTemp[messageTemp.find(":")+1:].strip("\r")
	message = message.strip("\n")

	if not(message.startswith("/w")):
		if color == "GREEN": print(Fore.MAGENTA + IDENT + ": " + Fore.GREEN + message)
		else:
			try: print(Fore.MAGENTA + IDENT + ": " + Fore.WHITE + message)
			except: pass

def botmessage(message):
	print(Fore.MAGENTA + "MESSAGE: " + message)

def boterror(message):
	print(Fore.RED + "ERROR: " + message)

def join_room(s):
	readbuffer = ""
	Loading = True
	while Loading:
		readbuffer = readbuffer + s.recv(1024).decode()
		temp = readbuffer.split('\n')
		readbuffer = temp.pop()

		for line in temp:
			Loading = loading_complete(line)

		print(readbuffer)

	os.system("cls")
	send_message(s, "Successfully joined chat!")

def loading_complete(line):

	if("ROOMSTATE" in line):
		return False
	else:
		return True

def open_socket():

	s = socket.socket()
	s.connect((HOST, PORT))

	message = "PASS " + PASS + "\r\n"
	s.send(message.encode('utf-8'))

	message = "NICK " + IDENT + "\r\n"
	s.send(message.encode('utf-8'))

	message = "CAP REQ :twitch.tv/membership" + "\r\n"
	s.send(message.encode("utf-8"))

	response = ""
	while "ACK" not in response:
		response = s.recv(1024).decode("utf-8")
		#print(response)

	message = "CAP REQ :twitch.tv/commands" + "\r\n"
	s.send(message.encode("utf-8"))

	response = ""
	while "ACK" not in response:
		response = s.recv(1024).decode("utf-8")
		#print(response)

	message = "CAP REQ :twitch.tv/tags" + "\r\n"
	s.send(message.encode("utf-8"))

	response = ""
	while "ACK" not in response:
		response = s.recv(1024).decode("utf-8")
		#print(response)

	message = "JOIN #" + CHANNEL + "\r\n"
	s.send(message.encode('utf-8'))

	return s

class TwitchBot:

	def __init__(self):

		self.message = ""
		self.user = ""
		self.EVENT_MESSAGE_RECEIVED = False
		self.COMMAND_PARSE_SUCCESSFUL = False
		self.messageBuffer = []
		self.message_attributes = {}

	def run(self):

		global s, readbuffer

		while True:
			try:
				readbuffer = readbuffer + s.recv(1024).decode("utf-8")
				temp = readbuffer.split('\n')
				readbuffer = temp.pop()
			except:
				readbuffer = ""
				temp = readbuffer.split('/n')
				readbuffer = temp.pop()

			for line in temp:
				if "PING" in line:
					strSend = "PONG :tmi.twitch.tv\r\n".encode('utf-8')
					s.send(strSend)
					break

				# New Code
				mod = 0
				m = re.search(r"(mod=)", line)
				if m != None:
					m = re.search(r"\d+", line[m.end():])
					mod = int(m.string[m.start():m.end()])

				subscriber = 0
				m = re.search(r"(subscriber=)", line)
				if m != None:
					m = re.search(r"\d+", line[m.end():])
					subscriber = int(m.string[m.start():m.end()])

				user = ""
				m = re.search(r"(user-type=)", line)
				if m != None:
					m = re.search(r"[:]", line[m.end():])
					m = re.match(r"[^!]*", m.string[m.end():])
					user = m.string[m.start():m.end()]

				user_id = ""
				m = re.search(r"(user-id=)", line)
				if m != None:
					m = re.search(r"\d+", line[m.end():])
					user_id = m.string[m.start():m.end()]

				message = ""
				m = re.search(r"(PRIVMSG #)", line)
				if m != None:
					m = re.search(r"[:]", line[m.end():])
					message = m.string[m.end():]

				bits = 0
				m = re.search("(bits=)", line)
				if m != None:
					m = re.search("\d+", line[m.end():])
					try:
						bits = int(m.string[m.start():m.end()])
					except Exception as e:
						print(e)

				# Let the main code know there is a message
				if not user.startswith("tmi.twitch.tv") and not user.startswith("jtv MODE") and user != "":
					self.messageBuffer.append([user,message,bits,subscriber,mod,user_id])
					#print("Mod=" + str(mod) + "; Subscriber=" + str(subscriber) + "; User=" + user + "; bits=" + str(bits))


def sendmessage(message="",color="WHITE"):

	global s

	send_message(s,message,color)

def sendwhisper(username, message):
	global s
	try:
		send_message(s, "/w " + username + " " + message)
	except:
		print(Fore.RED + "Error sending whisper")

s = open_socket()
join_room(s)
