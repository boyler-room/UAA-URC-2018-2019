import rospy#,serial
from time import sleep
from rover.msg import drvmsg
from rover.srv import drvsrv

sdevL='/dev/ttyF1'
sdevR='/dev/ttyF0'
#back wheels: channel 1, front: channel 2
#accel=1500
#decel=2000

#input in rpm, m/s, m
dim={#dimensions, centimeters
	'WSEP_LR':1.1,	#Left-Right wheel separation
	'WSEP_FB':0.9,		#Front-Back wheel separation
	'WCIRC':0.44,		#Wheel circumference
	'SPDSCALE':1,		#Angular velocity to controller units
	'FRCONST':1,		#Turn friction compensation
}
modes={
	'MD_STOP':0,	#stop
	'MD_DRIVE':1,	#drive with forward velocity and turn radius
	'MD_SIDE':2,	#tank drive, specify side speeds
	'MD_MOT':3,		#specify each motor speed individually
}
mode=modes['MD_STOP']
diff=False
param={#rads/s and cm/s
	'motFL':0,		#individual motors (rpm)
	'motFR':0,		
	'motBL':0,
	'motBR':0,
	'mmotFL':0,		#measured motor speeds (rpm)
	'mmotFR':0,		
	'mmotBL':0,
	'mmotBR':0,
	'sideL':0,		#left-right sides (rpm)
	'sideR':0,
	'speed':0,		#forward velocity (m/s), or in-place turn angular velocity (rpm)
	'turn':None,	#turn radius, None for inf (m)
	'currL':0,		#total current draw per controller
	'currR':0,
	'voltL':0,		#controller input voltage
	'voltR':0,
}

def scmd(cmdL,cmdR):
	global sbusL,sbusR
	if type(cmdL)==list: cmdL='\r'.join(cmdL)
	if type(cmdR)==list: cmdR='\r'.join(cmdR)
	if cmdL!=None: sbusL.write("%s\r"%cmdL)
	if cmdR!=None: sbusR.write("%s\r"%cmdR)
	rspL=rspR=None
	if cmdL!=None: rspL=sbusL.read()+sbusL.read(sbusL.in_waiting)
	if cmdR!=None: rspR=sbusR.read()+sbusR.read(sbusR.in_waiting)
	return (rspL,rspR)
scmd.timeout=1#seconds

def update():
	global param,modes,dim
	global mode,diff
	if diff:
		if mode==modes['MD_STOP']:
			param['turn']=None
			param['speed']=0
		if mode<=modes['MD_DRIVE']:
			if param['speed']==0:
				mode=modes['MD_STOP']
				param['sideL']=0
				param['sideR']=0
			elif param['turn']==None:
				param['sideL']=param['speed']*60/dim['WCIRC']
				param['sideR']=param['speed']*60/dim['WCIRC']
			elif param['turn']==0:
				param['sideL']=-param['speed']*dim['WSEP_LR']/dim['WCIRC']#interprets speed as angular v
				param['sideR']=+param['speed']*dim['WSEP_LR']/dim['WCIRC']
			else:
				param['sideL']=param['speed']*60*(param['turn']-dim['WSEP_LR'])/(param['turn']*dim['WCIRC'])
				param['sideR']=param['speed']*60*(param['turn']+dim['WSEP_LR'])/(param['turn']*dim['WCIRC'])
		if mode<=modes['MD_SIDE']:
			param['motFL']=param['sideL']
			param['motFR']=param['sideR']
			param['motBL']=param['sideL']
			param['motBR']=param['sideR']
		if mode<=modes['MD_MOT']:
			param['motFL']*=dim['SPDSCALE']
			param['motFR']*=dim['SPDSCALE']
			param['motBL']*=dim['SPDSCALE']
			param['motBR']*=dim['SPDSCALE']
		diff=False
	#scmd([b'!G 2 %d'%param['motFL'],b'!G 1 %d'%param['motBL']],[b'!G 2 %d'%param['motFR'],b'!G 1 %d'%param['motBR']])
	#tmpL,tmpR=scmd(['?A 2','?A 1'],['?A 2','?A 1'])
	#param['currL']=
	#param['currR']=
	#tmpL,tmpR=scmd(['?V'],[])
	#param['voltL']=
	#param['voltR']=
	#tmpL,tmpR=scmd(['?BS 2','?BS 1'],['?BS 2','?BS 1'])
	#param['mmotFL']=
	#param['mmotFR']=
	#param['mmotBL']=
	#param['mmotBR']=
	print("params: %s"%param)
