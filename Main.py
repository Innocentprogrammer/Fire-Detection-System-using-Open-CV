from tkinter import *
from PIL import Image, ImageTk
import cv2         
import threading   
import playsound   
from twilio.rest import Client 
import datetime
import serial.tools.list_ports 
import pyrebase

#firebase code
config={
"apiKey": "AIzaSyCCSugng-84qOKg676gHBBEb2EKCaqiYhM",
  "authDomain": "imagefire-76e9e.firebaseapp.com",
  "projectId": "imagefire-76e9e",
  "storageBucket": "imagefire-76e9e.appspot.com",
  "messagingSenderId": "812885764485",
  "appId": "1:812885764485:web:1d94ffe4883e64f87c3cec",
  "measurementId": "G-W08BK2T8KW",
  "serviceAccount":"serviceAccount.json",
  "databaseURL":"https://imagefire-76e9e-default-rtdb.firebaseio.com/"
}

firebase=pyrebase.initialize_app(config)
storage=firebase.storage()



# Initialize the fire detector cascade
fire_cascade = cv2.CascadeClassifier('fire_detection.xml') 

# Try to open both cameras (Camera 1 and Camera 2)
video1 = cv2.VideoCapture(0)  # First camera
video2 = cv2.VideoCapture(1)  # Second camera

# Check if each camera is available
camera1_available = video1.isOpened()
camera2_available = video2.isOpened()

if camera1_available:
    print("Camera 1 is open")
else:
    print("Camera 1 is not available")

if camera2_available:
    print("Camera 2 is open")
else:
    print("Camera 2 is not available")

if not camera1_available and not camera2_available:
    print("No cameras available, exiting...")
    exit()

# Global variables
Message_Status = False
ard_flag = False
output_file1 = None
output_file2 = None
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# Twilio credentials (replace with your own)
account_sid = 'AC36e95b61cbe9d66361337165b95710e2'
auth_token = '896e9c4cc69d7ec03250b4520c89b516'
twilio_phone_number = '+12568263610'
recipient_phone_number = '+918445518517'

# Function to save video footage when fire is detected
def save_Image(frame, camera_index):
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    image_path = f'fire_detected_camera{camera_index}_{now}.jpg'
    cv2.imwrite(image_path, frame)
    log_event(f"Image saved: {image_path}")

    
    storage.child(image_path).put(image_path)
    print(f"Image uploaded successfully to: {image_path}")

# Get the download URL of the uploaded file
    download_url = storage.child(image_path).get_url(None)
    print(f"Download URL: {download_url}")
    if(download_url):
        send_message_function(download_url)



# Function to log fire detection events8
def log_event(event):
    with open("fire_detection_log.txt", "a") as log_file:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{now} - {event}\n")
        log_display.insert(END, f"{now} - {event}\n")  # Insert new log entry into the Text widget

def display_log_file_content():
    try:
        with open("fire_detection_log.txt", "r") as log_file:
            log_content = log_file.read()
            log_display.delete(1.0, END)  # Clear existing content
            log_display.insert(END, log_content)  # Insert log content
    except FileNotFoundError:
        log_display.delete(1.0, END)
        log_display.insert(END, "Log file not found.")

# Function to play alarm sound
def play_alarm_sound_function(): 
    playsound.playsound('fire-alarm.mp3', True) 
    print("Fire alarm end")

# Twilio message sending function
def send_message_function(downloadURL):
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Warning! A Fire Accident has been detected. and Image of fire place {downloadURL}",
            from_=twilio_phone_number,
            to=recipient_phone_number
        )
        print(f"Message sent to {recipient_phone_number}")
    except Exception as e:
        print(e)


ports = serial.tools.list_ports.comports()
print(type(ports))
if len(ports)>0:
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
    serialInst.port ="COM3"
    serialInst.open()
    print("arduino connected")

    def initiate_ard(cmd):
        print("initiate ard called")
        print(cmd)
        command = cmd
        serialInst.write(command.encode('utf-8'))
        return True

    # arduino connnectivity code end

