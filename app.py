import cv2
import re
import serial
import serial.tools.list_ports

from video import Video


class App(object):
    """
    Main application class

    Attributes:
        rfid_uids              [list(string)] UIDs of the RFID tags, in the format '0x44 0xDE 0xE7 0x53'
        video_filenames        [list(string)] name of the videos associated to the RFID tags, with the same indices
        transmission_rate      [int] baud rate
        fps                    [int] frame rate of the update loop, and also of the videos
        fullscreen             [int] should the window be fullscreen?
        serial                 [Serial] serial configuration to receive Arduino signal
        video                  [Video] video wrapper for an
        running                [bool] should be application be running?
        last_input_keycode     [int] keycode of the last input received, -1 if no input received in last frame

    """

    def __init__(self, rfid_uids, video_filenames, window_name='window', transmission_rate=9600, fps=25, fullscreen=False):
        self.rfid_uids = rfid_uids
        self.video_filenames = video_filenames
        self.window_name = window_name
        self.transmission_rate = transmission_rate
        self.fps = fps
        self.fullscreen = fullscreen
        self.serial = serial.Serial(baudrate=transmission_rate)
        self.video = Video(window_name)  # create video wrapper in advance, we will load each video by name later
        self.running = False
        self.last_input_keycode = -1

    def setup(self):
        pass
        # self.detect_port()

    def run(self):
        print 'Run app in window "{}"'.format(self.window_name)
        # FPS1 = cvRound( cvGetCaptureProperty(capture1, CV_CAP_PROP_FPS)
        fixed_tick_diff = 1. / self.fps * cv2.getTickFrequency()  # equivalent of delta time, in ticks

        # open main window in fullscreen mode
        print 'Open fullscreen window'
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN if self.fullscreen else cv2.WINDOW_NORMAL)

        self.running = True
        lag = 0
        tick_end = cv2.getTickCount()
        while self.running:
            tick_start = cv2.getTickCount()
            lag += tick_start - tick_end

            self.process_input()

            while lag >= fixed_tick_diff:
                self.update()
                lag -= fixed_tick_diff

            tick_end = cv2.getTickCount()
            lag += tick_end - tick_start

            # Some tricks from CombineVids.c http://www.shervinemami.info/combineVids.html
            # Make sure the video runs at roughly the correct speed.
            # Add a delay that would result in roughly the desired frames per second.
            # Factor in how much time was used to process this frame already.
            delay = fixed_tick_diff - lag
            delay_ms = int(round(float(delay) * 1000 / cv2.getTickFrequency()))

            # Make sure there is at least some delay, to allow OpenCV to do its internal processing.
            # (this includes the case of being late ie having a negative delay)
            if delay_ms < 1:
                delay_ms = 1

            c = cv2.waitKey(delay_ms)  # Wait for a keypress, and let OpenCV display its GUI.
            self.last_input_keycode = c & 0xFF

        if self.serial.is_open:
            self.serial.close()

    def process_input(self):
        # Quit on ESC press
        if self.last_input_keycode == 27:
            self.running = False

        # DEBUG: play video on C, V, B
        if self.last_input_keycode == ord('c'):
            self.play_video(self.video_filenames[0], looping=True)
        if self.last_input_keycode == ord('v'):
            self.play_video(self.video_filenames[1])
        if self.last_input_keycode == ord('b'):
            self.play_video(self.video_filenames[2])

    def update(self):
        # if not self.serial.port:
        if not self.serial.is_open:
            # no port device connected yet or previous device connection was lost
            # detect any existing serial port
            self.open_connected_port()

        if self.video is not None:
            # to make things simple, we assume that the FPS of the app is the FPS of the video
            self.video.play_next_frame()

    def open_connected_port(self):
        """Get com port (often '/dev/ttyACM0' or '/dev/ttyACM1'), or keep current port if still present"""
        ports = list(serial.tools.list_ports.comports())

        # DEBUG
        # for p in ports:
        #     print p

        if len(ports) == 0:
            # print 'No serial ports found'
            return

        if self.serial.is_open and self.serial.port in (p.device for p in ports):
            # Current port device still in list, keep it (if possible, do not call this method if already a port!)
            print 'Keep current serial port ({})'.format(self.serial.port)
        else:
            # No current port device or the current device was lost, choose an arbitrary one
            self.serial.port = ports[0].device
            self.serial.open()
            print 'Open serial port: {}'.format(self.serial.port)

    def play_video(self, filename, looping=False):
        self.video.open(filename, looping)

    def read_serial(self):
        """
        Read data received at serial port and trigger corresponding events

        """
        # try-catch adapted from http://stackoverflow.com/questions/28509398/handle-exception-in-pyserial-during-disconnection
        try:
            line = self.serial.readline()
        except serial.SerialException as e:
            # There is no new data from serial port, probably sensed RFID
            # but was removed too fast (continue elegantly
            # instead of throwing exception as it does usually)
            print 'Sensed RFID but could not receive new data from serial port'
            return
        except TypeError as e:
            # We lost connection with Arduino, cancel serial port device and wait for next frame to detect another
            # port if possible
            print 'Disconnect of USB->UART occured'
            self.serial.port = ''
            # DEBUG
            print 'Serial is open? {}'.format(serial.is_open)
            # self.serial.close()  # close port (would be done anyway?)
            return

        # Some data was received

        # DEBUG
        # print line

        line = line.strip()
        if line.startswith('UID Value'):
            # RFID found, parse UID in 'UID Value: 0x44 0xDE 0xE7 0x53' for instance (keep string value)
            uid = re.findall('UID Value: ([0-9xA-F\s]+)$', line)[0]
            rfid_idx = self.rfid_uids.index(uid)
            print 'RFID #{0} detected (UID {1})'.format(rfid_idx, uid)
            self.on_rfid_detected(rfid_idx)

    def on_rfid_detected(self, rfid_idx):
        self.play_video(self.video_filenames[rfid_idx], looping=True)

