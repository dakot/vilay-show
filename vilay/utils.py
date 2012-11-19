from datetime import datetime

def autumn(n):
	""" Calculating n maximal different rgb-colors and returns them.
	Calculation is done by using the hue value of hsv-pictures. Therefor
	helperfunction valFromHue is used. """
	
	result = []
	for i in range(n):
		hue = int(i*360/n)
		result.append((valFromHue(0,hue),valFromHue(1,hue),valFromHue(2,hue)))
	return result
	
def valFromHue(channel,hue):
	""" Calculating one channel of an rgb signal in relation to the
	hsv-hue value. Channel 0=r,1=g,2=b."""
	
	hue = (hue + (channel)*120 + 120) % 360
	if hue < 60:
		return int(255 * hue /60)
	elif hue < 180:
		return 255
	elif hue < 240:
		return int(-255 * hue /60 + 4*255)
	else:
		return 0
    
def sec2time(secs):
    int_t = int(secs)
    ms = secs - int_t
    tstr = datetime.fromtimestamp(-3600 + int_t).strftime('%H:%M:%S')
    return tstr + '.%.3i' % (ms * 1000)
    
def time2seconds(h,m,s,ms):
    return h*3600+m*60+s+ms*1./1000
    