# Tkinter GUI Setup
root = Tk()
root.config(bg="White")
root.minsize(1500, 700)
root.maxsize(1500, 700)
root.title("Fire Detection System Using OpenCV")
ico = Image.open('circle 2.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
my_canvas = Canvas(root)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
label = Label(root, text="Fire Detection System", font="Times 15", bg="white")
label.place(x=700, y=5)

# Camera label placeholders
camera_label1 = Label(root)
camera_label1.place(x=250, y=35, width=500, height=400)
camera_label2 = Label(root)
camera_label2.place(x=800, y=35, width=500, height=400)

# Function to show frames from the cameras
def show_frames():
    global Message_Status, ard_flag, output_file1, output_file2

    # Camera 1
    if camera1_available:
        ret1, frame1 = video1.read()

        if ret1:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            fire1 = fire_cascade.detectMultiScale(frame1, 1.2, 5)

            for (x, y, w, h) in fire1:
                cv2.rectangle(frame1, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
                save_Image(frame1,1)
                log_event("Fire detected in Camera 1")
                threading.Thread(target=play_alarm_sound_function).start()
                # if ard_flag == False:
                if len(ports)>0:
                    initiate_ard('a')
                # ard_flag=True

            # Convert the image to ImageTk format and display
            img1 = Image.fromarray(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
            imgtk1 = ImageTk.PhotoImage(image=img1)
            camera_label1.imgtk = imgtk1
            camera_label1.configure(image=imgtk1)

    # Camera 2
    if camera2_available:
        ret2, frame2 = video2.read()

        if ret2:
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            fire2 = fire_cascade.detectMultiScale(frame2, 1.2, 5)

            for (x, y, w, h) in fire2:
                cv2.rectangle(frame2, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
                save_Image(frame2,2)
                log_event("Fire detected in Camera 2")
                threading.Thread(target=play_alarm_sound_function).start()
                # if ard_flag == False:
                if len(ports)>0:
                    initiate_ard('a')
                    # ard_flag=True

            # Convert the image to ImageTk format and display
            img2 = Image.fromarray(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
            imgtk2 = ImageTk.PhotoImage(image=img2)
            camera_label2.imgtk = imgtk2
            camera_label2.configure(image=imgtk2)

    # Call the function again after 10ms
    root.after(10, show_frames)

# Start video capturing and display
def start_camera():
    show_frames()

# Stop the cameras and clean up
def stop_camera():
    global video1, video2, output_file1, output_file2
    if video1.isOpened():
        video1.release()
    if video2 and video2.isOpened():
        video2.release()
    if output_file1 is not None:
        output_file1.release()
    if output_file2 is not None:
        output_file2.release()
    camera_label1.config(image='')
    camera_label2.config(image='')

# Start and Stop buttons
start_button = Button(root, text="Start", command=start_camera, bg="green", fg="white", font="Times 14 bold")
start_button.place(x=600, y=440)
stop_button = Button(root, text="Stop", command=stop_camera, bg="red", fg="white", font="Times 14 bold")
stop_button.place(x=920, y=440)
# display_log_button = Button(root, text="Display Log", command=display_log_file_content, bg="blue", fg="white", font="Times 14 bold")
# display_log_button.place(x=900, y=440)
log_label = Label(root, text="Logs Details", font="Times 14", bg="white")
log_label.place(x=750,y=480)

# Scrollbar setup
scrollbar = Scrollbar(root)
scrollbar.place(x=610, y=510, height=170)

# Create a Text widget for log display
log_display = Text(root, wrap=WORD, yscrollcommand=scrollbar.set, fg="green", bg="white", font="Times 12", height=10, width=75)
log_display.place(x=450, y=510)
# Configure scrollbar with Text widget
scrollbar.config(command=log_display.yview)

display_log_file_content()
# Start the Tkinter main loop
root.mainloop()
