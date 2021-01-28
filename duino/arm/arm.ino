/**/

#include <Wire.h>
#define I2C_ADDR	0x04

//pins
#define	BASE_DRA	4
#define	BASE_DRB	5
#define	BASE_DRV	6

#define	SHOULD_DRA	13
#define	SHOULD_DRB	12
#define	SHOULD_DRV	11

#define	ELBOW_DRA	3
#define	ELBOW_DRB	2
#define	ELBOW_DRV	10

typedef unsigned long dword;
typedef struct{
	byte mode;//0:stopped, 1:continuous
	byte dir;//0:brake, 1:ccw(B->A), 2:cw(A->B), 3:brake
	byte spd;//0-255
} motor;

char mode=0;//0:stopped, 1:per-motor
motor base, should, elbow;
byte cmd=0x00;

void setup()
{
	pinMode(BASE_DRA, OUTPUT);
	pinMode(BASE_DRB, OUTPUT);
	pinMode(BASE_DRV, OUTPUT);
	
	pinMode(SHOULD_DRA, OUTPUT);
	pinMode(SHOULD_DRB, OUTPUT);
	pinMode(SHOULD_DRV, OUTPUT);
	
	pinMode(ELBOW_DRA, OUTPUT);
	pinMode(ELBOW_DRB, OUTPUT);
	pinMode(ELBOW_DRV, OUTPUT);
	
	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);
}

void loop()
{
	if(mode>0){
		switch(base.mode){
		  case 1:
			break;
		  default:
			base.spd=0;
			base.dir=0;
			break;
		}
		switch(should.mode){
		  case 1:
			break;
		  default:
			should.spd=0;
			should.dir=0;
			break;
		}
		switch(elbow.mode){
		  case 1:
			break;
		  default:
			elbow.spd=0;
			elbow.dir=0;
			break;
		}
		
		digitalWrite(BASE_DRA, base.dir&0x2);
		digitalWrite(BASE_DRB, base.dir&0x1);
		analogWrite(BASE_DRV, base.spd);
		
		digitalWrite(SHOULD_DRA, should.dir&0x2);
		digitalWrite(SHOULD_DRB, should.dir&0x1);
		analogWrite(SHOULD_DRV, should.spd);
		
		digitalWrite(ELBOW_DRA, elbow.dir&0x2);
		digitalWrite(ELBOW_DRB, elbow.dir&0x1);
		analogWrite(ELBOW_DRV, elbow.spd);
	}
}

void stop()
{
	mode=0;
	base.mode=0;
	should.mode=0;
	elbow.mode=0;
	
	pinMode(BASE_DRV, OUTPUT);
	digitalWrite(BASE_DRA, LOW);
	digitalWrite(BASE_DRB, LOW);
	digitalWrite(BASE_DRV, LOW);
	
	pinMode(SHOULD_DRV, OUTPUT);
	digitalWrite(SHOULD_DRA, LOW);
	digitalWrite(SHOULD_DRB, LOW);
	digitalWrite(SHOULD_DRV, LOW);
	
	pinMode(ELBOW_DRV, OUTPUT);
	digitalWrite(ELBOW_DRA, LOW);
	digitalWrite(ELBOW_DRB, LOW);
	digitalWrite(ELBOW_DRV, LOW);
}

/*
	WRITE:
		0x00	stop/stop one
		0x01	run base
		0x02	... should
		0x03	... elbow
		0x04
	READ:
		0x80	0x1F
		0x81	base mode
		0x82	...
		0x83	...
		0x84
		0x85	base spd/dir
		0x86	...
		0x87	...
		0x88
		0x89
		0x8A
		0x8B
		0x8C
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
		Wire.write(base.mode);
		break;
	  case 0x82:
		Wire.write(should.mode);
		break;
	  case 0x83:
		Wire.write(elbow.mode);
		break;
	  case 0x85:
		Wire.write(base.dir);
		Wire.write(base.spd);
		break;
	  case 0x86:
		Wire.write(base.dir);
		Wire.write(base.spd);
		break;
	  case 0x87:
		Wire.write(base.dir);
		Wire.write(base.spd);
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
					base.mode=0;
					base.dir=0;
					break;
				  case 1:
					should.mode=0;
					should.dir=0;
					break;
				  case 2:
					elbow.mode=0;
					elbow.dir=0;
					break;
				}
			}else stop();
			break;
		  case 0x01:
			if(count>1){
				mode=1;
				base.mode=1;
				base.dir=(Wire.read()? 0x1:0x2);
				base.spd=Wire.read();
			}break;
		  case 0x02:
			if(count>1){
				mode=1;
				should.mode=1;
				should.dir=(Wire.read()? 0x1:0x2);
				should.spd=Wire.read();
			}break;
		  case 0x03:
			if(count>1){
				mode=1;
				elbow.mode=1;
				elbow.dir=(Wire.read()? 0x1:0x2);
				elbow.spd=Wire.read();
			}break;
		}while(Wire.available()) Wire.read();
	}
}
