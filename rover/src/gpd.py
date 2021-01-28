import evdev,rospy
from rover.msg import drvmsg
from rover.msg import armmsg
from rover.msg import mastmsg
ec=evdev.ecodes

gpddev='/dev/input/event16'

def init():
	global gpddev,gpd
	global drivetpc,armtpc,masttpc
	try: gpd=evdev.InputDevice(gpddev)
	except: pass
	try:
		rospy.init_node('gpd')
		drivetpc=rospy.Publisher('drive_ctrl',drvmsg,queue_size=2)
		armtpc=rospy.Publisher('arm_ctrl',armmsg,queue_size=3)
		masttpc=rospy.Publisher('mast_ctrl',mastmsg,queue_size=2)
	except rospy.ROSInitException as e:
		print(e)
		return
"""
	if e.type==ec.EV_KEY:
		if e.code==ec.BTN_NORTH:
			if e.value==1:
		elif e.code==BTN_SOUTH:
		elif e.code==BTN_EAST:
		elif e.code==BTN_WEST:
		elif e.code==BTN_TL:
		elif e.code==BTN_TR:
		elif e.code==BTN_THUMBL:
		elif e.code==BTN_THUMBR:
	if e.type==ec.EV_ABS:
		if e.code==ec.ABS_X: [-32768,32767]
		elif e.code==ec.ABS_Y:
		elif e.code==ec.ABS_RX:
		elif e.code==ec.ABS_RY:
		elif e.code==ec.ABS_Z: [0,255]
		elif e.code==ec.ABS_RZ:
		elif e.code==ec.ABS_HAT0X: 
		elif e.code==ec.ABS_HAT0Y: [-1,1]
"""

def sgn(x):
	if x<0: return -1
	if x>0: return 1
	return 0

def bind_arm(ev):
	global armtpc
	if ev.type==ec.EV_ABS:
		if ev.code==ec.ABS_Z:
			if ev.value>=128:
				if bind_arm.data['grab']!=1:
					bind_arm.data['grab']=1
					armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_GRAB,value=-1)
			else:
				if bind_arm.data['grab']!=0:
					bind_arm.data['grab']=0
					armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_GRAB)
		elif ev.code==ec.ABS_RZ:
			if ev.value>=128:
				if bind_arm.data['grab']!=-1:
					bind_arm.data['grab']=-1
					armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_GRAB,value=1)
			else:
				if bind_arm.data['grab']!=0:
					bind_arm.data['grab']=0
					armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_GRAB)
		if ev.code==ec.ABS_HAT0X:
			if ev.value==0: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_ROTATE)
			elif ev.value==1: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_ROTATE,value=90)
			elif ev.value==-1: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_ROTATE,value=-90)
		elif ev.code==ec.ABS_HAT0Y:
			if ev.value==0: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_WRIST)
			elif ev.value==1: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_WRIST,value=40)
			elif ev.value==-1: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_WRIST,value=-40)
		elif ev.code==ec.ABS_RX:
			tmp=abs(ev.value)//8192
			if tmp==1: tmp=sgn(ev.value)*40
			elif tmp==2: tmp=sgn(ev.value)*60
			elif tmp>=3: tmp=sgn(ev.value)*80
			if tmp!=bind_arm.data['base']:
				bind_arm.data['base']=tmp
				if tmp==0: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_BASE)
				else: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_BASE,value=tmp)
		elif ev.code==ec.ABS_RY:
			tmp=sgn(ev.value)*(abs(ev.value)//8192)*64
			if tmp!=bind_arm.data['should']:
				bind_arm.data['should']=tmp
				if tmp==0: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_SHOULD)
				else: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_SHOULD,value=tmp)
		elif ev.code==ec.ABS_Y:
			tmp=sgn(ev.value)*(abs(ev.value)//8192)*64
			if tmp!=bind_arm.data['elbow']:
				bind_arm.data['elbow']=tmp
				if tmp==0: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_ELBOW)
				else: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_ELBOW,value=tmp)
	elif ev.type==ec.EV_KEY:
		if ev.code==ec.BTN_EAST:
			if ev.value==1: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_SCREW,value=1)
			else: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_SCREW)
			armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_LSRPHIL)
			armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_LSRHEX)
		elif ev.code==ec.BTN_NORTH:
			if ev.value==1: armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_SCREW,value=-1)
			else: armtpc.publish(cmd=armmsg.C_STOP,joint=armmsg.J_SCREW)
			armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_LSRPHIL)
			armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_LSRHEX)
		elif ev.code==ec.BTN_WEST:
			armtpc.publish(cmd=armmsg.C_RUN,joint=armmsg.J_LSRGRAB)
	print(bind_arm.data)
