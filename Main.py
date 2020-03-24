from Global import *
from Parser import parse
from Database import USERS, MACROS, MEMES, COMMANDS
from Commands import *
from TwitchBot import *
from Controller import *
from Markov import MarkovModel
from threading import Thread
from colorama import Fore, Back, Style

from PyDisplayDS.Main import *

import re, os, sys, json, time, json, random, traceback, pickle

# Timer Variables
vjoy_time = 0
vjoy_time_last = 0
time_current = time.clock()

time_info_elapsed = 0
time_points_elapsed = 0
time_fix_elapsed = 0
time_bit_display_elapsed = 0
time_chatter_elapsed = 0

time_info_last = 0
time_points_last = 0
time_fix_last = 0
time_bit_display_last = 0
time_chatter_last = 0

# Defaults
WHITELIST_THRESHHOLD = 20
VJOY_REINIT_TIME = 200
INFO_TIME = 1000
POINTS_TIME = 300
FIX_TIME = 150
BIT_DISPLAY_TIME = 300
CHATTER_TIME = 10
MAX_THREAD_COUNT = 20
CURRENT_BITNUM = 0
CURRENT_ACTIVE_USERS = []
RUNNING = True

ACTIVE_CHATTERS = {}

def vjoy_init():
	global vjoy_time, vjoy_time_last

	while True:
		if vjoy_time > VJOY_REINIT_TIME:
			Vjoy.Initialize()
			vjoy_time = 0
			vjoy_time_last = time.clock()
		vjoy_time = time.clock() - vjoy_time_last

def display(user, message, **kwargs):
	print(COLORS[user["color"]] + user["name"] + ": ",end="")
	if kwargs.get("valid") == True:
		print(Fore.GREEN + message)
	elif kwargs.get("error") == True:
		print(Fore.RED + message)
	else:
		print(Fore.WHITE + message)

def update_corpus(user, message):
	if not os.path.isfile("corpuses/" + user["name"] + ".pickle"):
		corpus = {}
		m = MarkovModel(corpus, copy=False)
		m.update_corpus(message)
		with open("corpuses/" + user["name"] + ".pickle", 'wb') as f:
			pickle.dump(m.corpus, f, protocol=pickle.HIGHEST_PROTOCOL)
	else:
		with open("corpuses/" + user["name"] + ".pickle", 'rb') as f:
			corpus = pickle.load(f)
		m = MarkovModel(corpus, copy=False)
		m.update_corpus(message)
		with open("corpuses/" + user["name"] + ".pickle", 'wb') as f:
			pickle.dump(m.corpus, f, protocol=pickle.HIGHEST_PROTOCOL)

		# Update master corpus (all users)
		with open("corpuses/all.pickle", 'rb') as f:
			corpus = pickle.load(f)
		m = MarkovModel(corpus, copy=False)
		m.update_corpus(message)
		with open("corpuses/all.pickle", 'wb') as f:
			pickle.dump(m.corpus, f, protocol=pickle.HIGHEST_PROTOCOL)

# Run a separate thread to make sure vjoy stays running
vjoy_thread = Thread(target=vjoy_init)
vjoy_thread.start()

# Run a separate thread for the chatbot so we can do other things
TwitchBot = TwitchBot()
bot_thread = Thread(target=TwitchBot.run)
bot_thread.start()
PROGRAM_RUNNING = True

USERS["twitchplays_everything"]["level"] = 4

