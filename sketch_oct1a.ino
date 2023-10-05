const byte numBytes = 12;  // Adjust based on the expected length of your data
char receivedData[numBytes];
boolean newData = false;
char delimiter = ',';  // Delimiter used to separate values

// sends ten channels of PPM by bit banging.

int ch1 = 1500;       // initial values
int ch2 = 1500;
int ch3 = 1500;
int ch4 = 1500;
int ch5 = 1500;
int ch6 = 1500;

int channelOutPort = 2;

void setup() {
  pinMode(channelOutPort, OUTPUT);       // PPM output pin
  Serial.begin(9600);
}

struct ParsedData {
  int value1;
  int value2;
};

ParsedData parsedValues;

void loop() {
  recvWithEndMarker();
  if (newData) {
    parseData();
    newData = false;
    //ch1 = parsedValues.value1;
    //ch2 = parsedValues.value2;
    //ch3 = parsedValues.value2;
    Serial.print(parsedValues.value1+'\n');
  }
  /*
  ch1 = analogRead(A0);          // read analog sticks
  ch1 = map(ch1, 0,1023,1000,2000);
  ch2 = analogRead(A1);
  ch2 = map(ch2, 0,1023,1000,2000);
  ch3 = analogRead(A2);
  ch3 = map(ch3, 0,1023,1000,2000);
  ch4 = analogRead(A3);
  ch4 = map(ch4, 0,1023,1000,2000);
  ch5 = analogRead(A4);
  ch5 = map(ch5, 0,1023,1000,2000);
  ch6 = analogRead(A5);
  ch6 = map(ch6, 0,1023,1000,2000);
  */
  digitalWrite(channelOutPort, HIGH);
  delayMicroseconds(500);       // pulse
  digitalWrite(channelOutPort, LOW);
  delayMicroseconds(ch1-500);   // gap for the remaining period
  
  digitalWrite(channelOutPort, HIGH);        
  delayMicroseconds(500);
  digitalWrite(channelOutPort, LOW);     
  delayMicroseconds(ch2-500);   
  
  digitalWrite(channelOutPort, HIGH);        
  delayMicroseconds(500); 
  digitalWrite(channelOutPort, LOW);      
  delayMicroseconds(ch3-500);   

  digitalWrite(channelOutPort, HIGH);
  delayMicroseconds(500);  
  digitalWrite(channelOutPort, LOW);      
  delayMicroseconds(ch4-500);   

  digitalWrite(channelOutPort, HIGH);        
  delayMicroseconds(500);
  digitalWrite(channelOutPort, LOW);        
  delayMicroseconds(ch5-500);   

  digitalWrite(channelOutPort, HIGH);          // ch6 
  delayMicroseconds(500);
  digitalWrite(channelOutPort, LOW);      
  delayMicroseconds(ch6-500);

  digitalWrite(channelOutPort, HIGH);          // ch7 
  delayMicroseconds(500);
  digitalWrite(channelOutPort, LOW);      
  delayMicroseconds(1000-500);

  digitalWrite(channelOutPort, HIGH);          // ch8 
  delayMicroseconds(500);
  digitalWrite(channelOutPort, LOW);      
  delayMicroseconds(1100-500);

  digitalWrite(channelOutPort, HIGH);          // sync pulse
  delayMicroseconds(500);
  digitalWrite(channelOutPort, LOW);
  delayMicroseconds(5000);        // longer gap 
}

void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();
    if (rc != endMarker) {
      receivedData[ndx] = rc;
      ndx++;
      if (ndx >= numBytes) {
        ndx = numBytes - 1;
      }
    } else {
      receivedData[ndx] = '\0';  // Null-terminate the string
      ndx = 0;
      newData = true;
    }
  }
}

void parseData() {
  char *value1Str;
  char *value2Str;

  // Parse the received data based on the delimiter
  value1Str = strtok(receivedData, ",");
  value2Str = strtok(NULL, ",");

  if (value1Str != NULL && value2Str != NULL) {
    // Convert the string values to integers
    parsedValues.value1 = atoi(value1Str);
    parsedValues.value2 = atoi(value2Str);
  }
}
