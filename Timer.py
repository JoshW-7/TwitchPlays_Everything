import time


class Timer:

	def __init__(self, duration, **kwargs):
		self.duration = duration
		self.finished = False
		self.func = kwargs.get("func", None)
		self.auto_reset = kwargs.get("auto_reset", True)
		self.start_time = -1
		if kwargs.get("auto_start") == True:
			self.reset()

	def reset(self):
		self.start_time = time.time()

	def time_remaining(self):
		amount = self.duration - (time.time() - self.start_time)
		if amount <= 0:
			return 0
		return amount

	def check_done(self):
		if self.finished:
			return True
		elif self.start_time < 0:
			return False
		elif (time.time() - self.start_time) >= self.duration:
			if self.func:
				self.func()
			if self.auto_reset:
				self.reset()
			else:
				self.finished = True
			return True
		else:
			return False
