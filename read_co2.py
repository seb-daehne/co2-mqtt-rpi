#!/usr/bin/env python

import sys, fcntl, time, os
import paho.mqtt.client as mqtt



def decrypt(key,  data):
    cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]
    
    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]
    
    phase2 = [0] * 8
    for i in range(8):
        phase2[i] = phase1[i] ^ key[i]
    
    phase3 = [0] * 8
    for i in range(8):
        phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff
    
    ctmp = [0] * 8
    for i in range(8):
        ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff
    
    out = [0] * 8
    for i in range(8):
        out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff
    
    return out

def hd(d):
    return " ".join("%02X" % e for e in d)

if __name__ == "__main__":
    # Key retrieved from /dev/random, guaranteed to be random ;)
    key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]

    usb_device = os.environ['USB_DEVICE']
    mqtt_server = os.environ['MQTT_SERVER']
    mqtt_port = os.environ['MQTT_PORT']
    mqtt_topic = os.environ['MQTT_TOPIC']
    
    print("+ start co2 monitor")
    print("- usb device: ", usb_device)
    print("- mqtt server: ", mqtt_server )
    print("- mqtt port: ", mqtt_port)
    print("- mqtt topic: ", mqtt_topic)
    
    fp = open(usb_device, "a+b",  0)
    
    HIDIOCSFEATURE_9 = 0xC0094806
    set_report = "\x00" + "".join(chr(e) for e in key)
    fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report)
    
    values = {}
    publish_interval_in_s=60
    start_time = 0

    while True:

        data = list(ord(e) for e in fp.read(8))
        decrypted = decrypt(key, data)
        if (decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]):
            pass
        else:
            op = decrypted[0]
            val = decrypted[1] << 8 | decrypted[2]
            
            values[op] = val
            ## From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
            if (0x50 in values):
                if (time.time() - start_time > publish_interval_in_s):
                    print("publish data to mqtt: " + str(values[0x50]))
                    client = mqtt.Client("co2")
                    client.connect(mqtt_server)
                    client.publish(mqtt_topic, values[0x50])
                    client.disconnect()
                    start_time = time.time()
                    print("\n")