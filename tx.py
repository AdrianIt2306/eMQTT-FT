import base64
import uuid
import random
import time
import os
import json
import datetime
import sys
from paho.mqtt import client as mqtt
from dotenv import load_dotenv
from functools import reduce
from io import BytesIO
from PIL import Image

load_dotenv()

def TX_MQTT(FILE_LOCATION):
    # Print TX UUID
    TXUUID=uuid.uuid4()
    print('TX UUID is: ' + str(TXUUID))
    # Open file
    with open(FILE_LOCATION, "rb") as image_file:
        # Encode file to base64
        data = base64.b64encode(image_file.read())
        #print(data)
        # Convert enconded file to str
        data_pre = str(data)
        data_pre = data_pre[2:]
        data_pre =  data_pre.rstrip(data_pre[-1])
        #print(data_pre)
        # Define the num of chunks
        K = 5
        # compute chunk length
        chnk_len = len(data_pre) // K 
        # Chunck file into multiple
        chunked = [data_pre[idx : idx + chnk_len] for idx in range(0, len(data_pre), chnk_len)]        
        # Printing result
        print("The K len chunked length : " + str(chnk_len))
        #print("The K len chunked list : \n" + str(chunked))
        return chunked


def TX_MQTT_PUB(MESSAGE,TOPIC):
    client = mqtt.Client(client_id=os.getenv("MQTT_CLIENTID"))
    client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASSWORD"))
    # Establish a connection
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", 1883)), 10)
    publish_result = client.publish(TOPIC,payload=str(MESSAGE),qos=1)
    client.loop()
    #print(publish_result.is_published())
    client.disconnect(reasoncode=None)


FILE_LOCATION = sys.argv[1]
chunked_file = ""
chunked_file=TX_MQTT(FILE_LOCATION)



# Publish a message
TXUUID=str(uuid.uuid4())[0:8]
#print('TX UUID is: ' + TXUUID)
#print(len(chunked_file))
ct = datetime.datetime.now()
print("Start time 00:-", ct)
message_start = {"id":TXUUID,"message_type":"00","content":[{"partitions":str(len(chunked_file)),"file_name":FILE_LOCATION}]}
TX_MQTT_PUB(message_start,("transfer/"+TXUUID))

for index, item in enumerate(chunked_file):
    #print(index, item)
    #print(f"Transmission ID:  `{TXUUID}` | Part `{index+1}` - Message Part `{item}` ")
    # Define parameter for connection
    pending=str(index+1) + "/" +str(len(chunked_file))
    message_partition = {"id":TXUUID,"message_type":"01","content":[{"part":index+1,"pending":pending,"message":item}]}
    #print(message_partition)
    TX_MQTT_PUB(message_partition,("transfer/"+TXUUID))

message_finish = {"id":TXUUID,"message_type":"02","content":[""]}
TX_MQTT_PUB(message_finish,("transfer/"+TXUUID))
ct = datetime.datetime.now()
print("Finish time 02:-", ct)



