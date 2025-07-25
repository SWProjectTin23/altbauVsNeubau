#include "TimeUtils.h"
#include <NTPClient.h>
#include <WiFiUdp.h>

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000); // UTC, Update alle 60 Sek

void setupTime() {
  timeClient.begin();

  // Warten, bis Zeit geladen wurde
  while (!timeClient.update()) {
    timeClient.forceUpdate();
  }
}

unsigned long getUnixTime() {
  return timeClient.getEpochTime(); // UNIX Timestamp (z. B. 1753098733)
}
