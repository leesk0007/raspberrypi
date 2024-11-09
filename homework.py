import io
import cv2
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO

# LED on/off 함수
def led_on_off(pin, value):
    GPIO.output(pin, value)

# 거리 측정 함수
def measure_distance(trig, echo):
    time.sleep(0.2)  # 초음파 센서 준비 시간
    GPIO.output(trig, 1)  # Trig에 High 출력
    time.sleep(0.00001)  # 10us 딜레이
    GPIO.output(trig, 0)  # Trig에 Low 출력 (초음파 발사)

    # Echo 핀의 변화 감지
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    # 경과 시간 계산
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 340 * 100 / 2  # 거리 계산 (단위 cm)
    return distance

# MQTT 설정
broker_ip = "localhost"
client = mqtt.Client()
client.connect(broker_ip, 1883)
client.loop_start()

# 카메라 설정
camera = cv2.VideoCapture(0, cv2.CAP_V4L)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led1 = 6  # 첫 번째 LED 핀
led2 = 13  # 두 번째 LED 핀
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)

trig = 20  # 초음파 센서 Trig 핀
echo = 16  # 초음파 센서 Echo 핀
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

try:
    while True:
        distance = measure_distance(trig, echo)
        print("물체와의 거리는 %f cm입니다." % distance)

        if distance > 20:  # 20cm 이상
            led_on_off(led1, 0)  # LED 1 끔
            led_on_off(led2, 0)  # LED 2 끔

        elif 10 < distance <= 20:  # 10~20cm 사이
            led_on_off(led1, 1)  # LED 1 켬
            led_on_off(led2, 0)  # LED 2 끔

        elif distance <= 10:  # 10cm 이하
            led_on_off(led1, 1)  # LED 1 켬
            led_on_off(led2, 1)  # LED 2 켬

            # 카메라로 사진 촬영 및 전송
            ret, frame = camera.read()
            if ret:
                _, im_bytes = cv2.imencode('.jpg', frame)
                client.publish("jpeg", im_bytes.tobytes(), qos=0)  # 이미지 전송

        time.sleep(0.5)  # 0.5초 간격으로 거리 측정

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    # 자원 정리
    camera.release()
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()
