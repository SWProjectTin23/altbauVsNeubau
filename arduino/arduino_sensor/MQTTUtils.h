#ifndef MQTTUTILS_H
#define MQTTUTILS_H

void mqttSetup();
bool mqttReconnect();
void mqttPublish(const char* topic, const char* payload);
void mqttLoop();

#endif
