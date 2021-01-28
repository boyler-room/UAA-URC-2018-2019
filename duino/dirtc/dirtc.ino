#include <Wire.h>
#define I2C_ADDR	0x07

#define	SCOOPR_DRA	4
#define	SCOOPR_DRB	5
#define	SCOOPR_DRV	6

#define	SCOOPL_DRA	13
#define	SCOOPL_DRB	12
#define	SCOOPL_DRV	11

#define	HEIGHT_DRA	3
#define	HEIGHT_DRB	2
#define	HEIGHT_DRV	10

#define RAMP_DRA	7
#define RAMP_DRB	8
#define RAMP_DRV	9

typedef struct{
	byte mode;//0:stopped, 1:continuous
	byte dir;//0:brake, 1:ccw(B->A), 2:cw(A->B), 3:brake
	byte spd;//0-255
} motor;

char mode=0;//0:stopped, 1:per-motor
motor scoop,height,ramp;
byte cmd=0x00;

void setup()
{
	pinMode(SCOOPR_DRA,OUTPUT);
	pinMode(SCOOPR_DRB,OUTPUT);
	pinMode(SCOOPR_DRV,OUTPUT);
	
	pinMode(SCOOPL_DRA,OUTPUT);
	pinMode(SCOOPL_DRB,OUTPUT);
	pinMode(SCOOPL_DRV,OUTPUT);
	
	pinMode(HEIGHT_DRA,OUTPUT);
	pinMode(HEIGHT_DRB,OUTPUT);
	pinMode(HEIGHT_DRV,OUTPUT);
	
	pinMode(RAMP_DRA,OUTPUT);
	pinMode(RAMP_DRB,OUTPUT);
	pinMode(RAMP_DRV,OUTPUT);
	
	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);
}

void loop()
{
	if(mode>0){
		switch(scoop.mode){
		  case 1:
			break;
		  default:
			scoop.spd=0;
			scoop.dir=0;
			break;
		}
		switch(height.mode){
		  case 1:
			break;
		  default:
			height.spd=0;
			height.dir=0;
			break;
		}
		switch(ramp.mode){
		  case 1:
			break;
		  default:
			ramp.spd=0;
			ramp.dir=0;
			break;
		}
		
		digitalWrite(SCOOPR_DRA, scoop.dir&0x2);
		digitalWrite(SCOOPR_DRB, scoop.dir&0x1);
		digitalWrite(SCOOPL_DRA, scoop.dir&0x2);
		digitalWrite(SCOOPL_DRB, scoop.dir&0x1);
		analogWrite(SCOOPR_DRV, scoop.spd);
		analogWrite(SCOOPL_DRV, scoop.spd);
		
		digitalWrite(HEIGHT_DRA, height.dir&0x2);
		digitalWrite(HEIGHT_DRB, height.dir&0x1);
		analogWrite(HEIGHT_DRV, height.spd);
		
		digitalWrite(RAMP_DRA, ramp.dir&0x2);
		digitalWrite(RAMP_DRB, ramp.dir&0x1);
		analogWrite(RAMP_DRV, ramp.spd);
	}
}

void stop()
{
	mode=0;
	scoop.mode=0;
	height.mode=0;
	ramp.mode=0;
	
	pinMode(SCOOPR_DRV, OUTPUT);
	pinMode(SCOOPL_DRV, OUTPUT);
	digitalWrite(SCOOPR_DRA, LOW);
	digitalWrite(SCOOPR_DRB, LOW);
	digitalWrite(SCOOPL_DRA, LOW);
	digitalWrite(SCOOPL_DRB, LOW);
	digitalWrite(SCOOPR_DRV, LOW);
	digitalWrite(SCOOPL_DRV, LOW);
	
	pinMode(HEIGHT_DRV, OUTPUT);
	digitalWrite(HEIGHT_DRA, LOW);
	digitalWrite(HEIGHT_DRB, LOW);
	digitalWrite(HEIGHT_DRV, LOW);
	
	pinMode(RAMP_DRV, OUTPUT);
	digitalWrite(RAMP_DRA, LOW);
	digitalWrite(RAMP_DRB, LOW);
	digitalWrite(RAMP_DRV, LOW);
}

/*
	0x00	stop
	0x01	dirt scoop
	0x02	raise/lower
	0x03	ramp
*/

void req()
{
	switch(cmd){
	  case 0x80:
		Wire.write(0x1F);
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
					scoop.mode=0;
					scoop.dir=0;
					break;
				  case 1:
					height.mode=0;
					height.dir=0;
					break;
				  case 2:
					ramp.mode=0;
					ramp.dir=0;
					break;
				}
			}else stop();
			break;
		  case 0x01:
			if(count>1){
				mode=1;
				scoop.mode=1;
				scoop.dir=(Wire.read()? 0x1:0x2);
				scoop.spd=Wire.read();
			}break;
		  case 0x02:
			if(count>1){
				mode=1;
				height.mode=1;
				height.dir=(Wire.read()? 0x1:0x2);
				height.spd=Wire.read();
			}break;
		  case 0x03:
			if(count>1){
				mode=1;
				ramp.mode=1;
				ramp.dir=(Wire.read()? 0x1:0x2);
				ramp.spd=Wire.read();
			}break;
		}while(Wire.available()) Wire.read();
	}
}
