#gps and compass readings
import serial,threading,smbus2
import rospy
from rover.msg import navmsg
from time import sleep
from math import

"""
status - gps fix status
lattitude - lattitude, degrees N
longitude - longitude, degrees E
altitude - altitude, m above sea level
course - direction, degrees from N
speed - speed, km/h
speedmph - speed, mph
"""
i2cdev=1
i2c_cmp=0x1e
gpsdev='/dev/ttyUSB0'
params={
	'status':False,
	'lattitude':None,
	'longitude':None,
	'altitude':None,
	'heading':None,
	'inclination':None,
}

def update():
	global gpsbus,datatpc,i2cbus,i2c_cmp
	global params
	s=gpsbus.readline()[:-3].strip().split(',')
	if len(s)>1:
		if s[0]=='$GPGSA':
			try:
				d=int(s[2])
				if d>1: params['status']=True
				else: params['status']=False
			except: pass
		elif s[0]=='$GPGSV': pass
		elif s[0]=='$GPRMC': pass
		elif s[0]=='$GPVTG':
			try:
				d=float(s[1])
				params['course']=d
				d=float(s[7])
				params['speed']=d
				params['speedmph']=d*0.621
			except: pass
		elif s[0]=='$GPGGA':
			try:
				d=int(s[2][:2])+float(s[2][2:])/60
				if s[3]=='S': d=-d
				params['lattitude']=d
				d=int(s[4][:3])+float(s[4][3:])/60
				if s[5]=='W': d=-d
				params['longitude']=d
				d=float(s[9])
				params['altitude']=d
			except: pass
	dx=(i2cbus.read_byte_data(i2c_cmp,0x03)<<8)|i2cbus.read_byte_data(i2c_cmp,0x04)
	dy=(i2cbus.read_byte_data(i2c_cmp,0x07)<<8)|i2cbus.read_byte_data(i2c_cmp,0x08)
	dz=(i2cbus.read_byte_data(i2c_cmp,0x05)<<8)|i2cbus.read_byte_data(i2c_cmp,0x06)
	#mx=dx/gainxy*gausstomtesla
	#my=dy...
	#mz=dz...
	param['heading']=math.degrees(math.atan(dx/dy))
	
update.period=200

def shutdown():
	global gpsbus
	global runF
	runF=False
	gpsbus.close()
	rospy.spin()

def init():
	global datatpc,i2cbus,gpsbus
	global i2cdev,gpsdev,i2c_cmp
	global runF
	try:
		i2cbus=smbus2.SMBus(i2cdev)
		i2cbus.write_byte_data(i2c_cmp,0x02,0x00)
		i2cbus.write_byte_data(i2c_cmp,0x01,0x20))
	except:
		print('error opening compass')
		return
	try:
		gpsbus=serial.Serial(gpsdev)
	except:
		print('error opening gps')
		return
	try:
		rospy.init_node('nav')
		ctrltpc=rospy.Publisher('nav_data',navmsg,queue_size=1)
	except rospy.ROSInitException as e:
		print(e)
		shutdown()
		return
	runF=True

if __name__=='__main__':
	runF=False
	init()
	while runF:
		try: update()
		except: break
		sleep(update.period/1000)
	shutdown()
