#include <Servo.h>

#include <Wire.h>
#define I2C_ADDR	0x0A

#define LED_ACTIVE	3
#define LED_FOUND	2

#define SRV_TILT	10
#define SRV_SCAN	9
#define TURN_ZERO	89

byte cmd;

Servo tilt,scan;
bool led_a,led_f;

void setup()
{
	tilt.attach(SRV_TILT,900,2100);
	scan.attach(SRV_SCAN,800,2200);

	tilt.write(90);
	scan.write(TURN_ZERO);
	
	pinMode(LED_ACTIVE, OUTPUT);
	pinMode(LED_FOUND, OUTPUT);
	
	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);

	delay(500);
}

void loop()
{
	digitalWrite(LED_ACTIVE,led_a);
	digitalWrite(LED_FOUND,led_f);
}

/*
	0x00	reset/stop
	0x01	toggle active led
	0x02	toggle found led
	0x03	run tilt: pos
	0x04	run scan: dir(l,n,r)

	0x80	0x1F
*/

void req()
{
	switch(cmd)
	{
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
		tilt.write(90);
		scan.write(TURN_ZERO);
		led_a=led_f=0;
		break;
	  case 0x01:
		led_a=!led_a;
		break;
	  case 0x02:
		led_f=!led_f;
		break;
	  case 0x03:
		if(Wire.available()) tilt.write(Wire.read());
		break;
	  case 0x04:
		if(Wire.available()){
			byte d=Wire.read();
			if(d&0x80) scan.write(86);
			else if(d) scan.write(90);
			else scan.write(TURN_ZERO);
		}break;
	}while(Wire.available()) Wire.read();
}
