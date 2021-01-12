# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# GPIO
import board
import adafruit_dht
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# MQTT
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a3093y4vxcaaya-ats.iot.ap-northeast-1.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERT = "certificates/a362f0b2c7-certificate.pem.crt"
PATH_TO_KEY = "certificates/a362f0b2c7-private.pem.key"
PATH_TO_ROOT = "certificates/root.pem"
TOPIC = "test/testing"
RANGE = 9999

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.

print('Begin Publish')
#for i in range (RANGE):
i = 0
humidity = 0
clientId="rasberrypi01"
while i < RANGE:
  try:
  ### Temp/Humidity Get
    #temperature_c = dhtDevice.temperature
    humidity = None
    humidity = dhtDevice.humidity
  ###
    print(type(humidity))
    message = {
            "clientId" : clientId,
            "humidity" : humidity
            }
    print("::: {:03} :::".format(i))
    print(message)
    if humidity is not None:
      mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
      print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
      i += 1
  except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        t.sleep(1.0)
        continue
  except Exception as error:
        dhtDevice.exit()
        raise error
  t.sleep(1.0)
print('Publish End')

disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
