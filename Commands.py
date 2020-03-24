from Global import *
from Database import *
from Markov import MarkovModel
from TwitchBot import sendmessage
import Parser

import time
import sys
import json
import pickle
import random
from datetime import datetime
from profanity import profanity
from Controller import *


def allowed(user, command):
    if COMMANDS.get(command):
        return user["level"] >= COMMANDS[command]["level"]

def setlevel(user, message, args=[]):
    if len(args) != 2:
        return "Incorrect number of arguments"
    if args[0].startswith("!"):
        if user["level"] < 4:
            return "Access Denied"
        if args[0] not in [command["name"] for command in COMMANDS]:
            return "Command does not exist"
        if not args[1].isdigit():
            return "A number must be specified"
        return COMMANDS.modify(args[0], {"level": int(args[1])})
    else:
        if args[0].replace("@","").lower() not in [user["name"] for user in USERS]:
            return "User does not exist"
        if not args[1].isdigit():
            return "A number must be specified"
        if USER[args[0].replace("@","").lower()]['level'] >= user['level']:
            return "You cannot set level of that user"
        return USERS.modify(args[0].replace("@","").lower(), {"level": int(args[1])})

def savestate(user, message, args=[]):
    Controllers[0].hold_digital_duration({"name": "SAVESTATE1", "duration": 500})
    with open("./obs/savestate_message.txt", "w") as file:
        file.write(profanity.censor(message[message.find("!savestate") + len("!savestate") + 1:]))

def viewstate(user, message, args=[]):
    with open("./obs/savestate_message.txt", "r") as file:
        message = file.read()
    return message

def delete(user, message, args=[]):
    if len(args) != 1:
        return "Incorrect number of arguments"
    if args[0].lower() not in ["macros", "memes", "log"]:
        return "Invalid argument"
    if args[0].lower() == "memes":
        return MEMES.delete()
    if args[0].lower() == "macros":
        return MACROS.delete()
    if args[0].lower() == "log":
        return LOG.delete()

def me(user, message, args=[]):
    if len(args) == 1:
        if args[0].replace("@","").lower() not in [user["name"] for user in USERS]:
            return "User does not exist"
        else:
            other_user = USERS[args[0].replace("@","").lower()]
            return f"@{other_user['name']}: {LEVEL_NAMES[other_user['level']]}, {other_user['messages']} total messages, {other_user['valid_messages']} valid input messages ({100 * other_user['valid_messages'] / other_user['messages']:.2f}%), {other_user['points']} points"
    elif len(args) == 0:
        return f"@{user['name']}: {LEVEL_NAMES[user['level']]}, {user['messages']} total messages, {user['valid_messages']} valid input messages ({100 * user['valid_messages'] / user['messages']:.2f}%), {user['points']} points"
    else:
        return "Incorrect number of arguments"

def level(user, message, args=[]):
    if len(args) == 0:
        return f"@{user['name']} is level {user['level']} ({LEVEL_NAMES.get(user['level'])})"
    elif len(args) == 1:
        if args[0].replace("@","").lower() in [user["name"] for user in USERS]:
            other_user = USERS[args[0].replace("@","").lower()]
            return f"@{other_user['name']} is level {other_user['level']} ({LEVEL_NAMES.get(other_user['level'])})"
        else:
            return "User does not exist"
    else:
        return "Incorrect number of arguments"

def points(user, message, args=[]):
    return f"@{user['name']} has {user['points']} points"

def bet(user, message, args=[]):
    if len(args) != 1:
        return "Incorrect number of arguments"
    if not args[0].isdigit():
        return "Wager must be numerical"
    wager = int(args[0])
    if wager > user["points"]:
        return f"WutFace You need {wager - user['points']} more points to make that wager..."
    if random.random() >= 0.5:
        user["points"] += wager
        happyface = random.choice(["SeemsGood", "LUL", "KappaPride"])
        return f"{happyface} @{user['name']} gained {wager} points!"
    else:
        user["points"] -= wager
        sadface = random.choice(["BibleThump", "riPepperonis", "NotLikeThis"])
        return f"{sadface} @{user['name']} lost {wager} points..."

