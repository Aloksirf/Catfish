#include <OneWire.h> //Temp & DO

//----------------TEMP--------------------
int TempSensorPin = 2; //DS18S20 Signal pin on digital 2
//Temperature chip i/o
OneWire ds(TempSensorPin);  // on digital pin 2
float temperature;

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

//----------------TURBIDITY----------------
#define TurbiditySensorPin A1
float turbidity;


void setup() {
  
  
  
  Serial.begin(9600); 
}

void loop() {
    /**int temp;
    int turbidity;
    int dissO;*/
    int fromPI = 0;
    if(Serial.available() > 0){
      fromPI = Serial.read(); //detta ger oss vårt case.
    }
      delay(100);
      
  switch (fromPI) {
    case '1': //TEMP
      temperature = getTemp();
      Serial.println(temperature);
      
      break;
      
    case '2': //Dissolved oxygen
      Temperaturet = (uint8_t)getTemp();//läs temp ist
      ADC_Raw = analogRead(DO_PIN);
      ADC_Voltage = uint32_t(VREF) * ADC_Raw / ADC_RES;

      Serial.print("Temperaturet:\t" + String(Temperaturet) + "\t");
      Serial.print("ADC RAW:\t" + String(ADC_Raw) + "\t");
      Serial.print("ADC Voltage:\t" + String(ADC_Voltage) + "\t");
      Serial.println("DO:\t" + String(readDO(ADC_Voltage, Temperaturet)) + "\t");
      
      break;
      
    case '3': //TURBIDITY
      turbidity = getTurbidity();
      Serial.println(turbidity); // print out the value you read
      break;
          
    case 72: //H is 72
      Serial.println("F");
      break;
      
    default:
      break;
     
  }
}

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

float getTurbidity(){
    
    int turbiditySensorValue = analogRead(TurbiditySensorPin);// read the input on analog pin 2:
    float voltage = turbiditySensorValue * (5.0 / 1024.0); // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  //Here we need to convert it to NTU
    voltage = (-1)*1120.4*voltage*voltage + 5742.3*voltage - 4352.9;
    return voltage;
    }
