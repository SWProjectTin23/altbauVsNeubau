#include "TimeUtils.h"
#include <NTPClient.h>
#include <WiFiUdp.h>

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000); 

void setupTime() {
  timeClient.begin();

  while (!timeClient.update()) {
    timeClient.forceUpdate();
  }
}

unsigned long getUnixTime() {
  return timeClient.getEpochTime(); 
}
