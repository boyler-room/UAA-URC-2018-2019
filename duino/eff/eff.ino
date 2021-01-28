/**/

#include <Wire.h>
#define I2C_ADDR	0x05

//pins
#define	WRIST_DRA	8
#define	WRIST_DRB	7
#define	WRIST_DRV	9

#define	WROT_DRA	13
#define	WROT_DRB	12
#define	WROT_DRV	11

#define	GRAB_DIR	6
#define	GRAB_DRV	5

#define	SCREW_DIR	10
#define	SCREW_DRV	4

#define LASER_GRB	15
#define LASER_SCP	16
#define LASER_SCH	17

typedef unsigned long dword;
typedef struct{
	byte mode;//0:stopped, 1:continuous
	byte dir;//0:brake, 1:ccw(B->A), 2:cw(A->B), 3:brake
	byte spd;//0-255
} abmotor;
typedef struct{
	byte mode;//0:stopped, 1:continuous
	byte dir;//0:ccw(B->A), 1:cw(A->B)
} dmotor;

char mode=0;//0:stopped, 1:per-motor
abmotor wrist, wrot;
dmotor grab, screw;
bool lsr_scp,lsr_sch,lsr_grb;
byte cmd=0x00;

void setup()
{
	pinMode(WRIST_DRA, OUTPUT);
	pinMode(WRIST_DRB, OUTPUT);
	pinMode(WRIST_DRV, OUTPUT);
	
	pinMode(WROT_DRA, OUTPUT);
	pinMode(WROT_DRB, OUTPUT);
	pinMode(WROT_DRV, OUTPUT);
	
	pinMode(GRAB_DIR, OUTPUT);
	pinMode(GRAB_DRV, OUTPUT);
	
	pinMode(SCREW_DIR, OUTPUT);
	pinMode(SCREW_DRV, OUTPUT);
	
	pinMode(LASER_GRB, OUTPUT);
	pinMode(LASER_SCP, OUTPUT);
	pinMode(LASER_SCH, OUTPUT);
	
	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);
}

void loop()
{
	if(mode>0){
		switch(wrist.mode){
		  case 1:
			break;
		  default:
			wrist.spd=0;
			wrist.dir=0;
			break;
		}
		switch(wrot.mode){
		  case 1:
			break;
		  default:
			wrot.spd=0;
			wrot.dir=0;
			break;
		}
		
		digitalWrite(WRIST_DRA, wrist.dir&0x2);
		digitalWrite(WRIST_DRB, wrist.dir&0x1);
		analogWrite(WRIST_DRV, wrist.spd);
		
		digitalWrite(WROT_DRA, wrot.dir&0x2);
		digitalWrite(WROT_DRB, wrot.dir&0x1);
		analogWrite(WROT_DRV, wrot.spd);
		
		digitalWrite(GRAB_DIR, grab.dir);
		digitalWrite(GRAB_DRV, grab.mode);
		
		digitalWrite(SCREW_DIR, screw.dir);
		digitalWrite(SCREW_DRV, screw.mode);

		digitalWrite(LASER_GRB, lsr_grb);
		digitalWrite(LASER_SCP, lsr_scp);
		digitalWrite(LASER_SCH, lsr_sch);
	}
}

void stop()
{
	mode=0;
	wrist.mode=0;
	wrot.mode=0;
	grab.mode=0;
	screw.mode=0;
	lsr_grb=0;
	lsr_scp=0;
	lsr_sch=0;
	
	pinMode(WRIST_DRV, OUTPUT);
	digitalWrite(WRIST_DRA, LOW);
	digitalWrite(WRIST_DRB, LOW);
	digitalWrite(WRIST_DRV, LOW);
	
	pinMode(WROT_DRV, OUTPUT);
	digitalWrite(WROT_DRA, LOW);
	digitalWrite(WROT_DRB, LOW);
	digitalWrite(WROT_DRV, LOW);
	
	digitalWrite(GRAB_DRV, LOW);
	
	digitalWrite(SCREW_DRV, LOW);

	digitalWrite(LASER_SCP, LOW);
	digitalWrite(LASER_SCH, LOW);
	digitalWrite(LASER_GRB, LOW);
}

/*
	WRITE:
		0x00	stop/stop one
		0x01	run wrist
		0x02	... wrot
		0x03	... grab
		0x04	... screw
		0x05	laser grabber
		0x06	laser philips screw
		0x07	laser hex screw
	READ:
		0x80	0x1F
		0x81	wrist mode
		0x82	...
		0x83	...
		0x84	...
		0x85	wrist spd/dir
		0x86	...
		0x87	...
		0x88	...
		0x89	wrist pos
		0x8A	...
		0x8B	...
		0x8C	...
		0x8D
		0x8E
		0x8F	mode
*/

void req()
{
	switch(cmd){
	  case 0x80:
		Wire.write(0x1F);
		break;
	  case 0x81:
		Wire.write(wrist.mode);
		break;
	  case 0x82:
		Wire.write(wrot.mode);
		break;
	  case 0x83:
		Wire.write(grab.mode);
		break;
	  case 0x84:
		Wire.write(screw.mode);
		break;
	  case 0x85:
		Wire.write(wrist.dir);
		Wire.write(wrist.spd);
		break;
	  case 0x86:
		Wire.write(wrot.dir);
		Wire.write(wrot.spd);
		break;
	  case 0x87:
		Wire.write(grab.dir);
		break;
	  case 0x88:
		Wire.write(screw.dir);
		break;
	  case 0x8F:
		Wire.write(mode);
		break;
	}
}

void recv(int count)
{
	if(count--){
		cmd=Wire.read();
		switch(cmd){
		  case 0x00:
			if(count){
				mode=1;
				switch(Wire.read()){
				  case 0:
					wrist.mode=0;
					wrist.dir=0;
					break;
				  case 1:
					wrot.mode=0;
					wrot.dir=0;
					break;
				  case 2:
					grab.mode=0;
					break;
				  case 3:
					screw.mode=0;
					break;
				}
			}else stop();
			break;
		  case 0x01:
			if(count>1){
				mode=1;
				wrist.mode=1;
				wrist.dir=(Wire.read()? 0x1:0x2);
				wrist.spd=Wire.read();
			}break;
		  case 0x02:
			if(count>1){
				mode=1;
				wrot.mode=1;
				wrot.dir=(Wire.read()? 0x1:0x2);
				wrot.spd=Wire.read();
			}break;
		  case 0x03:
			if(count>0){
				mode=1;
				grab.mode=1;
				grab.dir=(!!Wire.read());
			}break;
		  case 0x04:
			if(count>0){
				mode=1;
				screw.mode=1;
				screw.dir=(!!Wire.read());
			}break;
		  case 0x05:
			lsr_grb=!lsr_grb;
			break;
		  case 0x06:
			lsr_scp=!lsr_scp;
			break;
		  case 0x07:
			lsr_sch=!lsr_sch;
			break;
		}while(Wire.available()) Wire.read();
	}
}