bind_arm.bname='Arm Control'
bind_arm.data={
	'base':0,
	'should':0,
	'elbow':0,
	'grab':0,
}
def bind_tankdrive(ev):
	global drivetpc,masttpc
	if ev.type==ec.EV_ABS:
		if ev.code==ec.ABS_Y:
			if abs(ev.value)//16384==0:
				if bind_tankdrive.data[0]!=0:
					bind_tankdrive.data[0]=0
					drivetpc.publish(cmd=drvmsg.C_LR,data=bind_tankdrive.data)
			else:
				tmp=-sgn(ev.value)*((abs(ev.value)-12288)//4096)*bind_tankdrive.maxspd*100//4
				if bind_tankdrive.data[0]!=tmp:
					bind_tankdrive.data[0]=tmp
					drivetpc.publish(cmd=drvmsg.C_LR,data=bind_tankdrive.data)
		elif ev.code==ec.ABS_RY:
			if abs(ev.value)//16384==0:
				if bind_tankdrive.data[1]!=0:
					bind_tankdrive.data[1]=0
					drivetpc.publish(cmd=drvmsg.C_LR,data=bind_tankdrive.data)
			else:
				tmp=-sgn(ev.value)*((abs(ev.value)-12288)//4096)*bind_tankdrive.maxspd*100//4
				if bind_tankdrive.data[1]!=tmp:
					bind_tankdrive.data[1]=tmp
					drivetpc.publish(cmd=drvmsg.C_LR,data=bind_tankdrive.data)
		elif ev.code==ec.ABS_HAT0Y:
			if ev.value==1: masttpc.publish(cmd=mastmsg.C_CAM_TILT,value=1)
			if ev.value==-1: masttpc.publish(cmd=mastmsg.C_CAM_TILT,value=-1)
		elif ev.code==ec.ABS_HAT0X:
			if ev.value==1: masttpc.publish(cmd=mastmsg.C_CAM_TURN,value=1)
			elif ev.value==-1: masttpc.publish(cmd=mastmsg.C_CAM_TURN,value=-1)
			else: masttpc.publish(cmd=mastmsg.C_CAM_TURN,value=0)
		print(bind_tankdrive.data)
	elif ev.type==ec.EV_KEY:
		if (ev.code==ec.BTN_TL or ev.code==ec.BTN_TR) and ev.value==1:
			bind_tankdrive.data[0]=0
			bind_tankdrive.data[1]=0
			drivetpc.publish(cmd=drvmsg.C_STOP,data=[])
		elif ev.code==ec.BTN_WEST and ev.value==1:
			bind_tankdrive.maxspd=bind_tankdrive.maxspd%10+1
		elif ev.code==ec.BTN_SOUTH and ev.value==1:
			bind_tankdrive.maxspd=(bind_tankdrive.maxspd+8)%10+1
bind_tankdrive.maxspd=10#x100
bind_tankdrive.data=[0,0]
bind_tankdrive.bname='Tank Drive'

def gpdloop():
	global gpd
	binds=[bind_tankdrive,bind_arm]
	bind=0
	while True:
		ev=gpd.read_one()
		if ev==None: continue
		elif ev.type==ec.EV_KEY and ev.code==ec.BTN_MODE:
			break
		elif ev.type==ec.EV_KEY and ev.code==ec.BTN_START and ev.value==1:
			bind=(bind+1)%len(binds)
			print('Binding: %s'%binds[bind].bname)
		elif ev.type==ec.EV_KEY and ev.code==ec.BTN_SELECT and ev.value==1:
			bind=(bind+len(binds)-1)%len(binds)
			print('Binding: %s'%binds[bind].bname)
		else: binds[bind](ev)

init()
gpdloop()
drivetpc.publish(cmd=drvmsg.C_STOP)
armtpc.publish(cmd=armmsg.C_FULLSTOP)
rospy.spin()
#except: pass
