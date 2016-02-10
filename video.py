import cv2


class Video(object):
    """
    Wrapper for an OpenCV video capture that allows playing frame by frame with optional looping

    Attributes:
        window_name [string] name of the OpenCV window to play this video in
        filename    [string] path to video file
        looping     [bool] is the video looping?
        capture     [VideoCapture] OpenCV video capture of the video clip
    """

    def __init__(self, window_name, filename='', looping=False):
        self.window_name = window_name
        self.filename = filename
        self.looping = looping
        # if filename is provided, immediately open video capture to match OpenCV syntax
        # else, prepare an empty video wrapper (common usage in this application)
        if filename:
            self.capture = cv2.VideoCapture(filename)
        else:
            self.capture = cv2.VideoCapture()

    def open(self, filename, looping=False):
        print 'Open video file {}'.format(filename)
        self.capture.open(filename)  # will also release previous video if any still active
        self.looping = looping

    def close(self):
        self.capture.release()

    def update(self):
        if self.capture.isOpened():
            self.play_next_frame()
            # TODO: looping

    def play_next_frame(self):
        # fps = self.capture.get(cv2.CAP_PROP_FPS)
        # print fps

        ret, frame = self.capture.read()

        # stop at end of video
        if not ret:
            return True

        cv2.imshow(self.window_name, frame)