def slots(user, message, args=[]):
    if len(args) != 1:
        return "Incorrect number of arguments"
    if not args[0].isdigit():
        return "Wager must be numerical"
    wager = int(args[0])
    if wager > user["points"]:
        return f"WutFace You need {wager - user['points']} more points to make that wager..."

    slot1 = random.choice(["KappaPride", "WutFace", "BibleThump"])
    slot2 = random.choice(["KappaPride", "WutFace", "BibleThump"])
    slot3 = random.choice(["KappaPride", "WutFace", "BibleThump"])

    MULT = {
        "KappaPride": 1,
        "WutFace": 0,
        "BibleThump": -1,
    }

    points = 0
    if slot1 == "KappaPride" and slot2 == "KappaPride" and slot3 == "KappaPride":
        points = 5*wager
    elif slot1 == "WutFace" and slot2 == "WutFace" and slot3 == "WutFace":
        points = 0
    elif slot1 == "BibleThump" and slot2 == "BibleThump" and slot3 == "BibleThump":
        points = -5*wager
    else:
        multiplier = MULT[slot1] + MULT[slot2] + MULT[slot3]
        points = multiplier*wager

    if points < 0:
        user["points"] += points
        if user["points"] < 0:
            user["points"] = 0
        sadface = random.choice(["BibleThump", "riPepperonis", "NotLikeThis"])
        return f"{slot1} {slot2} {slot3} @{user['name']} lost {points*-1} points..."
    elif points == 0:
        sadface = "WutFace"
        return f"{slot1} {slot2} {slot3} @{user['name']} didn't lost or gain any points..."
    else:
        user["points"] += points
        if user["points"] < 0:
            user["points"] = 0
        happyface = random.choice(["SeemsGood", "LUL", "KappaPride"])
        return f"{slot1} {slot2} {slot3} @{user['name']} gained {wager} points!"

def top(user, message, args=[]):
    top_five = sorted([user for user in USERS], reverse=True, key=lambda u: u["points"])[0:5]
    response = ""
    for n,user in enumerate(top_five):
        response += f"#{n+1}: {user['name']} ({user['points']}), "
    return response

def transfer(user, message, args=[]):
    if len(args) != 2:
        return "Incorrect number of arguments"
    points = args[1]
    if not points.isdigit():
        return "Amount must be numerical"
    other_user = args[0]
    if other_user.replace("@","").lower() not in [user["name"] for user in USERS]:
        return "User does not exist"
    USERS[other_user.replace("@","").lower()]["points"] += int(points)
    USERS[user["name"]]["points"] -= int(points)
    return f"@{user['name']} transfered {int(points)} points to @{other_user.replace('@','')}"

def tutorial(user, message, args=[]):
    return TUTORIAL_URL

def log(user, message, args=[]):
    if len(args) < 1:
        return "No log information provided"
    message = profanity.censor(message[message.find("!log") + len("!log") + 1:])
    return LOG.append({"user": user["name"], "message": message, "timestamp": str(datetime.now())})

def viewlog(user, message, args=[]):
    if len(args) != 0 and len(args) != 1:
        return "Incorrect number of arguments"
    if len(args) == 0:
        if len(LOG["log"]) == 0:
            return "Could not retrieve log"
        try:
            log = LOG["log"][-1]
            timestamp = log["timestamp"].split(".")[0]
        except:
            return "Could not retrieve log"
        finally:
            return f"{timestamp} {log['user']} : {log['message']}"
    elif len(args) == 1:
        if not args[0].isdigit():
            return "Offset must be numerical"
        if int(args[0]) >= len(LOG["log"]):
            return "Could not retrieve log"
        try:
            log = LOG["log"][-1 - int(args[0])]
            timestamp = log["timestamp"].split(".")[0]
        except:
            return "Could not retrieve log"
        finally:
            return f"{timestamp} {log['user']} : {log['message']}"

def show(user, message, args=[]):
    if not allowed(user, "!show"):
        return "Access Denied"

    if len(args) != 1:
        return "Incorrect number of arguments"
    entry = args[0]
    result = None
    if entry.startswith("#"):
        macro = MACROS.get(entry)
        if macro:
            return f"{macro['name']}: {macro['contents']}"
    else:
        meme = MEMES.get(entry)
        if meme:
            return f"{meme['name']}: {meme['contents']}"

    return "{0} does not exist!".format(entry)

def valid_inputs(user, message, args=[]):
    return ", ".join([button for button in VALID_INPUTS])

def length(user, message, args=[]):
    if len(args) < 1:
        return "Incorrect number of arguments"
    result = Parser.parse(''.join(args))
    if result["valid"]:
        return f"Length = {Parser.parse(''.join(args))['duration']}ms"
    else:
        return "Content did not successfully parse"

def stimulate(user, message, args=[]):
    return "Um...no thanks :/"

def simulate(user, message, args=[]):
    if len(args) == 0:
        with open("corpuses/" + user["name"] + ".pickle", 'rb') as f:
            corpus = pickle.load(f)
    elif len(args) == 1:
        other_user = args[0].replace("@","").lower()
        if other_user not in [user["name"] for user in USERS]:
            return "User does not exist"
        with open("corpuses/" + USERS[other_user]["name"] + ".pickle", 'rb') as f:
            corpus = pickle.load(f)
    else:
        return "Incorrect number of arguments"

    if corpus:
        m = MarkovModel(corpus, copy=False)
        return m.generate_sentence(length=20) + " " + m.generate_sentence(length=15) + " " + m.generate_sentence(length=10)

