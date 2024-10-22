import cv2         
import threading   
import playsound   
from twilio.rest import Client   
import datetime
import serial.tools.list_ports 

# The below line is to access the xml file which includes positive and negative images of fire. 
fire_cascade = cv2.CascadeClassifier('fire_detection.xml') 

# Initialize cameras
video1 = cv2.VideoCapture(0)  # First camera
video2 = cv2.VideoCapture(1)  # Second camera
if video1.isOpened():
    print("camera1 is open")
if video2.isOpened():
    print("camera2 is open ")

runOnce = False 
Message_Status = False
ard_flag=False

# Twilio credentials (replace with your own)
account_sid = 'AC544f52444dd4bedff81d1d8fa407a651'
auth_token = '3bda45e5908ff42f0f1e0966f0ce70ea'
twilio_phone_number = '+12035294362'
recipient_phone_number = '+918384865874'

# Video writer settings for saving detected fire footage
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_file = None


# for arduino connectivity 

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []

for one in ports:
    portsList.append(str(one))
    print(str(one))

# com = input("Select Com Port for Arduino #: ")
com=3
 

# for i in range(len(portsList)):
#     if portsList[i].startswith("COM" + str(com)):
#         use = "COM" + str(com)
#         print(use)



serialInst.baudrate = 9600
serialInst.port = "COM3"
serialInst.open()

def initiate_ard():

    command = 'ON'
    serialInst.write(command.encode('utf-8'))

# arduino connnectivity code end

# Function to save video footage when fire is detected
def save_video(frame):
    global output_file
    if output_file is None:
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = cv2.VideoWriter(f'fire_detected_{now}.avi', fourcc, 20.0, (frame.shape[1], frame.shape[0]))
    output_file.write(frame)

# Function to log fire detection events
def log_event(event):
    with open("fire_detection_log.txt", "a") as log_file:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{now} - {event}\n")

# Play alarm sound function
def play_alarm_sound_function(): 
    playsound.playsound('preview.mp3', True) 
    print("Fire alarm end") 

# Twilio message sending function
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

while(True):
    Alarm_Status = False
 
    # Read frames from both cameras
    ret1, frame1 = video1.read() 
    # ret2, frame2 = video2.read()

    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    # gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Detect fire in both frames
    fire1 = fire_cascade.detectMultiScale(frame1, 1.2, 5)
    # fire2 = fire_cascade.detectMultiScale(frame2, 1.2, 5)

    # Process fire detection in first camera
    for (x, y, w, h) in fire1:
        cv2.rectangle(frame1, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
        save_video(frame1)  # Save the footage
        log_event("Fire detected in Camera 1")  # Log event

        print("Fire alarm initiated for Camera 1")
        threading.Thread(target=play_alarm_sound_function).start()
        if ard_flag==False :
                initiate_ard()
                ard_flag=True
        if Message_Status == False:
            threading.Thread(target=send_message_function).start()
            Message_Status = True

    # Process fire detection in second camera
    # for (x, y, w, h) in fire2:
    #     cv2.rectangle(frame2, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
    #     save_video(frame2)  
    #     log_event("Fire detected in Camera 2")  

    #     print("Fire alarm initiated for Camera 2")
    #     threading.Thread(target=play_alarm_sound_function).start()
    #     if Message_Status == False:
    #         threading.Thread(target=send_message_function).start()
    #         Message_Status = True

    # Display the frames from both cameras
    cv2.imshow('Camera 1', frame1)
    # cv2.imshow('Camera 2', frame2)

    if video2.isOpened():
        ret2, frame2 = video2.read()
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        fire2 = fire_cascade.detectMultiScale(frame2, 1.2, 5)

        for (x, y, w, h) in fire2:
            cv2.rectangle(frame2, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
            save_video(frame2)  
            log_event("Fire detected in Camera 2")  

            print("Fire alarm initiated for Camera 2")
            threading.Thread(target=play_alarm_sound_function).start()
            if ard_flag==False :
                initiate_ard()
                ard_flag=True
            if Message_Status == False:
                threading.Thread(target=send_message_function).start()
                Message_Status = True

        cv2.imshow('Camera 2', frame2)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video writer and cameras
if output_file is not None:
    output_file.release()
video1.release()
video2.release()
cv2.destroyAllWindows()
