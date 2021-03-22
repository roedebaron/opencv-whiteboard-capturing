import threading

import cv2
import numpy as np
import utils
from video_capture import VideoCapture
from video_capture import Queue

########################################################################
pathImage = "sample3.jpg"
# widthImg = 640
# heightImg = 360
# widthImg = 640

# show_gui = False
########################################################################



# Captures ink on a paper.
class CaptureMachine():


	# "Constructor" for video capture sources.
	@classmethod
	def using_video_capture(cls, video_capture_source, is_show_gui):
		print("Using video capture")
		cap = VideoCapture(video_capture_source)
		return cls(None, cap, is_show_gui)

	# "Constructor" for static image source.
	@classmethod
	def using_image(cls, image_path, is_show_gui):
		print("Using image")
		return cls(image_path, None, is_show_gui)

	def __init__(self, image_path, video_cap, is_show_gui):
		self.widthImg = 640
		self.heightImg = 360
		self.image_path = None
		self.cap = None
		self._current_img_binarized = None
		self.gui_frames_queue = Queue() # Frames for GUI
		# self.pixel_coordinates_queue = Queue() # Not in use.. .
		if image_path is not None:
			self.image_path = image_path
		if video_cap is not None:
			self.cap = video_cap
		if is_show_gui:
			self._start_gui()




	# Starts the GUI thread. Shows the GUI :)
	def _start_gui(self):
		print("Starting GUI...")
		t = threading.Thread(target = self._start_gui_loop)
		t.daemon = True
		t.start()

		# CaptureMachine._is_show_gui = True
		# Trackbars for adjusting threshold on runtime.
		utils.initialize_trackbars()

		imgBlank = np.zeros((self.heightImg, self.widthImg, 3),
		                    np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
		image_array = ([imgBlank, imgBlank, imgBlank, imgBlank],
		                  [imgBlank, imgBlank, imgBlank, imgBlank])

		self.gui_frames_queue.add_element(image_array)

		# LABELS FOR DISPLAY
		self.labels = [["Original", "Gray", "Threshold", "Contours"],
		          ["Biggest Contour", "Warp Prespective", "Warp Gray", "Adaptive Threshold"]]

	def _start_gui_loop(self):
		print("Starting GUI loop...")
		while True:
			image_array = self.gui_frames_queue.read()
			stackedImage = utils.stack_images(image_array, 0.75, self.labels)
			cv2.imshow("Result", stackedImage)
			cv2.waitKey(10)


	# Starts capturing in a new thread.
	def start_capturing(self):
		print("Starting capturing...")
		t = threading.Thread(target = self._start_capturing_loop)
		t.daemon = True
		t.start()



	def _start_capturing_loop(self):
		print("Starting capturing loop...")
		while True:
			# print("Get pixels")
			if self.image_path:
				img = cv2.imread(self.image_path)
			else:
				img = self.cap.read()

			_current_img_binarized, img_all  = self._capture_image(img)

			# Add to GUI
			self.gui_frames_queue.add_element(img_all)
			self._current_img_binarized = _current_img_binarized




	# Gets the ink pixels for the current frame.
	# NB: The current binarized image is updated in another thread.
	def get_current_frame_ink_pixels(self):
		result = self._convert_to_coordinate_arrays(self._current_img_binarized)
		self._current_img_binarized = None
		return result



	# Captures and returns a binarized version of the image content.
	def _capture_image(self, img):
		img = cv2.resize(img, (self.widthImg, self.heightImg))  # RESIZE IMAGE
		imgBlank = np.zeros((self.heightImg, self.widthImg, 3),
		                    np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
		imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
		imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # ADD GAUSSIAN BLUR
		thres = utils.get_track_bar_values()  # GET TRACK BAR VALUES FOR THRESHOLDS
		imgThreshold = cv2.Canny(imgBlur, thres[0], thres[1])  # APPLY CANNY BLUR
		kernel = np.ones((5, 5))
		imgDial = cv2.dilate(imgThreshold, kernel, iterations = 2)  # APPLY DILATION
		imgThreshold = cv2.erode(imgDial, kernel, iterations = 1)  # APPLY EROSION

		## FIND ALL COUNTOURS
		imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
		imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
		contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL,
		                                       cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
		cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

		# FIND THE BIGGEST COUNTOUR
		biggest, maxArea = utils.calc_biggest_contour(contours)  # FIND THE BIGGEST CONTOUR

		# If connected corners found -> capture image.
		if biggest.size != 0:
			biggest = utils.reorder_points(biggest)
			cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
			imgBigContour = utils.draw_rectangle(imgBigContour, biggest, 2)
			pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
			pts2 = np.float32(
				[[0, 0], [self.widthImg, 0], [0, self.heightImg], [self.widthImg, self.heightImg]])  # PREPARE POINTS FOR WARP
			matrix = cv2.getPerspectiveTransform(pts1, pts2)
			imgWarpColored = cv2.warpPerspective(img, matrix, (self.widthImg, self.heightImg))

			# REMOVE 20 PIXELS FORM EACH SIDE
			imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
			imgWarpColored = cv2.resize(imgWarpColored, (self.widthImg, self.heightImg))

			# APPLY ADAPTIVE THRESHOLD
			imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
			imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 9, 2)
			imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
			imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)
			# print("Done")


			# Image Array for Display
			img_all = ([img, imgGray, imgThreshold, imgContours],
			           [imgBigContour, imgWarpColored, imgWarpGray, imgAdaptiveThre])

			return imgAdaptiveThre, img_all
		else:
			img_all = ([img, imgGray, imgThreshold, imgContours],
			                  [imgBlank, imgBlank, imgBlank, imgBlank])
			return None, img_all


	# Converts image to two arrays (x and y values) for pixels that contains ink (black color)
	# NB: This is very inefficient...
	def _convert_to_coordinate_arrays(self, img):
		if img is None:
			return None, None

		x_array = []
		y_array = []
		for i in range(len(img)):
			for j in range(len(img[i])):
				if(img[i][j] == 0):
					x_array.append(j)
					y_array.append(i)

		return x_array, y_array


























