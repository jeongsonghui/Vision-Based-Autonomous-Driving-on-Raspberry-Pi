import threading
import time
import cv2
import RPi.GPIO as GPIO
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image

PWMA = 18
AIN1   =  22
AIN2   =  27

PWMB = 23
BIN1   = 25
BIN2  =  24

def motor_back(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,True) #AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,True) #BIN1
    
def motor_go(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,True)#AIN2
    GPIO.output(AIN1,False) #AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,True)#BIN2
    GPIO.output(BIN1,False) #BIN1

def motor_stop():
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,False) #AIN1
    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,False) #BIN1
    
def motor_right(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,True)#AIN2
    GPIO.output(AIN1,False) #AIN1
    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,True) #BIN1
    
def motor_left(speed):
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,True) #AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,True)#BIN2
    GPIO.output(BIN1,False) #BIN1
        
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN2,GPIO.OUT)
GPIO.setup(AIN1,GPIO.OUT)
GPIO.setup(PWMA,GPIO.OUT)

GPIO.setup(BIN1,GPIO.OUT)
GPIO.setup(BIN2,GPIO.OUT)
GPIO.setup(PWMB,GPIO.OUT)

L_Motor= GPIO.PWM(PWMA,100)
L_Motor.start(0)

R_Motor = GPIO.PWM(PWMB,100)
R_Motor.start(0)

class NvidiaModel(nn.Module):
    def __init__(self):
        super(NvidiaModel, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 24, kernel_size=5, stride=2),
            nn.ELU(),
            nn.Conv2d(24, 36, kernel_size=5, stride=2),
            nn.ELU(),
            nn.Conv2d(36, 48, kernel_size=5, stride=2),
            nn.ELU(),
            nn.Conv2d(48, 64, kernel_size=3),
            nn.ELU(),
            nn.Dropout(0.2),
            nn.Conv2d(64, 64, kernel_size=3),
            nn.ELU(),
        )
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(64 * 1 * 18, 100), 
            nn.ELU(),
            nn.Linear(100, 50),
            nn.ELU(),
            nn.Linear(50, 10),
            nn.ELU(),
            nn.Linear(10, 1)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

model = NvidiaModel()

speedSet = 40

resize = transforms.Resize((66,200))
tf_toTensor = transforms.ToTensor()

def img_preprocess(image):
    height, _, _ = image.shape
    image = image[int(height/2):,:,:]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image = cv2.resize(image, (200,66))
    image = cv2.GaussianBlur(image,(5,5),0)
    _,image = cv2.threshold(image,160,255,cv2.THRESH_BINARY_INV)
    return image

def drive_straight_after_delay(speed, delay):
    global angle_locked
    angle_locked = True
    time.sleep(delay) 
    motor_go(speed) 
    set_steering_angle_for_duration(112, 3)
    
def set_steering_angle(angle):
    global steering_angle
    steering_angle = angle

def reset_steering_angle():
    global steering_angle
    steering_angle = 0

def set_steering_angle_for_duration(angle, duration):
    set_steering_angle(angle)
    timer = threading.Timer(duration, reset_steering_angle)
    timer.start()

camera = cv2.VideoCapture(-1)
camera.set(3, 640)
camera.set(4, 480)
        
def main():
    
    model_path = '/home/songheeji/AI_CAR/worst_model.pth'
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    carState = "stop"
    
    try:
        while True:
            keyValue = cv2.waitKey(1)
        
            if keyValue == ord('q') :
                break
            elif keyValue == 82 :
                print("go")
                carState = "go"
            elif keyValue == 84 :
                print("stop")
                carState = "stop"
                
            _, image = camera.read()
            image = cv2.flip(image,-1)
            preprocessed = img_preprocess(image)
            cv2.imshow('pre', preprocessed)
            preprocessed = tf_toTensor(preprocessed)
            preprocessed = preprocessed.unsqueeze(0)
            
            outputs = model(preprocessed)
            steering_angle = outputs.item()
            print("predict angle:",steering_angle)
                
            if carState == "go":
                if steering_angle >= 111.5 and steering_angle <= 114.5:
                    print("go")
                    motor_go(speedSet)
                elif steering_angle > 114.5 and steering_angle < 118.5:
                    print("right")
                    motor_right(speedSet)
                elif steering_angle < 111.5:
                    print("left")
                    motor_left(speedSet)
                elif steering_angle >118.5:
                    print("detected")
                    motor_stop()
                    threading.Thread(target=drive_straight_after_delay, args=(50, 3)).start()
            elif carState == "stop":
                motor_stop()
            
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()