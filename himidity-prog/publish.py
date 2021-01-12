# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# System
import os, sys, json, yaml
import time as t

# GPIO
import board
import adafruit_dht
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# MQTT
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

# Log setting
from logging import basicConfig, getLogger, DEBUG
basicConfig(level=DEBUG)
logger = getLogger( "<" + __file__ + ">")

# Configfile load
def config_load(path):
    if(os.path.isfile(path)):
        with open(path, "r") as obj:
            config = json.load(obj)
            logger.debug("Config Load Success <%s>" % path)
    else:
        logger.error("Config load error <%s>" % path)
        sys.exit()
    
    awsconfig = dict(
            ENDPOINT = config["ENDPOINT"],
            CLIENT_ID = config["CLIENT_ID"],
            PATH_TO_CERT = config["PATH_TO_CERT"],
            PATH_TO_KEY = config["PATH_TO_KEY"],
            PATH_TO_ROOT = config["PATH_TO_ROOT"],
            TOPIC = config["TOPIC"],
            RANGE = config["RANGE"]
        )
    return awsconfig
    

def main():
    logger.info("/_/_/_/Start Program/_/_/_/")
    # config load
    path = "config.json"
    awsconfig = config_load(path)

    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=awsconfig["ENDPOINT"],
                cert_filepath=awsconfig["PATH_TO_CERT"],
                pri_key_filepath=awsconfig["PATH_TO_KEY"],
                client_bootstrap=client_bootstrap,
                ca_filepath=awsconfig["PATH_TO_ROOT"],
                client_id=awsconfig["CLIENT_ID"],
                clean_session=False,
                keep_alive_secs=6
                )
    logger.info("Connecting to {} with client ID '{}'...".format(awsconfig["ENDPOINT"], awsconfig["CLIENT_ID"]))
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    logger.info("/_/_/_/Connected!/_/_/_/")
    logger.info("/_/_/_/Begin Publish/_/_/_/")
    i = 0
    while True:
        try:
            ### Temp/Humidity Get
            #temperature_c = dhtDevice.temperature
            humidity = None
            humidity = dhtDevice.humidity
            message = {
                    "clientId" : awsconfig["CLIENT_ID"],
                    "humidity" : humidity
                    }
            logger.info("::: {:04} :::".format(i))
            logger.debug(message)
            if humidity is not None:
                mqtt_connection.publish(topic=awsconfig["TOPIC"], payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
                logger.info("Published: '" + json.dumps(message) + "' to the topic: " + "'" + awsconfig["TOPIC"] + "'")
                i += 1
    
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            logger.error(error.args[0])
            t.sleep(1.0)
            continue
    
        except Exception as error:
            dhtDevice.exit()
            raise error

        finally :
            if(i > awsconfig["RANGE"]):
                break
            t.sleep(1.0)

    logger.info('/_/_/_/Publish End/_/_/_/')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()

if __name__ == "__main__":
    main()
