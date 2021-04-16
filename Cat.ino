#include <OneWire.h> //Temp & DO
#include <EEPROM.h>  //TDS & Conductivity
#include "GravityTDS.h" //TDS
#include "DFRobot_EC10.h" //Conductivity

//----------------TEMP--------------------
int TempSensorPin = 2; //DS18S20 Signal pin on digital 2
//Temperature chip i/o
OneWire ds(TempSensorPin);  // on digital pin 2
float temperature;

//----------------PH-----------------------
#define pHSensorPin 2        //pH meter Analog output to Arduino Analog Input 0
unsigned long int avgValue;  //Store the average value of the sensor feedback
float b;
int buf[10],temp;
float ph;

//----------------TURBIDITY----------------
#define TurbiditySensorPin A1
float turbidity;

//---------------TDS-----------------------
#define TdsSensorPin A4
GravityTDS gravityTds;
float tdsValue = 0;

//----------------CONDUCTIVITY------------
#define ConductivityPin A3
float voltageEC,ecValue;
DFRobot_EC10 ec;

//-------------DO-------------------------
#define DO_PIN A0

#define VREF 5000    //VREF (mv)
#define ADC_RES 1024 //ADC Resolution

//Single-point calibration Mode=0
//Two-point calibration Mode=1
#define TWO_POINT_CALIBRATION 1

#define READ_TEMP (25) //Current water temperature ℃, Or temperature sensor function!!!!!!!!!!!!!!!!!!!!!!!!!!

//Single point calibration needs to be filled CAL1_V and CAL1_T
#define CAL1_V (1928) //mv
#define CAL1_T (25)   //℃
//Two-point calibration needs to be filled CAL2_V and CAL2_T
//CAL1 High temperature point, CAL2 Low temperature point
#define CAL2_V (1300) //mv
#define CAL2_T (15)   //℃

const uint16_t DO_Table[41] = {
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410};

uint8_t Temperaturet;
uint16_t ADC_Raw;
uint16_t ADC_Voltage;
uint16_t DO;

int16_t readDO(uint32_t voltage_mv, uint8_t temperature_c)
{
#if TWO_POINT_CALIBRATION == 0
  uint16_t V_saturation = (uint32_t)CAL1_V + (uint32_t)35 * temperature_c - (uint32_t)CAL1_T * 35;
  return (voltage_mv * DO_Table[temperature_c] / V_saturation);
#else
  uint16_t V_saturation = (int16_t)((int8_t)temperature_c - CAL2_T) * ((uint16_t)CAL1_V - CAL2_V) / ((uint8_t)CAL1_T - CAL2_T) + CAL2_V;
  return (voltage_mv * DO_Table[temperature_c] / V_saturation);
#endif
}


void setup(void) {

for(byte i = 0;i< 8; i++ ){///////////////////////////////////////////////////////////////////////////////7här har jag fibblat
      EEPROM.write(0x0F+i, 0xFF);
    }
  
  Serial.begin(9600); 
  
  //----------------TDS-------------------
   gravityTds.setPin(TdsSensorPin);
   gravityTds.setAref(5.0);  //reference voltage on ADC, default 5.0V on Arduino UNO
   gravityTds.setAdcRange(1024);  //1024 for 10bit ADC;4096 for 12bit ADC
   gravityTds.begin();  //initialization
  //--------------CONDUCTIVITY------------
   ec.begin();
  }

