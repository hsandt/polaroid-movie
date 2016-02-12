import cv2
import numpy as np


class Video(object):
    """
    Wrapper for an OpenCV video capture that allows playing frame by frame with optional looping

    Attributes:
        window_name     [string] name of the OpenCV window to play this video in
        filename        [string] path to video file
        looping         [bool] is the video looping?
        capture         [VideoCapture] OpenCV video capture of the video clip
        frame_counter   [int] next frame index to play
    """

    def __init__(self, window_name, filename='', looping=False):
        self.window_name = window_name
        self.filename = filename
        # if filename is provided, immediately open video capture to match OpenCV syntax
        # else, prepare an empty video wrapper (common usage in this application)
        if filename:
            self.capture = cv2.VideoCapture(filename)
            self.frame_counter = 0
        else:
            self.capture = cv2.VideoCapture()
            self.frame_counter = -1
        self.looping = looping

    def open(self, filename, looping=False):
        """
        Open video at the beginning

        """
        print 'Open video file {}'.format(filename)
        self.frame_counter = 0
        self.capture.open(filename)  # will also release previous video if any still active
        self.looping = looping

    def open_same_frame(self, filename, looping=False):
        """
        Open video at same frame as the previous video, or 0 if no previous video.
        Prefer this method with looping and all videos, and with the same duration

        """
        print 'Open video file {} at same frame'.format(filename)
        frame_counter = self.frame_counter if self.is_open else 0
        self.capture.open(filename)  # will also release previous video if any still active
        self.looping = looping
        # warp at same time as previous video
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

    def close(self):
        """
        Close video and show blank image

        """
        if self.is_open:
            self.show_blank()
            self.capture.release()
            self.frame_counter = -1

    @property
    def is_open(self):
        return self.capture.isOpened()

    def update(self):
        if self.capture.isOpened():
            self.play_next_frame()

    def play_next_frame(self):
        """
        Play next frame or video, or 1st frame if video is looping has reached its end

        """
        ret, frame = self.capture.read()
        # assert ret, 'Video capture: cannot read next frame; video seems to have ended without looping or closing'

        # if no frame could be read, it means the video has ended and is *not* looping
        # then clear window with a last empty frame
        if ret:
            cv2.imshow(self.window_name, frame)
        else:
            self.show_blank()
            return

        # http://stackoverflow.com/questions/17158602/playback-loop-option-in-opencv-videos
        self.frame_counter += 1
        # If the last frame is reached, reset the capture and the frame_counter in looping mode, close video else
        # This means that self.capture.read() should always return a correct frame when called
        if self.frame_counter == self.capture.get(cv2.CAP_PROP_FRAME_COUNT):
            if self.looping:
                self.frame_counter = 0  # Or whatever as long as it is the same as next line
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                pass

    def show_blank(self):
        """
        Show a white frame
        Useful to prevent window from showing the last frame of the video 'frozen' when a video stops

        """
        if self.capture.isOpened:
            height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            white_frame = np.zeros((height, width, 3), np.uint8)
            white_frame[:] = (255, 255, 255)
            cv2.imshow(self.window_name, white_frame)
