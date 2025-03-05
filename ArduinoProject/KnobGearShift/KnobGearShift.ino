#include <Arduino.h>
#include "Arduino_GFX_Library.h"
#include "pin_config.h"

// DXQ120MYB2416A
Arduino_DataBus *bus = new Arduino_ESP32QSPI(
    SCREEN_CS /* CS */, SCREEN_SCLK /* SCK */, SCREEN_SDIO0 /* SDIO0 */,
    SCREEN_SDIO1 /* SDIO1 */, SCREEN_SDIO2 /* SDIO2 */, SCREEN_SDIO3 /* SDIO3 */);

Arduino_GFX *gfx = new Arduino_SH8601(bus, SCREEN_RST /* RST */, 0 /* rotation */,
                                      false /* IPS */, SCREEN_WIDTH, SCREEN_HEIGHT);

#define MESSAGE_GEAR_SHIFT "KNOB_GEAR_SHIFT::"

enum KNOB_State
{
    KNOB_NULL,
    KNOB_INCREMENT,
    KNOB_DECREMENT,
};

int encoder = 0;


bool KNOB_Trigger_Flag = false;
uint8_t KNOB_State_Flag = KNOB_State::KNOB_NULL;

//  0B000000[encoder_A][encoder_B]
uint8_t KNOB_Previous_Logical = 0B00000000;
size_t KNOB_CycleTime = 0;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Knob Gear Shift init.");

  pinMode(SCREEN_EN, OUTPUT);
  digitalWrite(SCREEN_EN, HIGH);

  pinMode(KNOB_DATA_A, INPUT_PULLUP);
  pinMode(KNOB_DATA_B, INPUT_PULLUP);
  pinMode(KNOB_KEY, INPUT_PULLUP);

  gfx->begin();
  gfx->fillScreen(CYAN);
  gfx->Display_Brightness(254);
  gfx->SetContrast(SH8601_ContrastOff);
  gfx->setTextColor(ORANGE);
  gfx->setTextSize(16);

}


char last_gear[2];
#define MESSAGE_KNOB_VALUE "KNOB_VALUE::"
#define MESSAGE_KNOB_ROTATE "KNOB_ROTATE::"
int knob_value = 0;

void loop() {
  
  if (millis() > KNOB_CycleTime)
  {
      KNOB_Logical_Scan_Loop();
      KNOB_CycleTime = millis() + 10; // 20ms
  }

  if (KNOB_Trigger_Flag == true)
  {
    KNOB_Trigger_Flag = false;
    switch (KNOB_State_Flag)
    {
    case KNOB_State::KNOB_INCREMENT:
        encoder++;
        knob_value++;
        Serial.printf("%s+\n", MESSAGE_KNOB_ROTATE);
        break;
    case KNOB_State::KNOB_DECREMENT:
        encoder--;
        knob_value--;
        Serial.printf("%s-\n", MESSAGE_KNOB_ROTATE);
        break;

    default:
        break;
    }

    Serial.printf("%s%d\n", MESSAGE_KNOB_VALUE, knob_value);

    encoder = encoder < 0 ? 0 : encoder;
    encoder = encoder > 24 ? 24 : encoder;    
    int idx = encoder / 5;

    
    const char *GEARS = "PRNDS";

    char gear = GEARS[idx];
    char gearStr[2];
    gearStr[0] = gear;
    gearStr[1] = '\0';

    // switch(idx){
    //   case 0:
    //     gfx->fillScreen(DARKGREY);
    //     break;
    //   case 1:
    //     gfx->fillScreen(PURPLE);
    //     break;
    //   case 2:
    //     gfx->fillScreen(NAVY);
    //     break;
    //   case 3:
    //     gfx->fillScreen(DARKGREEN);
    //     break;
    //   case 4:
    //     gfx->fillScreen(DARKCYAN);
    //     break;
    // }
    
    gfx->fillScreen(NAVY);
    if (strcmp(last_gear, gearStr)){
      strcpy(last_gear, gearStr);
      Serial.printf("%s%s\n", MESSAGE_GEAR_SHIFT, last_gear);
    }
    
    int16_t screenWidth = gfx->width();
    int16_t screenHeight = gfx->height();

    int16_t x1, y1;
    uint16_t w, h;

    gfx->setTextSize(18);
    gfx->getTextBounds(gearStr, 0, 0, &x1, &y1, &w, &h);

    int16_t x = (screenWidth - w) / 2;
    int16_t y = (screenHeight - h) / 2 - 15;
    

    gfx->setCursor(x, y);
    gfx->println(gearStr);

    char buff[5];
    snprintf(buff, 5, "%d", encoder);
    gfx->setTextSize(8);
    gfx-> getTextBounds(buff, 0,0, &x1, &y1, &w, &h);
    x = (screenWidth - w) / 2;
    y = screenHeight - h - 10;
    gfx->setCursor(x, y);
    gfx->println(buff);

  }
}


void KNOB_Logical_Scan_Loop(void)
{
    uint8_t KNOB_Logical_Scan = 0B00000000;

    if (digitalRead(KNOB_DATA_A) == 1)
    {
        KNOB_Logical_Scan |= 0B00000010;
    }
    else
    {
        KNOB_Logical_Scan &= 0B11111101;
    }

    if (digitalRead(KNOB_DATA_B) == 1)
    {
        KNOB_Logical_Scan |= 0B00000001;
    }
    else
    {
        KNOB_Logical_Scan &= 0B11111110;
    }

    if (KNOB_Previous_Logical != KNOB_Logical_Scan)
    {
        if (KNOB_Logical_Scan == 0B00000000 || KNOB_Logical_Scan == 0B00000011)
        {
            KNOB_Previous_Logical = KNOB_Logical_Scan;
            KNOB_Trigger_Flag = true;
        }
        else
        {
            if (KNOB_Logical_Scan == 0B00000010)
            {
                switch (KNOB_Previous_Logical)
                {
                case 0B00000000:
                    KNOB_State_Flag = KNOB_State::KNOB_INCREMENT;
                    break;
                case 0B00000011:
                    KNOB_State_Flag = KNOB_State::KNOB_DECREMENT;
                    break;

                default:
                    break;
                }
            }
            if (KNOB_Logical_Scan == 0B00000001)
            {
                switch (KNOB_Previous_Logical)
                {
                case 0B00000000:
                    KNOB_State_Flag = KNOB_State::KNOB_DECREMENT;
                    break;
                case 0B00000011:
                    KNOB_State_Flag = KNOB_State::KNOB_INCREMENT;
                    break;

                default:
                    break;
                }
            }
        }
        // delay(10);
    }
}






















