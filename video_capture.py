import cv2, queue, threading

# Bufferless VideoCapture to store only the most recent frame in order
# to avoid significant delay when client is reading frames at low FPS.
class VideoCapture:

  # Gets video capture source and starts reading in a new thread
  # NB: Will keep waiting until source obtained!
  def __init__(self, source):
    print("Waiting for video capture source to open...")

    self.cap = cv2.VideoCapture(source)

    # # Check if camera opened successfully
    # if (cap.isOpened() == False):
    #   raise Exception("Error opening video stream or file")

    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # Read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      is_valid, frame = self.cap.read()
      # Stop reading. No more frames.
      if not is_valid:
        break
      # If valid, ensure empty queue.
      if not self.q.empty():
        try:
          # Discard previous (unprocessed) frame
          self.q.get_nowait()
        except queue.Empty:
          pass
      # Add the new frame to queue for client to read.
      self.q.put(frame)

  # Gets the newest frame obtained from video capture source.
  def read(self):
    return self.q.get()


class Queue:

  def __init__(self):
    self.q = queue.Queue()


  # Adds an element and discards existing.
  def add_element(self, element):
      # Ensure empty queue.
      if not self.q.empty():
        try:
          # Discard previous (unprocessed) frame
          self.q.get_nowait()
        except queue.Empty:
          pass
      # Add the new frame to queue for client to read.
      self.q.put(element)

  # # Adds an element and discards existing.
  # def add_element(self, element):
  #     self.q.put(element)

  # Gets the newest frame from video capture source.
  def read(self):
    return self.q.get()