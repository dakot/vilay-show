import cv
import cv2

import time
import utils

class Stimulus:
    """Stimulus is a seqence of images, that are fix in time (like movies). In this 
    software it is the main object that all other objects are referenced on.
    
    Actually stimuli can just be movies."""
    # TODO implement stimuli for sequences of pictures 
    
    def __init__(self, movie_path):
        self.path = movie_path
        self.data = cv2.VideoCapture(self.path)
        self.fps = self.data.get(cv.CV_CAP_PROP_FPS )
        self.nFrames = int(self.data.get(cv.CV_CAP_PROP_FRAME_COUNT ))
        self.length  = self.nFrames / self.fps
        self.width   = int(self.data.get(cv.CV_CAP_PROP_FRAME_WIDTH ))
        self.height  = int(self.data.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
        
        # actual information
        self.act_pos = 0   # actual position of stimulus in seconds
        self.act_frame = None   # numpy array containing last frame image
        self.speed = 1
        
        # synchronizing information
        self.start_pos = 0
        self.start_time = 0
        
        # performance caching
        self.end_pos_str = utils.sec2time(self.nFrames/self.fps)
    
    def get_next_frame(self):
        """requests next frame and returns its numpy array representation"""
        
        self.act_frame = self.data.read()[1]
        self.act_pos = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
        return self.act_frame
    
    def set_pos(self, new_pos):
        """sets stimulus position, due to compromized movies it is needed to set position 
        somewhere before requested position and ask for new frames until next frame is
        at the requested new position"""
        
        # checks if new_pos exisits in stimulus
        if new_pos < 0 or new_pos > self.nFrames/self.fps:
            return False
        
        try_pos = new_pos
        got_pos = new_pos
        
        # decrease the tried position as long as the stimulus is set (by open cv) 
        # to a position somewhere before new_pos
        while got_pos >= new_pos:
            try_pos -= 1
            if try_pos < 0:
                got_pos = 0
                self.data.grab()
                self.data.set(cv.CV_CAP_PROP_POS_MSEC, got_pos*1000)
                self.data.grab()
                got_pos = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
                break
            self.data.set(cv.CV_CAP_PROP_POS_MSEC, try_pos*1000)
            self.data.grab()
            got_pos = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
        
        # request frames until new_pos is equal to stimulus position
        delta = new_pos - got_pos
        frames_to_jump = int(delta*self.fps) - 1
        for i in range(frames_to_jump):
            self.data.grab()
        
        self.act_pos = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
        
        return True
    
    def resync(self):
        """This function resynchronizes the stimulus to the expected position. The difference between
        resync and set_pos is that resync just requests a small number of frames that are infront of
        the actual stimulus position (to jump over them) and set_pos sets a completely new position 
        (and is slower). Resync also returns the number of skipped frames."""
        
        skip_frames = 0
        expected_pos = self.start_pos + (time.time()-self.start_time)*self.speed
        delta = expected_pos - self.act_pos
        
        if delta > 1./self.fps:
            skip_frames = int(delta*self.fps)
            for i in range(skip_frames):
                self.data.grab()
        
            self.act_pos = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
        return skip_frames