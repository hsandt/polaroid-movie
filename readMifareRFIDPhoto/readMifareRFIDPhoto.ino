/**************************************************************************/
/*! 
    @file     readMifare.pde
    @author   Adafruit Industries
	@license  BSD (see license.txt)

    This example will wait for any ISO14443A card or tag, and
    depending on the size of the UID will attempt to read from it.
   
    If the card has a 4-byte UID it is probably a Mifare
    Classic card, and the following steps are taken:
   
    - Authenticate block 4 (the first block of Sector 1) using
      the default KEYA of 0XFF 0XFF 0XFF 0XFF 0XFF 0XFF
    - If authentication succeeds, we can then read any of the
      4 blocks in that sector (though only block 4 is read here)
	 
    If the card has a 7-byte UID it is probably a Mifare
    Ultralight card, and the 4 byte pages can be read directly.
    Page 4 is read by default since this is the first 'general-
    purpose' page on the tags.


This is an example sketch for the Adafruit PN532 NFC/RFID breakout boards
This library works with the Adafruit NFC breakout 
  ----> https://www.adafruit.com/products/364
 
Check out the links above for our tutorials and wiring diagrams 
These chips use SPI or I2C to communicate.

Adafruit invests time and resources providing this open source code, 
please support Adafruit and open-source hardware by purchasing 
products from Adafruit!

Code modified by hsandt to send signal when losing RFID tag and detecting
when photoresistors are covered too.

*/
/**************************************************************************/

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

// If using the breakout with SPI, define the pins for SPI communication.
#define PN532_SCK  (2)
#define PN532_MOSI (3)
#define PN532_SS   (4)
#define PN532_MISO (5)

// If using the breakout or shield with I2C, define just the pins connected
// to the IRQ and reset lines.  Use the values below (2, 3) for the shield!
#define PN532_IRQ   (2)
#define PN532_RESET (3)  // Not connected by default on the NFC Shield

// Uncomment just _one_ line below depending on how your breakout or shield
// is connected to the Arduino:

// Use this line for a breakout with a software SPI connection (recommended):
//Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

// Use this line for a breakout with a hardware SPI connection.  Note that
// the PN532 SCK, MOSI, and MISO pins need to be connected to the Arduino's
// hardware SPI SCK, MOSI, and MISO pins.  On an Arduino Uno these are
// SCK = 13, MOSI = 11, MISO = 12.  The SS line can be any digital IO pin.
Adafruit_PN532 nfc(PN532_SS);

// Or use this line for a breakout or shield with an I2C connection:
//Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

#if defined(ARDUINO_ARCH_SAMD)
// for Zero, output on USB Serial console, remove line below if using programming port to program the Zero!
// also change #define in Adafruit_PN532.cpp library file
   #define Serial SerialUSB
#endif

// ADDED
// interval between consecutive RFID presence checks in ms (excluding maxRetries / timeout of readPassiveTargetID itself)
int detectionInterval = 200;
// max tries for RFID detection (from 0x01 to 0xFE, around 0s to 1s)
int maxTries = 0x10;

// ADDED: photo input pins, in order 1-2-3
int photoInputs[] = {8, 7, 2};

void setup(void) {

  /* RFID setup */
  
  #ifndef ESP8266
    while (!Serial); // for Leonardo/Micro/Zero
  #endif
  Serial.begin(115200);
  Serial.println("Hello!");

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC); 
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);

  // ADDED
  // Set the max number of retry attempts to read from a card
  // This prevents us from waiting forever for a card, which is
  // the default behaviour of the PN532.
  // Use any uint8_t value inferior to 0xFF, the lower the value the shorter the timeout (around 0s to 1s for 0xFE)
  nfc.setPassiveActivationRetries(maxTries);
  
  // configure board to read RFID tags
  nfc.SAMConfig();
  
  Serial.println("Waiting for an ISO14443A Card ...");

  /* PHOTORESISTOR setup */

  pinMode(photoInputs[0], INPUT);
  pinMode(photoInputs[1], INPUT);
  pinMode(photoInputs[2], INPUT);
  
}


