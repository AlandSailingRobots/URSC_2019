#!/usr/bin/env python3
import paho.mqtt.client as mqtt
def getWindDirection(inputString):
	output = str('')
	for char in inputString[15:18]:
		if char in '1234567890':
			output += char
	return output

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("weather")
	client.username_pw_set("yirnfmrp", "yhxQJ-e_JUMg")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(getWindDirection(str(msg.payload)))
	#print(message)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("m24.cloudmqtt.com", 14846, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
