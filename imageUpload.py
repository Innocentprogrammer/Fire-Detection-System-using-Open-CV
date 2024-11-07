import pyrebase

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
myImage="circle 2.png"


# storage.child(myImage).put(myImage)

storage.child(myImage).put(myImage)
print(f"Image uploaded successfully to: {myImage}")

# Get the download URL of the uploaded file
download_url = storage.child(myImage).get_url(None)
print(f"Download URL: {download_url}")