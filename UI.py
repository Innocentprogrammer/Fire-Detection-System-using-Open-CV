from tkinter import *
from PIL import Image, ImageTk
import cv2         
import threading   
import playsound   
from twilio.rest import Client 
import time

def start():
    # video = cv2.VideoCapture(0)
    # while True:
    #     ret, frame = video.read()
    #     print(f"Frame: {frame}")
    #     cv2.imshow('frame', frame)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

# The below line is to access xml file which includes positive and negative images of fire. (Trained images) File is also provided within the quote "NO MR_STOCK FOOTAGE NO MR (1831)_preview.mp4" 
    fire_cascade = cv2.CascadeClassifier('fire_detection.xml') 

    video = cv2.VideoCapture(0) 
    runOnce = False 
    Message_Status = False
    Alarm_Status = False

# Twilio credentials (replace with your own)
    account_sid = 'AC36e95b61cbe9d66361337165b95710e2'
    auth_token = '896e9c4cc69d7ec03250b4520c89b516'
    twilio_phone_number = '+12568263610'
    recipient_phone_number = '+918445518517'

    def play_alarm_sound_function(): 
        playsound.playsound('preview.mp3',True) 
        if cv2.waitKey(1) & 0xFF == ord('q'):
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
    while(True):
        ret, frame = video.read() 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fire = fire_cascade.detectMultiScale(frame, 1.2, 5) 

        if len(fire) > 0:
            for (x,y,w,h) in fire:
                cv2.rectangle(frame,(x-20,y-20),(x+w+20,y+h+20),(255,0,0),2)
                ri_gray = gray[y:y+h, x:x+w]
                ri_color = frame[y:y+h, x:x+w]

                print("Fire alarm initiated")
                threading.Thread(target=play_alarm_sound_function).start() 
                if Message_Status == False:
                    threading.Thread(target=send_message_function).start()
                    Message_Status = True

            # cv2.imshow('frame', frame)
            # cv2.waitKey(1)  # Wait for 1 millisecond 
            # time.sleep(5000)# Wait for 5 seconds
            # break # Break out of the loop after fire detection

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
    video.release()
    cv2.destroyAllWindows()
 
root = Tk()
root.config(bg="White")
root.minsize(400, 500)
root.maxsize(400, 500)
root.title("Fire Detection System Using OpenCV")
ico = Image.open('circle 2.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
label = Label(root, text="Fire Detection System", font="Times 15", bg="white")
label.place(x=110, y=5)
start = Button(root, text="Start", command=start, bg="green", fg="white", font="Times 14 bold")
start.place(x=170,y=50)

root.mainloop()