import rospy, smbus2
from rover.msg import armmsg

i2cdev=1
i2c_arm=0x04
i2c_ee=0x05

param={
	'base':0,
	'shoulder':0,
	'elbow':0,
	'wrist':0,
	'rotation':0,
	'grab':0,
	'screw':0,
}

def update():
	global param,modes,dim
	global mode,diff
	if diff:
		diff=False
	print("params: %s"%param)
update.period=2000#ms

def ctrl_h(msg):
	global i2cbus,i2c_arm,i2c_ee
	if msg.cmd==C_FULLSTOP:
		i2cbus.write_byte(i2c_arm,0x00)
		i2cbus.write_byte(i2c_ee,0x00)
	elif msg.cmd==C_STOP:
		if msg.joint==armmsg.J_BASE: i2cbus.write_byte_data(i2c_arm,0x00,0x00)
		elif msg.joint==armmsg.J_SHOULD: i2cbus.write_byte_data(i2c_arm,0x00,0x01)
		elif msg.joint==armmsg.J_ELBOW: i2cbus.write_byte_data(i2c_arm,0x00,0x02)
		elif msg.joint==armmsg.J_WRIST: i2cbus.write_byte_data(i2c_ee,0x00,0x00)
		elif msg.joint==armmsg.J_ROTATE: i2cbus.write_byte_data(i2c_ee,0x00,0x01)
		elif msg.joint==armmsg.J_GRAB: i2cbus.write_byte_data(i2c_ee,0x00,0x02)
		elif msg.joint==armmsg.J_SCREW: i2cbus.write_byte_data(i2c_ee,0x00,0x03)
	elif msg.cmd==C_RUN:
		if msg.joint==armmsg.J_BASE:
			if msg.value>=0 and msg.value<256: i2cbus.write_word_data(i2c_arm,0x01,(msg.value<<8)+1)
			elif msg.value>-256: i2cbus.write_word_data(i2c_arm,0x01,msg.value<<8)
		elif msg.joint==armmsg.J_SHOULD:
			if msg.value>=0 and msg.value<256: i2cbus.write_word_data(i2c_arm,0x02,(msg.value<<8)+1)
			elif msg.value>-256: i2cbus.write_word_data(i2c_arm,0x02,msg.value<<8)
		elif msg.joint==armmsg.J_ELBOW:
			if msg.value>=0 and msg.value<256: i2cbus.write_word_data(i2c_arm,0x03,(msg.value<<8)+1)
			elif msg.value>-256: i2cbus.write_word_data(i2c_arm,0x03,msg.value<<8)
		elif msg.joint==armmsg.J_WRIST:
			if msg.value>=0 and msg.value<256: i2cbus.write_word_data(i2c_ee,0x01,(msg.value<<8)+1)
			elif msg.value>-256: i2cbus.write_word_data(i2c_ee,0x01,msg.value<<8)
		elif msg.joint==armmsg.J_ROTATE:
			if msg.value>=0 and msg.value<256: i2cbus.write_word_data(i2c_ee,0x02,(msg.value<<8)+1)
			elif msg.value>-256: i2cbus.write_word_data(i2c_ee,0x02,msg.value<<8)
		elif msg.joint==armmsg.J_GRAB:
			if msg.value==0: i2cbus.write_byte_data(i2c_ee,0x00,0x02)
			elif msg.value<0: i2cbus.write_byte_data(i2c_ee,0x03,0x01)
			else: i2cbus.write_byte_data(i2c_ee,0x03,0x00)
		elif msg.joint==armmsg.J_SCREW:
			if msg.value==0: i2cbus.write_byte_data(i2c_ee,0x00,0x03)
			elif msg.value<0: i2cbus.write_byte_data(i2c_ee,0x04,0x00)
			else: i2cbus.write_byte_data(i2c_ee,0x04,0x01)

def shutdown():
	global i2cbus,i2c_arm,i2c_ee
	global runF
	runF=False
	try: i2cbus.write_byte(i2c_arm,0x00)
	except: pass
	try: i2cbus.write_byte(i2c_ee,0x00)
	except: pass
	rospy.spin()

def init():
	global ctrltpc,i2cbus
	global runF
	try:
		i2cbus=smbus2.SMBus(i2cdev)
        if i2cb.read_byte_data(i2c_arm,0x80)!=0x1F: raise IOError('Arm controller not found.')
        if i2cb.read_byte_data(i2c_ee,0x80)!=0x1F: raise IOError('End effector controller not found.')

	except:
		return
	try:
		rospy.init_node('arm')
		ctrltpc=rospy.Subscriber('arm_ctrl',armmsg,ctrl_h)
		#datasrv=rospy.Service('arm_data',drvsrv,data_h)
	except rospy.ROSInitException as e:
		print(e)
		shutdown()
		return
	runF=True

if __name__=='__main__':
	runF=False
	init()
	while runF:
		#try: update()
		#except: break
		sleep(update.period/1000)
	shutdown()
