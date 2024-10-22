import threading   
from twilio.rest import Client   
import playsound   
import cv2      
import serial.tools.list_ports   

# The below line is to access xml file which includes positive and negative images of fire. (Trained images) File is also provided within the quote "NO MR_STOCK FOOTAGE NO MR (1831)_preview.mp4" 
fire_cascade = cv2.CascadeClassifier('fire_detection.xml') 

video = cv2.VideoCapture(0) 
runOnce = False 
Message_Status = False

# Twilio credentials (replace with your own)
account_sid = 'AC544f52444dd4bedff81d1d8fa407a651'
auth_token = '3bda45e5908ff42f0f1e0966f0ce70ea'
twilio_phone_number = '+12035294362'
recipient_phone_number = '+918445518517'

def play_alarm_sound_function(): 
    playsound.playsound('fire_Alarm.mp3',True) 
    print("Fire alarm end") 

def send_message_function():
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="Warning! A Fire Accident has been detected.",
            from_=twilio_phone_number,
            to=recipient_phone_number
        )
        print(f"Message sent to {recipient_phone_number}")
    except Exception as e:
        print(e)


# for arduino connectivity 
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []

for one in ports:
    portsList.append(str(one))
    print(str(one))

# com = input("Select Com Port for Arduino #: ")
com=3
 

for i in range(len(portsList)):
    if portsList[i].startswith("COM" + str(com)):
        use = "COM" + str(com)
        print(use)



serialInst.baudrate = 9600
serialInst.port = use
serialInst.open()

# arduino connnectivity code end
		
while(True):
    Alarm_Status = False
    ret, frame = video.read() 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fire = fire_cascade.detectMultiScale(frame, 1.2, 5) 

    for (x,y,w,h) in fire:
        cv2.rectangle(frame,(x-20,y-20),(x+w+20,y+h+20),(255,0,0),2)
        ri_gray = gray[y:y+h, x:x+w]
        ri_color = frame[y:y+h, x:x+w]

        print("Fire alarm initiated")
        threading.Thread(target=play_alarm_sound_function).start() 
        if Message_Status == False:
            threading.Thread(target=send_message_function).start()
            Message_Status = True

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break