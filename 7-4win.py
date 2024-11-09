import io
import time
import paho.mqtt.client as mqtt

def on_connect(client,userdata,flag,rc,prop=None):
    print("jpeg 토픽으로 메시지 구독 신청")
    client.subscribe("jpeg")

def on_message(client,userdata,msg):
    filename='./data/image.jpg'%(time.time()*10)
    file = open(filename,"wb")
    file.write(msg.payload)
    file.close()
    print("이미지수신 %s" % filename)

ip=input("브로커의 IP>>")

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect=on_connect
client.on_message=on_message
client.connect(ip,1883)
client.loop_forever()

