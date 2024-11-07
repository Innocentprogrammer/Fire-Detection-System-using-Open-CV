from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import playsound
from twilio.rest import Client
import time

def start():
    global video
    fire_cascade = cv2.CascadeClassifier('fire_detection.xml')
    video = cv2.VideoCapture(0)  # Open webcam
    runOnce = False

    # Twilio credentials (replace with your own)
    account_sid = 'AC36e95b61cbe9d66361337165b95710e2'
    auth_token = '896e9c4cc69d7ec03250b4520c89b516'
    twilio_phone_number = '+12568263610'
    recipient_phone_number = '+918445518517'

    # Flags for alarm, message, and email status
    Alarm_Status = False
    Message_Status = False
    Fire_Reported = 0

    def play_alarm_sound_function():
        playsound.playsound('preview.mp3', True)
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

    def show_frame():
        global Fire_Reported, Message_Status, Alarm_Status
        Fire_Reported = 0
        if video.isOpened():
            ret, frame = video.read()
            if ret:
                # Step 1: Fire Intensity Detection
                frame = cv2.resize(frame, (960, 540))
                blur = cv2.GaussianBlur(frame, (41, 41), 0)
                hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

                # Define the fire-like color range (intensity-based detection)
                lower = np.array([18, 80, 80], dtype="uint8")
                upper = np.array([30, 255, 255], dtype="uint8")

                mask = cv2.inRange(hsv, lower, upper)
                output = cv2.bitwise_and(frame, hsv, mask=mask)
                no_red = cv2.countNonZero(mask)

                # If significant red/yellow color is detected
                if int(no_red) > 15000:
                    Fire_Reported += 1

                # Step 2: Confirm with Cascade Detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                fire = fire_cascade.detectMultiScale(frame, 1.2, 5)

                if Fire_Reported >= 1 and len(fire) > 0:
                    for (x, y, w, h) in fire:
                        cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
                        print("Fire alarm initiated")

                        # Trigger the alarm
                        if Alarm_Status == False:
                            threading.Thread(target=play_alarm_sound_function).start()
                            Alarm_Status = True

                        # Send the message once
                        if Message_Status == False:
                            threading.Thread(target=send_message_function).start()
                            Message_Status = True

                # Convert frame to ImageTk format for Tkinter
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                camera_label.imgtk = imgtk
                camera_label.configure(image=imgtk)

            camera_label.after(10, show_frame)  # Schedule the next frame

    show_frame()

def stop():
    global video
    if video.isOpened():
        video.release()
        camera_label.config(image='')

root = Tk()
root.config(bg="White")
root.minsize(800, 600)
root.maxsize(800, 600)
root.title("Fire Detection System Using OpenCV")
ico = Image.open('circle 2.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
label = Label(root, text="Fire Detection System", font="Times 15", bg="white")
label.place(x=300, y=5)

# Add label to display the video feed
camera_label = Label(root)
camera_label.place(x=50, y=100, width=700, height=400)

# Start and Stop buttons
start_button = Button(root, text="Start", command=start, bg="green", fg="white", font="Times 14 bold")
start_button.place(x=350, y=520)
stop_button = Button(root, text="Stop", command=stop, bg="red", fg="white", font="Times 14 bold")
stop_button.place(x=450, y=520)

root.mainloop()