def simulate_all(user, message, args=[]):
    with open("corpuses/all.pickle", "rb") as f:
        corpus = pickle.load(f)
    if corpus:
        m = MarkovModel(corpus, copy=False)
        return m.generate_sentence(length=35) + " " + m.generate_sentence(length=20)

def color(user, message, args=[]):
    if len(args) != 1:
        return "Incorrect number of arguments"
    if args[0].lower() not in COLORS.keys():
        return "Choices: " + ", ".join(color for color in COLORS.keys())
    else:
        user["color"] = args[0].lower()
        return "Color changed"

def commands(user, message, args=[]):
    commands = sorted([command["name"] for command in COMMANDS if user["level"] >= command["level"]])
    if len(commands) < 20:
        return ", ".join(commands)
    elif len(commands) < 40:
        sendmessage(", ".join(commands[0:20]))
        sendmessage(", ".join(commands[20:]))
    elif len(commands) < 60:
        sendmessage(", ".join(commands[0:20]))
        sendmessage(", ".join(commands[20:40]))
        sendmessage(", ".join(commands[40:]))

def macros(user, message, args=[]):
    macros = sorted([macro["name"] for macro in MACROS])
    if len(macros) < 20:
        return ", ".join(macros)
    elif len(macros) < 40:
        sendmessage(", ".join(macros[0:20]))
        sendmessage(", ".join(macros[20:]))
    elif len(macros) < 60:
        sendmessage(", ".join(macros[0:20]))
        sendmessage(", ".join(macros[20:40]))
        sendmessage(", ".join(macros[40:]))

def memes(user, message, args=[]):
    memes = sorted([meme["name"] for meme in MEMES])
    if len(memes) < 20:
        return ", ".join(memes)
    elif len(memes) < 40:
        sendmessage(", ".join(memes[0:20]))
        sendmessage(", ".join(memes[20:]))
    elif len(memes) < 60:
        sendmessage(", ".join(memes[0:20]))
        sendmessage(", ".join(memes[20:40]))
        sendmessage(", ".join(memes[40:]))

def setmessage(user, message, args=[]):
    if len(args) < 1:
        return "No message provided"

    message = profanity.censor(message[message.find("!setmessage") + len("!setmessage") + 1:])

    with open("./obs/message.txt", "w") as file:
        file.write(message)

def add(user, message, args=[]):
    if len(args) < 1:
        return "Incorrect number of arguments"
    if args[0].startswith("!"):
        if len(args) != 1:
            return "Incorrect number of arguments"
        else:
            if args[0][1:] not in FUNCTIONS:
                return "Corresponding function does not exist for '{0}'".format(args[0])
            return COMMANDS.add(args[0], level=0)
    elif args[0].startswith("#"):
        if len(args) < 2:
            return "Incorrect number of arguments"
        else:
            contents = message[message.find(args[0]) + len(args[0]) + 1:]
            if len(args[0]) > 16:
                return "Macro name too long"
            if "<" in Parser.parse(contents, user)["parsed_message"]:
                MACROS.add(args[0], contents=contents)
                return "Macro added, but variable macros cannot checked for validity"
            elif not Parser.parse(contents, user)["valid"]:
                return "Macro contents must parse successfully"
            else:
                MACROS.add(args[0], contents=contents)
    else:
        if len(args) < 2:
            return "Incorrect number of arguments"
        else:
            contents = message[message.find(args[0]) + len(args[0]) + 1:]
            if len(args[0]) > 16:
                return "Meme name too long"
            return MEMES.add(args[0], contents=contents)

def modify(user, message, args=[]):
    if len(args) < 1:
        return "Incorrect number of arguments"
    entry = args[0]
    if entry.startswith("#"):
        contents = message[message.find(entry) + len(entry) + 1:]
        return MACROS.modify(entry, {"contents": contents})
    else:
        contents = message[message.find(entry) + len(entry) + 1:]
        return MEMES.modify(entry, {"contents": contents})

def remove(user, message, args=[]):
    if len(args) != 1:
        return "Incorrect number of arguments"
    entry = args[0]
    if entry.startswith("!"):
        if user["level"] < LEVELS["admin"]:
            return "Commands can only be removed by admin"
        else:
            return COMMANDS.remove(entry)
    elif entry.startswith("#"):
        return MACROS.remove(entry)
    else:
        return MEMES.remove(entry)

def python(user, message, args=[]):
    contents = message[message.find("!python") + len("!python") + 1:]
    exec(contents)










FUNCTIONS = dir(sys.modules[__name__])