while PROGRAM_RUNNING:

	# While there are messages to be processed
	while len(TwitchBot.messageBuffer) > 0:

		# Grab the message attributes
		username = TwitchBot.messageBuffer[0][0].strip("\r").strip("\n")
		message = TwitchBot.messageBuffer[0][1].strip("\r").strip("\n")
		bitnum = TwitchBot.messageBuffer[0][2]
		subscriber = TwitchBot.messageBuffer[0][3]
		mod = TwitchBot.messageBuffer[0][4]
		user_id = TwitchBot.messageBuffer[0][5]

		# Add the user to the database if they don't exist
		user = USERS[username]
		if user is None:
			if mod:
				USERS.add(username, level=3, subscriber=subscriber, mod=mod, color="cyan", points=1000, messages=0, valid_messages=0, team=0, active_cycles=0)
			else:
				sendmessage("Welcome to TPE! Here is an overview of how things work: " + TUTORIAL_URL)
				USERS.add(username, level=0, subscriber=subscriber, mod=mod, color="cyan", points=1000, messages=0, valid_messages=0, team=0, active_cycles=0)
		user = USERS[username]

		# Attempt to parse this as an input message
		result = parse(message, user)
		if result["valid"]:
			display(user, message, valid=True)
			user["valid_messages"] += 1
			e = Thread(target=Controllers[user["team"]].execute_input_array, args=[result["input_sequence"], user])
			e.start()
		elif result["problem_input"]["error"] != "ERR_INVALID_INPUT":
			error_message = f"{result['problem_input']['error']} occurred at '{result['problem_input']['name']}'"
			display(user, message)
			display({"name": "ERROR", "color": "red"}, error_message, error=True)
			sendwhisper(user["name"], error_message)
		elif message.startswith("!"):
			display(user, message)
			args = message.split(" ")
			response = ""
			if len(args) > 0:
				if len(args[0]) > 1:
					command = args[0][1:]
					if command in globals():
						try:
							if not allowed(user, args[0]):
								response = "Access Denied"
							else:
								response = globals()[command](user, message, args[1:])
						except Exception as e:
							display({"name": "ERROR", "color": "red"}, str(e), error=True)
							print(traceback.format_exc())
					else:
						response = "Command does not exist!"
			if response:
				sendmessage(response)
		else:
			# Update user corpus
			c = Thread(target=update_corpus, args=[user, message])
			c.start()

			display(user, message)
			words = message.split(" ")
			if len(words) == 1:
				for meme in MEMES:
					if words[0] == meme["name"]:
						sendmessage(meme["contents"])
						break

		# Update user attributes
		user["subscriber"] = subscriber
		user["messages"] += 1
		if user["name"] not in CURRENT_ACTIVE_USERS:
			CURRENT_ACTIVE_USERS.append(user["name"])
			user["active_cycles"] = 0

		# Active Chatters
		if user["name"] not in ACTIVE_CHATTERS.keys():
			ACTIVE_CHATTERS[user["name"]] = {"last_message": time.time()}
		else:
			ACTIVE_CHATTERS[user["name"]]["last_message"] = time.time()

		# Check if reached superviewer threshold
		if user["valid_messages"] >= SUPERVIEWER_THRESHOLD:
			if user["level"] == LEVELS["viewer"]:
				USERS.modify(user["name"], {"level": LEVELS["superviewer"]})
				sendmessage("@" + user["name"] + " You have been promoted to superviewer! " + SUPERVIEWER_ABILITIES)

		# Bit Display Zone
		if bitnum > 0:
			if bitnum > CURRENT_BITNUM:
				CURRENT_BITNUM = bitnum
				with open("./obs/bit_display.txt", "w") as file:
					file.write(f"Thanks @{username} for the {bitnum} bits!")
				time_bit_display_elapsed = 0
				time_bit_display_last = time_current
			sendmessage(f"Thanks @{username} for the {bitnum} bits!")

		# Finish up
		for database in [USERS, COMMANDS, MACROS, MEMES]:
			if database.changed:
				database.commit()
		del TwitchBot.messageBuffer[0]

	# Display inputs
	if INPUT_DISPLAY_ENABLED:
		inputs = [button for button in Controllers[0].buttons.keys() if Controllers[0].buttons[button]]
		display_inputs(inputs)

	# Timed Messages
	time_current = time.clock()
	time_info_elapsed = time_current - time_info_last
	time_points_elapsed = time_current - time_points_last
	time_fix_elapsed = time_current - time_fix_last
	time_bit_display_elapsed = time_current - time_bit_display_last
	time_chatter_elapsed = time_current - time_chatter_last

	if time_bit_display_elapsed > BIT_DISPLAY_TIME:
		time_bit_display_elapsed = 0
		time_bit_display_last = time_current
		CURRENT_BITNUM = 0
		with open("./obs/bit_display.txt", "w") as file:
			file.write("")

	if time_info_elapsed > INFO_TIME:
		sendmessage(BOT_INFO)
		time_info_elapsed = 0
		time_info_last = time_current

	if time_chatter_elapsed > CHATTER_TIME:
		current = time.time()
		actually_active = []
		for user,data in ACTIVE_CHATTERS.items():
			if current - data["last_message"] <= 120:
				actually_active.append(user)
		with open("./obs/active_chatters.txt", "w") as file:
			if len(actually_active) == 0:
				file.write("None :(")
			else:
				file.write(", ".join([user for user in actually_active]) + ", ")
		time_chatter_elapsed = 0
		time_chatter_last = time_current

	if time_points_elapsed > POINTS_TIME:
		for username in CURRENT_ACTIVE_USERS:
			USERS[username]["points"] += 50
			USERS[username]["active_cycles"] += 1
		USERS.commit()
		CURRENT_ACTIVE_USERS = []
		time_points_elapsed = 0
		time_points_last = time_current



#
