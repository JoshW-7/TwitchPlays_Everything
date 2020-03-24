import pickle
import os


class Database:
	def __init__(self, name, **kwargs):
		self.name = name
		self.changed = False
		self.autocommit = kwargs.get("autocommit", True)
		self.sequential = kwargs.get("sequential", False)
		if not os.path.isfile(f"./database/{self.name}.pickle"):
			if self.sequential:
				self.data = {self.name: []}
			else:
				self.data = {}
			self.commit()
		else:
			with open(f"./database/{self.name}.pickle", 'rb') as f:
				self.data = pickle.load(f)

	def commit(self):
		with open(f"./database/{self.name}.pickle", 'wb') as f:
			pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)
		self.changed = False

	def append(self, log_data):
		if not self.sequential:
			return "This is not a sequential database"
		self.data[self.name].append(log_data)
		if self.autocommit:
			self.commit()
		return f"Added message to {self.name}"

	def add(self, name, **kwargs):
		if not self.get(name):
			self.data[name] = {"name": name}
			for key,value in kwargs.items():
				self.data[name][key] = value
			if self.autocommit:
				self.commit()
			return f"Added '{name}' to {self.name}"
		else:
			return f"'{name}' already exists in {self.name}"

	def remove(self, name):
		if not self.get(name):
			return f"'{name}' does not exist in {self.name}"
		else:
			del self.data[name]
			self.changed = True
			if self.autocommit:
				self.commit()
			return f"'{name}' removed from {self.name}"

	def delete(self):
		os.remove(f"./database/{self.name}.pickle")
		self.__init__(self.name, autocommit=self.autocommit, sequential=self.sequential)
		return f"{self.name} deleted"

	def get(self, name):
		return self.data.get(name)

	def modify(self, name, mods={}):
		if not self.get(name):
			return f"'{name}' does not exist in {self.name}"
		else:
			for key,value in mods.items():
				self.data[name][key] = value
			if self.autocommit:
				self.commit()
			return f"'{name}' modified from {self.name}"

	def __getitem__(self, key):
		val = self.data.get(key)
		if self.autocommit:
			self.commit()
		return val

	def __setitem__(self, key, value):
		self.data[key] = value
		self.changed = True
		if self.autocommit:
			self.commit()

	def __delitem__(self, key):
		del self.data[key]
		self.changed = True
		if self.autocommit:
			self.commit()

	def __iter__(self):
		return iter(self.data.values())

	def __len__(self):
		return len(self.data)

USERS = Database("users")
COMMANDS = Database("commands")
MACROS = Database("macros")
MEMES = Database("memes")
LOG = Database("log", sequential=True)











#