update.period=2000#ms

def ctrl_h(msg):
	global param,modes
	global mode,diff
	if msg.cmd==drvmsg.C_STOP:
		mode=modes['MD_STOP']
	elif msg.cmd==drvmsg.C_DRV:
		mode=modes['MD_DRIVE']
		param['speed']=msg.data[0]*100
		param['turn']=None
	elif msg.cmd==drvmsg.C_TRN:
		mode=modes['MD_DRIVE']
		param['turn']=msg.data[0]*100
	elif msg.cmd==drvmsg.C_DRVTRN:
		mode=modes['MD_DRIVE']
		param['speed']=msg.data[0]*100
		param['turn']=msg.data[1]*100
	elif msg.cmd==drvmsg.C_LEFT:
		mode=modes['MD_SIDE']
		param['sideL']=msg.data[0]
	elif msg.cmd==drvmsg.C_RIGHT:
		mode=modes['MD_SIDE']
		param['sideR']=msg.data[0]
	elif msg.cmd==drvmsg.C_LR:
		mode=modes['MD_SIDE']
		param['sideL']=msg.data[0]
		param['sideR']=msg.data[1]
	elif msg.cmd==drvmsg.C_MOTFL:
		mode=modes['MD_MOT']
		param['motFL']=msg.data[0]
	elif msg.cmd==drvmsg.C_MOTFR:
		mode=modes['MD_MOT']
		param['motFR']=msg.data[0]
	elif msg.cmd==drvmsg.C_MOTBL:
		mode=modes['MD_MOT']
		param['motBL']=msg.data[0]
	elif msg.cmd==drvmsg.C_MOTBR:
		mode=modes['MD_MOT']
		param['motBR']=msg.data[0]
	elif msg.cmd==drvmsg.C_MOTS:
		mode=modes['MD_MOT']
		param['motFL']=msg.data[0]
		param['motFR']=msg.data[1]
		param['motBL']=msg.data[2]
		param['motBR']=msg.data[3]
	diff=True
	
	print("Command %d w/ data %s"%(msg.cmd,msg.data))

def data_h(msg):
	global param,modes,mode
	if msg.cmd==drvsrv.R_DRV: pass
	elif msg.cmd==drvsrv.R_MOT: pass
	elif msg.cmd==drvsrv.R_PWR: pass

def shutdown():
	global sbusL,sbusR
	global runF
	runF=False
	#try:
	#	scmd([b'!G 1 0',b'!G 2 0'],[b'!G 1 0',b'!G 2 0'])
	#	sbusL.close()
	#	sbusR.close()
	#except: pass
	rospy.spin()

def init():
	global sdevL,sdevR
	global sbusL,sbusR
	global ctrltpc,datasrv
	global runF
	#try:
	#	sbusL=serial.Serial(sdevL,115200,timeout=scmd.timeout)
	#	sbusR=serial.Serial(sdevR,115200,timeout=scmd.timeout)
	#	scmd(b'^ECHOF 1',b'^ECHOF 1')
	#	scmd(b'^RWD 500',b'^RWD 500')
	#	scmd([b'!AC 2',b'!AC 1'],b'')
	#	scmd([b'!EES',b'%EESAV'],[b'!EES',b'%EESAV'])
	#except serial.SerialException as e:
	#	print(e)
	#	return
	try:
		rospy.init_node('drive')
		ctrltpc=rospy.Subscriber('drive_ctrl',drvmsg,ctrl_h)
		datasrv=rospy.Service('drive_data',drvsrv,data_h)
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
