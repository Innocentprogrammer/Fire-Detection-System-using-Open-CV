import cv2         
import threading   
import playsound   

# The below line is to access xml file which includes positive and negative images of fire. (Trained images) File is also provided within the quote "NO MR_STOCK FOOTAGE NO MR (1831)_preview.mp4" 
fire_cascade = cv2.CascadeClassifier('fire_detection.xml') 

video = cv2.VideoCapture(0) 
runOnce = False 
Message_Status = False


def play_alarm_sound_function(): 
    playsound.playsound('fire_Alarm.mp3',True) 
    print("Fire alarm end") 

		
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


    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break