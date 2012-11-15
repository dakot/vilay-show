import numpy as np

import sequence

class TimeSeries:
    """A time series is a time-ordered vector of (time, value)-vectors. Time is
    given in seconds (float) and value is any numeric format."""
    
    def __init__(self, filename, label = "noname", approx = "none"):
        """filename: path to text-file of tab-separated values
         label (optional): string that describe this time series
         approx (default=none): approximation type between values (actually just none)"""
        
        self.filename = filename
        self.data = np.loadtxt(filename)
        self.label = label
        self.equal_tupel_length = self.calc_tupel_length()
        self.approx = approx
        
    def get_elem(self, request_time):
        """returns the value of the time series at a specific time point"""
        if self.approx == "none":
            if self.equal_tupel_length > 0:
                n = int( (request_time - self.data[0,0]) / self.equal_tupel_length)
                return self.data[n][1]
            else:
                print "ERROR: not implemented yet"  #TODO
                return None
        else:
            print "ERROR: only approx = 'none' implemented"
    
    def calc_tupel_length(self):
        """returns the duration of one tupel, if constant. Otherwise returns -1"""
        dist = self.data[1,0]-self.data[0,0]
        for i in range(len(self.data)-1):
            if dist != (self.data[i+1,0]-self.data[i,0]):
                return -1
        
        return dist
    
    def get_sequences(self, offset = 0, function = None ):
        """returns a list of sequences where function returns true if calculated 
        with time series values"""
        seq = []
        if self.approx == "none":
            last_val = False
            begin = 0
            end = 0
            for (i,val) in self.data:
                if function is None:
                    act_val = bool(val > 0)
                else:
                    act_val = function(val)
                if last_val != act_val:
                    if act_val:
                        begin = i
                    else:
                        end = i
                        seq.append(sequence.Sequence(min(max(0,begin+offset),self.data[len(self.data)-1,0]), end-begin, self.label))
                last_val = act_val
        
        return seq

# TODO delete (helper function for testing get_sequences)
def greater_zero(a):
    return a>0