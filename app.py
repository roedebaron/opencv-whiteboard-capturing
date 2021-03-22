from flask import Flask, render_template
from flask import jsonify
from flask_cors import CORS
from capture_machine import CaptureMachine


print("Running!")
app = Flask(__name__)
CORS(app)


# Uncomment to use webcam instead.
# source = 0

# Input Rtsp stream from iOS app here.
# Remember to start streaming from the app before running this program.
source = "rtsp://192.168.0.104"
# Show GUI?
is_show_gui = True # False option not implemented.

source = "sample3.jpg"


# capture_machine = CaptureMachine.using_video_capture(source, is_show_gui)
capture_machine = CaptureMachine.using_image(source, is_show_gui)

# Start capturing
capture_machine.start_capturing()

@app.route('/')
def hello_world():
	return 'Hello World!'


@app.route('/whiteboard')
def get_whiteboard():
	return render_template("index.html")


@app.route('/inkPixels')
def get_ink_pixels():
	success = False

	# Get ink pixels for the next valid frame.
	# A frame is only valid if paper can be detected in the frame i.e. four connected corners.
	while not success:
		x, y = capture_machine.get_current_frame_ink_pixels()
		if x != None:
			success = True
			print("Valid frame found")
		else:
			print("No valid frame found")

	return {
		'x': x,
		'y': y
	}



if __name__ == '__main__':
	app.run(host='localhost', port=5000)
