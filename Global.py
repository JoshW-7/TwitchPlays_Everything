from colorama import Fore

GAME_INPUTS = {
	"DS": ["a", "b", "x", "y", "l", "r", "left", "right", "up", "down", "start", "select"],
	"N64": ["a", "b", "l", "r", "z", "left", "right", "up", "down", "cleft", "cright", "cup", "cdown", "dleft", "dright", "dup", "ddown", "start"],
	"WiiU": ["a", "b", "x", "y", "l", "r", "zl", "zr", "plus", "minus", "lclick", "cclick", "up", "down", "left", "right", "dup", "ddown", "dright", "dleft", "cup", "cdown", "cleft", "cright"]
}
CONSOLE = "WiiU"

UNIVERSAL_INPUTS = ["#", "."]
STATE_INPUTS = ["savestate", "save", "ss", "loadstate", "load", "ls"]
VALID_INPUTS = GAME_INPUTS[CONSOLE] + STATE_INPUTS + UNIVERSAL_INPUTS

DURATION_DEFAULT = 200
DURATION_MAX = 60000
INPUT_SYNONYMS = {
	"pause": "start",
	"kappa": "#",
}

LEVELS = {
    "viewer": 0,
    "whitelist": 1,
    "superviewer": 2,
    "mod": 3,
    "admin": 4,
}

LEVEL_NAMES = {
	0: "Viewer",
	1: "Whitelist",
	2: "Superviewer",
	3: "Mod",
	4: "Admin",
}

COLORS = {
	"red": Fore.RED,
	"green": Fore.GREEN,
	"blue": Fore.BLUE,
	"yellow": Fore.YELLOW,
	"cyan": Fore.CYAN,
	"white": Fore.WHITE
}

SUPERVIEWER_THRESHOLD = 20
SUPERVIEWER_ABILITIES = "You can now use 'ss/save/savestate 4-6' and ls/load/loadstate 1-6 in messages"
BOT_INFO = "MrDestructoid I am a Twitch Plays program written in Python. Type buttons in chat to play and type !tutorial or !commands for more information."
TUTORIAL_URL = "http://twitchplays.wikia.com/wiki/Welcome_to_TPE"

































#
