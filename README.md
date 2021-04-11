![python](https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white)

# Real Time Whiteboard Capturing

Hello, friends! This is a naive implementation of a real time whiteboard capturing machine :o) 

It's very slow, but it does the job.
 
## Getting Started

Clone the repository and install the dependencies provided in the requirements file. 

Next, follow these steps in order to use the capturing machine: 

1. Download the app **Live-Reporter Live Camera** on App Store. This makes it possible to create an RTSP stream of your phone camera. Link: https://apps.apple.com/us/app/live-reporter-live-camera/id996017825

2. Open the app to start live streaming your phone camera and note down the RTSP URL

3. Assign the URL to the *source* variable in **app.py**

4. Press green button (and make sure the app is open on your phone). The GUI will show how the live stream from your phone camera is captured so you can adjust the camera position accordingly.

5. Go to http://localhost:5000/whiteboard to see how the ink is plotted on a canvas real time (in slow motion) 

## Demo

The top window shows the program GUI capturing the frames from the phone camera.

The bottom is a browser window showing the page on the /whiteboard endpoint. 

![demo](demo.gif)



