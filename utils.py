import cv2
import numpy as np


## TO STACK ALL THE IMAGES IN ONE WINDOW
def stack_images(imgArray, scale, labels=[]):
	rows = len(imgArray)
	cols = len(imgArray[0])
	# If columns is a list
	rowsAvailable = isinstance(imgArray[0], list)
	width = imgArray[0][0].shape[1]
	height = imgArray[0][0].shape[0]
	if rowsAvailable:
		for x in range(0, rows):
			for y in range(0, cols):
				imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
				if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
		imageBlank = np.zeros((height, width, 3), np.uint8)
		hor = [imageBlank] * rows
		hor_con = [imageBlank] * rows
		for x in range(0, rows):
			hor[x] = np.hstack(imgArray[x])
			hor_con[x] = np.concatenate(imgArray[x])
		ver = np.vstack(hor)
		# ver_con = np.concatenate(hor)
	else:
		for x in range(0, rows):
			imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
			if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
		hor = np.hstack(imgArray)
		hor_con = np.concatenate(imgArray)
		ver = hor
	if len(labels) != 0:
		eachImgWidth = int(ver.shape[1] / cols)
		eachImgHeight = int(ver.shape[0] / rows)
		# print(eachImgHeight)
		for d in range(0, rows):
			for c in range(0, cols):
				cv2.rectangle(ver, (c * eachImgWidth, eachImgHeight * d),
				              (c * eachImgWidth + len(labels[d]) * 13 + 27, 30 + eachImgHeight * d), (255, 255, 255),
				              cv2.FILLED)
				cv2.putText(ver, labels[d][c], (eachImgWidth * c + 10, eachImgHeight * d + 20), cv2.FONT_HERSHEY_COMPLEX,
				            0.7, (255, 0, 255), 2)
	return ver


def reorder_points(myPoints):
	myPoints = myPoints.reshape((4, 2))
	myPointsNew = np.zeros((4, 1, 2), dtype = np.int32)
	add = myPoints.sum(1)

	myPointsNew[0] = myPoints[np.argmin(add)]
	myPointsNew[3] = myPoints[np.argmax(add)]
	diff = np.diff(myPoints, axis = 1)
	myPointsNew[1] = myPoints[np.argmin(diff)]
	myPointsNew[2] = myPoints[np.argmax(diff)]

	return myPointsNew


def calc_biggest_contour(contours):
	biggest = np.array([])
	max_area = 0
	for i in contours:
		area = cv2.contourArea(i)
		if area > 5000:
			peri = cv2.arcLength(i, True)
			approx = cv2.approxPolyDP(i, 0.02 * peri, True)
			if area > max_area and len(approx) == 4:
				biggest = approx
				max_area = area
	return biggest, max_area


def draw_rectangle(img, biggest, thickness):
	cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
	cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
	cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
	cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)

	return img

# Nothing
def nothing(x):
	pass

# Init trackbars that enable user to adjust settings at runtime.
# Default values yield great results!
def initialize_trackbars(th1=200, th2=100):
	cv2.namedWindow("Trackbars")
	cv2.resizeWindow("Trackbars", 360, 240)
	cv2.createTrackbar("Threshold1", "Trackbars", th1, 255, nothing)
	cv2.createTrackbar("Threshold2", "Trackbars", th2, 255, nothing)


def get_track_bar_values():
	Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
	Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")



	# if Threshold1 < 1:
	# 	Threshold1 = 200
	#
	# if Threshold2 < 1:
	# 	Threshold2 = 100

	# Threshold1 = 200
	# Threshold2 = 200
	src = Threshold1, Threshold2
	return src