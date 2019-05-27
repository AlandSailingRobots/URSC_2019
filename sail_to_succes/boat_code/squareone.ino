//Libraries

#include <SoftwareSerial.h>
#include <TinyGPS++.h>
#include <Wire.h>
#include <Servo.h>
#include <hmc6343.h>

TinyGPSPlus gps;
Servo servoMotorSail;
Servo servoMotorDirection;

hmc6343 hmc;
unsigned long TIMEOUT;
float heading, roll, pitch;    //Variables to store values returned from the HMC6343 library
String string = "";

char postCommand[] = "AT+HTTPPARA=\"URL\",\"robosailing.eu-north-1.elasticbeanstalk.com/dataTransfer/sensorData\""; //Url with endpoint where we send our sensordata

void setup()
{

  Serial.begin(9600);
  Serial1.begin(9600);

  initGsmModule(19200);
  
}

void loop()
{
  string = "";
  String a = sensorsInfo();
  performJsonPostRequest(a.c_str());

  Serial.println(string);
  int direction = (string.substring(46, 49)).toInt();
  int sail = (string.substring(49, 52)).toInt();
  float headingObjective = (string.substring(53, 56)).toInt();

  if (sail < 60 || sail > 120 || direction < 60 || direction > 120) {



  } else {

    servoMotorSail.attach(7);
    servoMotorDirection.attach(6);

    servoMotorSail.write(sail);
    servoMotorDirection.write(direction);
    

    TIMEOUT = millis();
    float difference=25;
    int correctCounter = 0;

    while ((correctCounter<10) && ((millis()- TIMEOUT) < 5000)) {
      hmc.readHeading(heading, roll, pitch);
      difference=abs(heading-headingObjective);
      if(difference < 20){
        correctCounter++;
      }
    }
    servoMotorDirection.write(90);
    delay(500);
    servoMotorDirection.detach();
    servoMotorSail.detach();
    
  }
}

String sensorsInfo()
{
  unsigned long start = millis();
  do
  {
    while (Serial1.available())
      gps.encode(Serial1.read());

  } while (millis() - start < 1000);

  String y =  (String)gps.date.year();
  char m[3];
  sprintf(m, "%02d", gps.date.month());
  char d[3];
  sprintf(d, "%02d", gps.date.day());
  char h[3];
  sprintf(h, "%02d", gps.time.hour());
  char mi[3];
  sprintf(mi, "%02d", gps.time.minute());
  char sec[3];
  sprintf(sec, "%02d", gps.time.second());

  String speed = (String)gps.speed.kmph();

  long lon = (long)(gps.location.lng() * 10000000);
  long lat = (long)(gps.location.lat() * 10000000);

  hmc.readHeading(heading, roll, pitch);
  String timestamp = "\"" + y + "-" + m + "-" + d + "T" + h + ":" + mi + ":" + sec + "Z\"";
  String json = "{\"created\":" + timestamp + ",\"latitude\":" + lat + ",\"longitude\":" + lon + ",\"direction\":11,\"gpsSpeed\":" + speed + ",\"compassHeading\":" + heading + "}";
  Serial.println(json);
  return json;

}

void initGsmModule(int baudRate) {
  Serial.print("Initializing Gsm Module...\n");
  Serial2.begin(baudRate);
  Serial.print("Disabe echo");
  Serial2.println("ATE0");//Disable module echomode
  wait("ERROR\r\n,OK\r\n", 5000);

  Serial.println("Setting up APN");
  Serial2.println("AT+SAPBR=3,1,\"APN\",\"internet\"");
  wait("ERROR\r\n,OK\r\n", 5000);
  Serial.print("Opening up bearer");
  Serial2.println("AT+SAPBR=1,1");
  wait("ERROR\r\n,OK\r\n", 5000);

  Serial.println("Initializing http session");
  Serial2.println("AT+HTTPINIT");//Initialize http session
  wait("ERROR\r\n,OK\r\n", 5000);

  Serial.println("Selecting bearer");
  Serial2.println("AT+HTTPPARA=\"CID\",1");//Selecting bearer
  wait("ERROR\r\n,OK\r\n", 5000);
  Serial.println("Selecting url");
  Serial2.println(postCommand);//Posting command that specifies the url
  wait("ERROR\r\n,OK\r\n", 5000);

  Serial.println("Setting request format");
  Serial2.println("AT+HTTPPARA=\"CONTENT\",\"application/json\"");//Setting request content to json format
  wait("ERROR\r\n,OK\r\n", 5000);
}

void performJsonPostRequest(char* jsonStr) {

  
  int strLength = strlen(jsonStr);
  Serial.println("Preparing to read json data");
  //Telling the module to read 'strLength' bytes of data with a timeout value
  Serial2.print("AT+HTTPDATA=");
  Serial2.print(strLength);
  Serial2.print(",");
  Serial2.println(120000);
  wait("ERROR\r\n,OK\r\n,DOWNLOAD\r\n", 5000);
  
  Serial.println("Entering json data");
  Serial2.println(jsonStr);//Send json data to module
  wait("ERROR\r\n,OK\r\n", 5000);
  Serial.println("Executing post request");
  Serial2.println("AT+HTTPACTION=1");//Setting the request action to 1=Post
  wait("ERROR\r\n,OK\r\n", 5000);

  delay(2000);
  Serial2.println("AT+HTTPREAD");//Reads respons from webserver
  saveRespons();
  Serial.println(string);
}

void saveRespons() {
  delay(600);
  char inChar;
  while (Serial2.available()) {
    inChar = Serial2.read();
    string += inChar;
  }
}

int16_t wait(char* Values, uint16_t timeout) {

  uint16_t Length = strlen(Values);

  char InputBuffer[Length + 1];
  strcpy(InputBuffer, Values);
  char CompareBuffer[Length + 1];
  memset(CompareBuffer, 0, sizeof(CompareBuffer));

  uint16_t Quantity = 1;

  for (int16_t n = 0; n < Length; n++) {
    if (InputBuffer[n] == ',')
      Quantity++;
  }

  char* InputTokens[Quantity];
  memset(InputTokens, 0, sizeof(InputTokens));
  char* CompareTokens[Quantity];
  memset(CompareTokens, 0, sizeof(CompareTokens));

  InputTokens[0] = InputBuffer;
  CompareTokens[0] = CompareBuffer;

  uint16_t TokenPosition = 1;
  for (int16_t n = 0; n < Length; n++) {
    if (InputBuffer[n] == ',') {
      InputBuffer[n] = 0;
      InputTokens[TokenPosition] = &InputBuffer[n + 1];
      CompareTokens[TokenPosition] = &CompareBuffer[n + 1];
      TokenPosition++;
    }
  }

  uint64_t timer = millis();
  char c;

  while (millis() - timer < timeout) {
    while (Serial2.available()) {
      c = Serial2.read();
      Serial.print(c);

      for (int16_t n = 0; n < Quantity; n++) {
        Length = strlen(CompareTokens[n]);
        if (c == InputTokens[n][Length])
          CompareTokens[n][Length] = c;
        else
          memset(CompareTokens[n], 0, Length);

        if (!strcmp(InputTokens[n], CompareTokens[n]))
          return n;
      }
    }
  }
  return -1;
}
