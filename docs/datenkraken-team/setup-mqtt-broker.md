To create a user with a password install mosquitto and execute the following command

Go into the mqtt-broker folder and create the passwd file
```
touch passwd
```
Write the username and the password to the file
```
mosquitto_passwd -b passwd myuser mypassword```
