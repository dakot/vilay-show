import time

class Sequence:
	'doc'
	
	def __init__(self, begin, duration, label = "noname"):
		self.begin = begin
		self.duration = duration
		self.label = label
		
		# for scheduling
		self.frame_count = 0
		self.time_started = 0
		
		# for evaluation
		self.skipped_frames = 0

	def reinit(self):
		self.frame_count = 0
		self.skipped_frames = 0
		self.time_started = time.time()
		
	def contains(self, movie_time):
		# TODO: add condition for movie_time beeing before act_time: actually just approximation implemented (+0.1)
		return movie_time+0.1 >= self.begin and movie_time <= self.begin + self.duration
		
""" global functions for Sequences, all return a new sequence """
def union(seq_arr1, seq_arr2):
	# TODO
	pass

def intersect(seq_arr1, seq_arr2):
	# TODO
	pass

def diff(seq_arr1, seq_arr2):
	# TODO
	pass

def complement(seq_arr, omega_seq):
	# TODO
	pass

