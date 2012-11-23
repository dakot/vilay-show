import time

class Snippet:
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


def read_snippets(filename):
    file = open(filename)
    snippets = []
    while True:
        line = file.readline()
        if line == '':
            break
        line = line[0:len(line)-1]
        
        vec = line.split("\t")
        
        if len(line) <=1:
            pass
        elif len(vec) == 2:
            try:
                snippets.append(sequence.Sequence(float(vec[0]),float(vec[1])))
            except Exception, e:
                warnings.warn('read_seq: Could not read input. Begin and duraration have to be float. FORMAT: begin (in sec) TAB duration (in sec) (TAB label) ')
        elif len(vec) == 3:
            try:
                snippets.append(sequence.Sequence(float(vec[0]),float(vec[1]),vec[2]))
            except Exception, e:
                warnings.warn('read_seq: Could not read input. Begin and duraration have to be float. FORMAT: begin (in sec) TAB duration (in sec) (TAB label) ')
        else:
           warnings.warn('read_seq: Could not read input. FORMAT: begin (in sec) TAB duration (in sec) (TAB label) ')
        
    return snippets