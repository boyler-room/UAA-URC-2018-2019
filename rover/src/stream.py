#webcam broadcasts via gst-launch
#zed broadcast via shared mem?

import subprocess,signal,threading
import rospy
from rover.msg import cammsg

cams=[#[[launch args],popen instance,control param]
	[['gst-launch-1.0',
			#'v4l2src','device=/dev/video0',
			'videotestsrc',
		'!','video/x-raw,height=480,framerate=15/1',
		'!','x264enc','tune=zerolatency','bitrate=512',
		'!','mpegtsmux',
		'!','udpsink','host=239.0.0.20','port=8080','sync=false','async=false'
		],None,False],
	[['gst-launch-1.0',
			#'v4l2src','device=/dev/video0',
			'videotestsrc',
		'!','video/x-raw,height=480,framerate=15/1',
		'!','x264enc','tune=zerolatency','bitrate=512',
		'!','mpegtsmux',
		'!','udpsink','host=239.0.0.20','port=8081','sync=false','async=false'
		],None,False],
	[['gst-launch-1.0',
			#'v4l2src','device=/dev/video0',
			'videotestsrc',
		'!','video/x-raw,height=480,framerate=15/1',
		'!','x264enc','tune=zerolatency','bitrate=512',
		'!','mpegtsmux',
		'!','udpsink','host=239.0.0.20','port=8082','sync=false','async=false'
		],None,False],
]

def update():
	global cams
	for c in cams:
		if c[1]!=None and c[1].poll()!=None: c[1]=None
		if c[2] and (c[1]==None):
			c[1]=subprocess.Popen(c[0])
			if c[1].poll()!=None:
				#error msg
				c[2]=False
		elif not c[2] and (c[1]!=None):
			c[1].send_signal(signal.SIGINT)
			c[1].wait()
			c[1]=None
update.period=50#ms

def ctrl_h(msg):
	global cams
	if msg.cam<0 or msg.cam>=len(cams): return#error
	if msg.cmd==cammsg.C_STOP: cams[msg.cam][2]=False
	elif msg.cmd==cammsg.C_START: cams[msg.cam][2]=True

def init():
	global ctrltpc
	global runF
	try:
		rospy.init_node('stream')
		ctrltpc=rospy.Subscriber('stream_ctrl',cammsg,ctrl_h)
	except rospy.ROSInitException as e:
		print(e)
		shutdown()
		return
	runF=True

def shutdown():
	global runF
	global cams
	runF=False
	for c in cams:
		c[2]=False
		if c[1]!=None:
			c[1].send_signal(signal.SIGINT)
			c[1].wait()
			c[1].log.close()
			c[1]=None
	rospy.spin()

if __name__=='__main__':
	runF=False
	init()
	while runF:
		try: update()
		except: break
		sleep(update.period/1000)
	shutdown()