void loop(void) {

    //int fromPI = 0;
    //if(Serial.available() > 0){
      //fromPI = Serial.read(); //detta ger oss vårt case.
      //}
      delay(100);
      int fromPI = (int)'6';
  switch (fromPI) {
    case '1': //TEMP
      temperature = getTemp();
      Serial.println(temperature);
      
      break;
      
    case '2': //pH
      ph = getpH();
      Serial.println(ph,2);
      
      break;
      
    case '3': //TURBIDITY
      turbidity = getTurbidity();
      Serial.println(turbidity); // print out the value you read
      Serial.println(" NTU");
      break;
    
    case '4': //TDS
      
      temperature = getTemp();  //make sure the temp is measured
      Serial.println(temperature);
      gravityTds.setTemperature(temperature);  // set the temperature and execute temperature compensation
      gravityTds.update();  //sample and calculate 
      tdsValue = gravityTds.getTdsValue();  // then get the value
      Serial.println(tdsValue,2);
      Serial.println("ppm");
    
      break;
      
    case '5': //CONDUCTIVITY
  
        static unsigned long timepoint = millis();
      if(millis()-timepoint>1000U)  //time interval: 1s
      {
        timepoint = millis();
        voltageEC = analogRead(ConductivityPin)/1024.0*5000;  // read the voltage
        //Serial.print("Conductivity: \nvoltage:");
        Serial.println(voltageEC);
        temperature = getTemp();  //make sure the temp is measured
        ecValue =  ec.readEC(voltageEC,temperature);  // convert voltage to EC with temperature compensation
        Serial.print("V \nEC:");
        Serial.println(ecValue,1);
        Serial.println("ms/cm");
      }
      ec.calibration(voltageEC,temperature);  // calibration process by Serail CMD
      
      break;
      
    case '6'://DO
      Temperaturet = (uint8_t)getTemp();//läs temp ist
      ADC_Raw = analogRead(DO_PIN);
      ADC_Voltage = uint32_t(VREF) * ADC_Raw / ADC_RES;

      Serial.print("Temperaturet:\t" + String(Temperaturet) + "\t");
      Serial.print("ADC RAW:\t" + String(ADC_Raw) + "\t");
      Serial.print("ADC Voltage:\t" + String(ADC_Voltage) + "\t");
      Serial.println("DO:\t" + String(readDO(ADC_Voltage, Temperaturet)) + "\t");
      break;
      
    case 'H':
      Serial.println("C");
      break;
      
    default:
      break;
     
  }
}

/** Returns the temperature from one DS18S20 in DEG Celsius.
 * 
 */
float getTemp(){

    byte data[12];
    byte addr[8];
  
    if ( !ds.search(addr)) {
        //no more sensors on chain, reset search
        ds.reset_search();
        return -1000;
    }
  
    if ( OneWire::crc8( addr, 7) != addr[7]) {
        //Serial.println("CRC is not valid!");
        return -1000;
    }
  
    if ( addr[0] != 0x10 && addr[0] != 0x28) {
        //Serial.print("Device is not recognized");
        return -1000;
    }
  
    ds.reset();
    ds.select(addr);
    ds.write(0x44,1); // start conversion, with parasite power on at the end
  
    byte present = ds.reset();
    ds.select(addr);    
    ds.write(0xBE); // Read Scratchpad
  
    delay(500);
    for (int i = 0; i < 9; i++) { // we need 9 bytes
      data[i] = ds.read();
    }
    
    ds.reset_search();
    
    byte MSB = data[1];
    byte LSB = data[0];
  
    float tempRead = ((MSB << 8) | LSB); //using two's compliment
    float TemperatureSum = tempRead / 16;
    
    return TemperatureSum;
  
}

float getpH(){
  
      for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
    { 
      buf[i]=analogRead(pHSensorPin);
      delay(10);
      //i.7
    }
    for(int i=0;i<9;i++)        //sort the analog from small to large
    {
      for(int j=i+1;j<10;j++)
      {
        if(buf[i]>buf[j])
        {
          temp=buf[i];
          buf[i]=buf[j];
          buf[j]=temp;
        }
      }
    }
    avgValue=0;
    for(int i=2;i<8;i++)                      //take the average value of 6 center sample
      avgValue+=buf[i];
    float phValue=(float)avgValue*5.0/1024/6; //convert the analog into millivolt
    phValue=3.5*phValue;                      //convert the millivolt into pH value

 //   phValue = 
      
    return phValue;
  }

float getTurbidity(){
    
    int turbiditySensorValue = analogRead(TurbiditySensorPin);// read the input on analog pin 2:
    float voltage = turbiditySensorValue * (5.0 / 1024.0); // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  //Here we need to convert it to NTU
    voltage = (-1)*1120.4*voltage*voltage + 5742.3*voltage - 4352.9;
    return voltage;
    }
