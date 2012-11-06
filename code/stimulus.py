import cv
import cv2

class Stimulus:
	'doc'
	
	def __init__(self, movie_path):
		self.path =			movie_path
		self.data = 		cv2.VideoCapture(self.path)
		self.fps = self.data.get(cv.CV_CAP_PROP_FPS )
		self.nFrames = int(self.data.get(cv.CV_CAP_PROP_FRAME_COUNT ))
		self.width   = int(self.data.get(cv.CV_CAP_PROP_FRAME_WIDTH ))
		self.height  = int(self.data.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
		self.act_time = 0
		self.act_frame = None
		self.speed = 1
	
	def get_next_frame(self):
		self.act_frame = self.data.read()[1]
		self.act_time = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
		return self.act_frame
	
	def set_time(self, new_time):
		if new_time < 0 or new_time > self.nFrames/self.fps:
			return False
		
		try_time = new_time
		got_time = new_time
		
		while got_time >= new_time:
			try_time -= 1
			if try_time < 0:
				got_time = 0
				self.data.set(cv.CV_CAP_PROP_POS_MSEC, got_time)
				self.data.grab()
				break
			self.data.set(cv.CV_CAP_PROP_POS_MSEC, try_time*1000)
			self.data.grab()
			
			got_time = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
		
		delta = new_time - got_time
		frames_to_jump = int(delta*self.fps) - 1
		for i in range(frames_to_jump):
			self.data.grab()
		
		self.act_time = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
		return True
	
	def resync(self, expected_time):
		#print "movie_time", movie_time/1000, "| timer ", sequence.begin + (timer - sequence.time_started) - 1./fps
		skip_frames = 0
		expected_time -= 1./self.fps
		if self.act_time < expected_time:
			delta = expected_time - self.act_time
			skip_frames = int(delta*self.fps)+1
			#print self.act_time, expected_time, delta, skip_frames
			for i in range(skip_frames):
				self.data.grab()
		self.act_time = self.data.get(cv.CV_CAP_PROP_POS_MSEC)/1000
		return skip_frames