void loop(void) {

  /* RFID variables */
  
  // ADDED: static variables keep data to remember: previously detected RFID and Photoresistor covered
  static bool rfidDetected = false;
  static uint8_t lastRfidUid[] = { 0, 0, 0, 0, 0, 0, 0 };
  
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
  uint8_t success;

  /* PHOTORESISTOR variables */
  
  static bool photoDetected[3] = {false, false, false};  // all photoresistors uncovered

  /* READ NFC */
  
  // Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
  // 'uid' will be populated with the UID, and uidLength will indicate
  // if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  /* RFID detection */
  
  if (success)
  {
//    Serial.println("success");
    bool change = false;

    if (rfidDetected)
    {
      // an RFID was detected last frame, has it changed?
      bool sameUid = true;
      for (int i = 0; i < uidLength; ++i) {
        if (uid[i] != lastRfidUid[i]) {
          sameUid = false;
          break;
        }
      }
      
      if (!sameUid)
      {
        change = true;
        // new RFID detected, you may send message to indicate that previous RFID was lost
        // since our Python code on computer-side will replace old video with new video immediately, we do not need this message
//        Serial.print("Lost UID Value: ");
//        nfc.PrintHex(lastRfidUid, uidLength);  // we assume we only use one kind of RFID; else, create another variable to store last RFID UID length
//        Serial.println("");
//        Serial.println("Immediate switch to new RFID");
      }
    }
    else
    {
      // if no RFID before, always considered as a change
      rfidDetected = true;
      change = true;
    }

    if (change) {
    
      for (int i = 0; i < uidLength; ++i) {
          lastRfidUid[i] = uid[i];
      }
      
      // Display some basic information about the card
      Serial.println("Found an ISO14443A card");
      Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
      Serial.print("  UID Value: ");
      nfc.PrintHex(uid, uidLength);
      Serial.println("");
      
      if (uidLength == 4)
      {
        // We probably have a Mifare Classic card ... 
        Serial.println("Seems to be a Mifare Classic card (4 byte UID)");
  	  
        // Now we need to try to authenticate it for read/write access
        // Try with the factory default KeyA: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
        Serial.println("Trying to authenticate block 4 with default KEYA value");
        uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
  	  
  	  // Start with block 4 (the first block of sector 1) since sector 0
  	  // contains the manufacturer data and it's probably better just
  	  // to leave it alone unless you know what you're doing
        success = nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, keya);
  	  
        if (success)
        {
          Serial.println("Sector 1 (Blocks 4..7) has been authenticated");
          uint8_t data[16];
  		
          // If you want to write something to block 4 to test with, uncomment
  		// the following line and this text should be read back in a minute
          //memcpy(data, (const uint8_t[]){ 'a', 'd', 'a', 'f', 'r', 'u', 'i', 't', '.', 'c', 'o', 'm', 0, 0, 0, 0 }, sizeof data);
          // success = nfc.mifareclassic_WriteDataBlock (4, data);
  
          // Try to read the contents of block 4
          success = nfc.mifareclassic_ReadDataBlock(4, data);
  		
          if (success)
          {
            // Data seems to have been read ... spit it out
            Serial.println("Reading Block 4:");
            nfc.PrintHexChar(data, 16);
            Serial.println("");
  		  
            // Wait a bit before reading the card again
            delay(detectionInterval);
          }
          else
          {
            Serial.println("Ooops ... unable to read the requested block.  Try another key?");
          }
        }
        else
        {
          Serial.println("Ooops ... authentication failed: Try another key?");
        }
      }
      
      if (uidLength == 7)
      {
        // We probably have a Mifare Ultralight card ...
        Serial.println("Seems to be a Mifare Ultralight tag (7 byte UID)");
  	  
        // Try to read the first general-purpose user page (#4)
        Serial.println("Reading page 4");
        uint8_t data[32];
        success = nfc.mifareultralight_ReadPage (4, data);
        if (success)
        {
          // Data seems to have been read ... spit it out
          nfc.PrintHexChar(data, 4);
          Serial.println("");
  		
          // Wait a bit before reading the card again
          delay(detectionInterval);
        }
        else
        {
          Serial.println("Ooops ... unable to read the requested page!?");
        }
      }
    } // end if change
  } // end if success
  else
  {
//    Serial.println("NO success");
    
    // ADDED: if no RFID detected but an RFID was detected in the last frame (1s ago), send message in serial port to tell it
    if (rfidDetected) {
      Serial.print("Lost UID Value: ");
      nfc.PrintHex(lastRfidUid, uidLength);
      Serial.println("");
      Serial.flush();
      rfidDetected = false;
      // keeping old uid is fine, but remember it is meaningless until next RFID comes
    }
  }

  /* PHOTORESISTOR detection */

  for (int i = 0; i < 3; ++i) {
    if (photoDetected[i] && digitalRead(photoInputs[i]) == LOW) {
      photoDetected[i] = false;
      Serial.print("Lost Photo: ");
      Serial.println(i+1);
    } else if (!photoDetected[i] && digitalRead(photoInputs[i]) == HIGH) {
      photoDetected[i] = true;
      Serial.print("Photo: ");
      Serial.println(i+1);
    } else {
//      Serial.print("no change for ");
//      Serial.println(i+1);
    }
  }
  
}

