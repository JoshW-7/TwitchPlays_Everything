import random
import copy
import sqlite3

class MarkovModel:

	def __init__(self, corpus={}, **kwargs):
		if kwargs.get("copy") == True:
			self.corpus = copy.deepcopy(corpus)
		else:
			self.corpus = corpus

	def _sanitized(self, message):
		illegal_chars = [".", ",", "!", "?", "\n", ":", "'", '"']
		for char in illegal_chars:
			message = message.replace(char, "")
		return message

	def update_corpus(self, message):
		sentences = [sentence for sentence in message.split(".") if len(sentence) > 0]
		for sentence in sentences:
			words = [word for word in sentence.split(" ") if len(word) > 0]
			for i in range(len(words)-2):
				first, second, third = (words[i], words[i+1], words[i+2])
				if (first,second) not in self.corpus.keys():
					self.corpus[(first,second)] = {
						"total": 1,
						"next": {
							third: 1,
						}
					}
				else:
					self.corpus[(first,second)]["total"] += 1
					if third not in self.corpus[(first,second)]["next"].keys():
						self.corpus[(first,second)]["next"][third] = 1
					else:
						self.corpus[(first,second)]["next"][third] += 1

	def merge_corpus(self, other_corpus):
		for key,values in other_corpus.items():
			if key not in self.corpus.keys():
				self.corpus[key] = {
					"total": values["total"],
					"next": values["next"],
				}
			else:
				self.corpus[key]["total"] += values["total"]
				for word in values["next"]:
					if word in self.corpus[key]["next"]:
						self.corpus[key]["next"][word] += values["next"][word]
					else:
						self.corpus[key]["next"][word] = values["next"][word]

	def generate_sentence(self, **kwargs):
		start = kwargs.get("start")
		if start is not None:
			found = False
			for key in self.corpus.keys():
				if key[0].lower().startswith(start.lower()):
					pair = key
					found = True
			if not found:
				pair = random.choice(list(self.corpus.keys()))
		else:
			pair = random.choice(list(self.corpus.keys()))

		words = [pair[0], pair[1]]
		next_word = ""
		capitalize = False
		for i in range(kwargs.get("length", 20)):
			if self.corpus.get(pair) or self.corpus.get( (self._sanitized(pair[0]), self._sanitized(pair[1]) )):
				if not self.corpus.get(pair):
					pair = (self._sanitized(pair[0]), self._sanitized(pair[1]))
				choices = [word for word in self.corpus[pair]["next"].keys()]
				weights = [n for n in self.corpus[pair]["next"].values()]
				next_word = random.choices(choices, weights=weights, k=1)[0]
				if capitalize:
					next_word = next_word.capitalize()
				pair = (pair[1], next_word)
				if next_word.endswith(".") or next_word.endswith("!") or next_word.endswith("?"):
					capitalize = True
				else:
					capitalize = False
				words.append(next_word)
			else:
				break

		words[0] = words[0].capitalize()
		if (not words[-1].endswith(".") and not words[-1].endswith("!") and not words[-1].endswith("?")) or words[-1].endswith(","):
			if words[-1].endswith(","):
				words[-1] = words[-1].strip(",")
			words[-1] = words[-1] + random.choices([".", "!", "?"], weights=[1, kwargs.get("exitement", 0), kwargs.get("inquisitiveness", 0)], k=1)[0]

		return " ".join(words)
