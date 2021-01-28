#include <Wire.h>
#define I2C_ADDR	0x09

#include "math.h"

#define NG	0//MQ-4 Methane natural gas sensor
#define LPG	1//MQ-6 LPG (propane + butane)
#define HYD	2//MQ-8 Hydrogen gas sensor
#define CO2	3//MQ-135 Carbon Dioxide

int LPGRaw;
int NGRaw;
int HYDRaw;
int LPGppm;
int NGppm;
int HYDppm;

byte cmd;

void setup()
{
	Wire.begin(I2C_ADDR);
	Wire.onReceive(recv);
	Wire.onRequest(req);
}

void loop()
{
	//Read analog value from each gas sensor 
	LPGRaw = analogRead(LPG);
	NGRaw = analogRead(NG);
	HYDRaw = analogRead(HYD);

	//Caclulate the PPM of each gas sensor using the funtions defined below           
	LPGppm = LPG_ppm(LPGRaw);
	NGppm = NG_ppm(NGRaw);
	HYDppm = HYD_ppm(HYDRaw);
}

//Calculate LPG PPM
int LPG_ppm(double rawValue)
{
	double ppm = 26.572*exp(1.2894*(rawValue*5.0/1024));//Convert voltage to ppm
	return ppm;
}
//Calculate NG PPM
int NG_ppm(double rawValue)
{
	double ppm = 10.938*exp(1.7742*(rawValue*5.0/1024));
	return ppm;
}
//Calculate HYD PPM
int HYD_ppm(double rawValue)
{
	double ppm = 3.027*exp(1.0698*(rawValue*5.0/1024));
	return ppm;
}

/*
	0x80	0x1F
	0x81	methane
	0x82	lpg
	0x83	hydrogen
	0x84	co2
*/

void req()
{
	switch(cmd){
	  case 0x80:
	  	Wire.write(0x1F);
		break;
	  case 0x81:
	  	Wire.write(NGppm);
		break;
	  case 0x82:
	  	Wire.write(LPGppm);
		break;
	  case 0x83:
	  	Wire.write(HYDppm);
		break;
	  case 0x84:
		break;
	}
}

void recv(int count)
{
	cmd=Wire.read();
}
