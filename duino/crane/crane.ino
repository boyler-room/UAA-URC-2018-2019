#include <Wire.h>
#define I2C_ADDR	0x06

#define X_DIR	2
#define X_DRV	3
#define Y_DIR	4
#define Y_DRV	5
#define Z_DIR	6
#define Z_DRV	7

#define SCOOP_S	9

unsigned int speed_T=2000;//us per step
bool stepX,stepY,stepZ;
bool dirX,dirY,dirZ;
byte cmd;

void setup()
{
	pinMode(X_DIR,OUTPUT);
	pinMode(X_DRV,OUTPUT);
	pinMode(Y_DIR,OUTPUT);
	pinMode(Y_DRV,OUTPUT);
	pinMode(Z_DIR,OUTPUT);
	pinMode(Z_DRV,OUTPUT);

	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);
}

void loop()
{
	if(stepX) onestep(X_DRV);
	if(stepY) onestep(Y_DRV);
	if(stepZ) onestep(Z_DRV);
	delayMicroseconds(speed_T);
}

void onestep(int pin)
{
	digitalWrite(pin,HIGH);
	delayMicroseconds(100);
	digitalWrite(pin,LOW);
	delayMicroseconds(100);
}

void dirset(int pin)
{
	if(pin==X_DIR) digitalWrite(pin,dirX);
	if(pin==Y_DIR) digitalWrite(pin,dirY);
	if(pin==Z_DIR) digitalWrite(pin,dirZ);
}

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
	cmd=Wire.read();
	switch(cmd){
	  case 0x00:
		if(--count){
			switch(Wire.read()){
			  case 0:
				stepX=0;
				break;
			  case 1:
				stepY=0;
				break;
			  case 2:
				stepZ=0;
				break;
			}
		}else{
			stepX=0;
			stepY=0;
			stepZ=0;
		}break;
	  case 0x01:
		if(--count){
			dirX=!!Wire.read();
			dirset(X_DIR);
		}stepX=1;
		break;
	  case 0x02:
		if(--count){
			dirY=!!Wire.read();
			dirset(Y_DIR);
		}stepY=1;
		break;
	  case 0x03:
		if(--count){
			dirZ=!!Wire.read();
			dirset(Z_DIR);
		}stepZ=1;
		break;
	}while(Wire.available()) Wire.read();
}
