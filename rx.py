import base64
import uuid
import random
import time
import json
import os
import ast
import traceback
import datetime
import codecs
from paho.mqtt import client as mqtt
from dotenv import load_dotenv
from functools import reduce
from io import BytesIO
from PIL import Image


load_dotenv()


transmissions = []
def RX_MQTT(messageMqtt):
    if(messageMqtt not in transmissions):
        print("The transmission is not in cache, adding to")
        transmissions.append(messageMqtt)
    else:
        print("The transmission is in cache")


IN_TX = {}
IN_TX_META = {}

def get_extension(path):
    file_name_extension = os.path.splitext(path)
    file_extension = file_name_extension[1]   
    parts = file_extension.split(".")
    if(parts[1]=='jpg'):
        extension='jpeg'
    else:
        extension = parts[1]
    return extension

def connect_mqtt() -> mqtt:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client(client_id=os.getenv("MQTT_SERVERID"))
    client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASSWORD"))
    client.on_connect = on_connect
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", 1883)))
    return client

def subscribe(client: mqtt):
    def on_message(client, userdata, msg):
        TX_ID =  msg.topic.split('/')
        message_parsed = ast.literal_eval(msg.payload.decode())
        #print(message_parsed)   
        if(message_parsed.get('message_type')=='00'):      
            ct = datetime.datetime.now()
            print("Start time 00:-", ct)       
            RX_MQTT(TX_ID[1])
            IN_TX[TX_ID[1]] = []
            IN_TX_META[TX_ID[1]] = {"name":(message_parsed.get('content')[0]).get('file_name')}
            ct = datetime.datetime.now()
            print("Finish time 00:-", ct)       
        elif(message_parsed.get('message_type')=='01'):
            ct = datetime.datetime.now()
            print("Start time 01:-", ct)       
            if TX_ID[1] in IN_TX:
                IN_TX[TX_ID[1]].append({"part":(message_parsed.get('content')[0]).get('part'),"message":(message_parsed.get('content')[0]).get('message')})
            else:
                print("The transmission is not in working array.")  
            ct = datetime.datetime.now()
            print("Finish time 01:-", ct)           
        elif(message_parsed.get('message_type')=='02'):
            ct = datetime.datetime.now()
            print("Start time 02:-", ct)   
            if TX_ID[1] in IN_TX:                
                chunked_converted=""
                im=""
                #print(len(IN_TX[TX_ID[1]]))
                for chunk in IN_TX[TX_ID[1]]:                    
                    #print(f"Part Number:  `{chunk.get('part')}` | Message Part `{chunk.get('message')}` ")
                    chunked_converted=chunked_converted+chunk.get('message')
                file_converted = bytes(chunked_converted, 'utf-8')
                #file_converted = bytes(chunked_converted)
                #print(chunked_converted)
                print((file_converted))
                print(len(chunked_converted))
                file_name=os.path.basename(IN_TX_META[TX_ID[1]].get('name'))
                file_extension_type = get_extension(file_name)
                print(file_extension_type)
                full_path = os.getenv("MQTT_FT_CONTENT_LOCATION")+file_name
                print(full_path)

                #im.save(full_path, str(file_extension_type))
                try:
                    #im = Image.open(BytesIO(base64.b64decode(chunked_converted)))   
                    final_file = base64.b64decode(chunked_converted)
                    print(final_file)                 
                    #im.save(full_path, file_extension_type)
                    with open(full_path, 'wb') as archivo:
                        archivo.write(final_file)
                    print("Image saved successfully")

                    ct = datetime.datetime.now()
                    print("Finish time 02:-", ct)  
                except:
                    traceback.print_exc()
                    print("An exception occurred generating document")
                del IN_TX[TX_ID[1]]
            else:
                print("The transmission is not in working array.")                    
        #print(IN_TX)
    client.subscribe("transfer/#")
    client.on_message = on_message
    client.loop()

client = connect_mqtt()
subscribe(client)
client.loop_forever()
