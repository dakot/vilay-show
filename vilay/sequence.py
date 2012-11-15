import time

class Sequence:
    """Sequences are intervalls (tupel of begin and duration) that describe 
    a specific part of an stimulus, e.g. a scene in a movie. Sequences can 
    be labeled by a string"""
    
    def __init__(self, begin, duration, label = "noname"):
        # general sequence data
        self.begin = begin
        self.duration = duration
        self.label = label
        
        # for scheduling
        self.frame_count = 0
        self.time_started = 0
        
        # for evaluation
        self.skipped_frames = 0

    def reinit(self):
        """reinitializes a sequence by resetting 
            - frame_counter (for scheduling), 
            - number of skipped frames (for evaluation) and by 
            - setting start_time (for scheduling issues to actual cpu time) """
        
        self.frame_count = 0
        self.skipped_frames = 0
        self.time_started = time.time()
        
    def contains(self, stimulus_time):
        """function contains returns True if a given stimulus time is part of this scene"""
        # TODO: add condition for movie_time beeing before act_time: actually just approximation implemented (+0.1)
        return stimulus_time+0.1 >= self.begin and stimulus_time <= self.begin + self.duration

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

