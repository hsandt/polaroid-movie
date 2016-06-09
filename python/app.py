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
        sensor_state_to_video_name
                               [list(string)] name of the videos associated to the RFID/Photo combinations (sensor_state)
        transmission_rate      [int] baud rate
        fps                    [int] frame rate of the update loop, and also of the videos
        fullscreen             [int] should the window be fullscreen?
        serial                 [Serial] serial configuration to receive Arduino signal
        video                  [Video] video wrapper for an
        running                [bool] should be application be running?
        last_input_keycode     [int] keycode of the last input received, -1 if no input received in last frame
        sensor_state           [list(int)] state of the RFID and photo sensors in the format [RFID, PHOTO1, PHOTO2, PHOTO3]
                                with RFID = 0 (no RFID), 1, 2 or 3 and PHOTOX = 0 (nothing) or 1 (covered)

    """

    def __init__(self, rfid_uids, sensor_state_to_video_name, window_name='window', transmission_rate=9600, fps=25,
                 fullscreen=False):
        self.rfid_uids = rfid_uids
        self.sensor_state_to_video_name = sensor_state_to_video_name
        self.window_name = window_name
        self.transmission_rate = transmission_rate
        self.fps = fps
        self.fullscreen = fullscreen
        self.serial = serial.Serial(baudrate=transmission_rate, timeout=0.006)  # timeout corresponds to sending 80 octal chars at 115200 baud rate
        self.video = Video(window_name)  # create video wrapper in advance, we will load each video by name later
        self.running = False
        self.last_input_keycode = -1
        self.sensor_state = [0, False, False, False]

    def run(self):
        """
        Run application by opening window and listening to serial port while rendering videos

        """
        print 'Run app in window "{}"'.format(self.window_name)
        # FPS1 = cvRound( cvGetCaptureProperty(capture1, CV_CAP_PROP_FPS)
        fixed_tick_diff = 1. / self.fps * cv2.getTickFrequency()  # equivalent of delta time, in ticks

        # open main window in fullscreen mode
        print 'Open fullscreen window'
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN if self.fullscreen else cv2.WINDOW_NORMAL)

        # initial video
        self.on_sensor_state_changed()

        self.running = True

        lag = 0
        tick_end = cv2.getTickCount()

        while self.running:
            tick_start = cv2.getTickCount()
            lag += tick_start - tick_end

            # KEYBOARD INPUT
            # IMPROVE: we do not need to check input as fast as rendering, so use a different fps
            self.process_input()

            # SERIAL PORT INPUT
            if not self.serial.is_open:
                # no port device connected yet or previous device connection was lost
                # detect any existing serial port
                self.open_connected_port()
            if self.serial.is_open:
                self.read_serial()

            # UPDATE / RENDER
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
        """
        Process keyboard input to quit application and for debugging

        """
        # Quit on ESC press
        if self.last_input_keycode == 27:
            self.running = False

        # Toggle fullscreen on F press (may not work at times, do not overdo it)
        if self.last_input_keycode == ord('f'):
            old_fullscreen_mode = cv2.getWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN)
            new_fullscreen_mode = cv2.WINDOW_FULLSCREEN if old_fullscreen_mode == cv2.WINDOW_NORMAL else cv2.WINDOW_NORMAL
            print 'Switching fullscreen mode from {} to {}'.format(old_fullscreen_mode, new_fullscreen_mode)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, new_fullscreen_mode)

        # Stop current video on S press
        if self.last_input_keycode == ord('s'):
            self.stop_video()

        # DEBUG: simulate sensors
        if self.last_input_keycode == ord('d'):
            self.on_rfid_lost()
        if self.last_input_keycode == ord('f'):
            self.on_rfid_detected(1)
        if self.last_input_keycode == ord('g'):
            self.on_rfid_detected(2)
        if self.last_input_keycode == ord('h'):
            self.on_rfid_detected(3)
        if self.last_input_keycode == ord('j'):
            self.on_rfid_detected(4)
        if self.last_input_keycode == ord('v'):
            self.toggle_photo_state(1)
        if self.last_input_keycode == ord('b'):
            self.toggle_photo_state(2)
        if self.last_input_keycode == ord('n'):
            self.toggle_photo_state(3)

    def update(self):
        if self.video.is_open:
            # to make things simple, we assume that the FPS of the app is the FPS of the video
            self.video.play_next_frame()

    def open_connected_port(self):
        """
        Check if a new port was connected or seek a new serial port (often '/dev/ttyACM0' or '/dev/ttyACM1' on Unix)
        if the current port is not valid, and start listening to this port

        """
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

    def read_serial(self):
        """
        Read data received at serial port and trigger corresponding events

        """
        # try-catch adapted from http://stackoverflow.com/questions/28509398/handle-exception-in-pyserial-during-disconnection
        try:
            line = self.serial.readline()  # ensure short timeout to continue looping quickly if no signal
        except serial.SerialException as e:
            # Lost connection with Arduino
            print 'Lost connection with Arduino'
            # close port (port does not seem to close when plugging Arduino out); you can keep last port in self.serial.port
            self.serial.close()
            return
        except TypeError as e:
            # We lost connection with Arduino, cancel serial port device and wait for next frame to detect another
            # port if possible
            print 'Disconnect of USB->UART occured'
            # self.serial.port = ''
            # DEBUG
            print 'error: {}'.format(e.message)
            print 'Serial is open? {}'.format(serial.is_open)
            # self.serial.close()  # close port (would be done anyway?)
            return

        if not line:
            return

        # Some data was received
        line = line.strip()

        # DEBUG
        # print 'line: {}'.format(line)

        # Detect RFID detected
        if line.startswith('UID Value'):
            # RFID found, parse UID in 'UID Value: 0x44 0xDE 0xE7 0x53' for instance (keep string value)
            uid = re.findall('^UID Value: ([0-9xA-F\s]+)$', line)[0]
            if uid not in self.rfid_uids:
                print 'Found unknown UID {0}, cannot choose output video'.format(uid)
                return

            rfid_idx = self.rfid_uids.index(uid)
            if rfid_idx == 0:
                print 'Found dummy UID {0}, probably an error on Arduino side'.format(uid)
                return

            print 'RFID #{0} detected (UID {1})'.format(rfid_idx, uid)
            self.on_rfid_detected(rfid_idx)

        # Detect RFID lost
        if line.startswith('Lost UID Value'):
            # RFID lost
            print 'RFID lost'

            # OPTIONAL: parse UID and check we lost the previous RFID detected
            uid = re.findall('^Lost UID Value: ([0-9xA-F\s]+)$', line)[0]
            # photo ID is from 1 to 5 but we added dummy ID 0, so it is really like an index
            rfid_idx = self.rfid_uids.index(uid)
            if rfid_idx == self.sensor_state[0]:
                print '(#{0} (UID {1}))'.format(rfid_idx, uid)
            else:
                # mismatch error coming from Arduino, but clear current RFID anyway
                print 'Warning: lost #{0} (UID {1}) whereas last RFID detected was #{2} (UID {3})'\
                    .format(rfid_idx, uid, self.sensor_state[0], self.rfid_uids[self.sensor_state[0]])

            self.on_rfid_lost()

        # Detect PHOTO detected
        if line.startswith('Photo'):
            # Photo found, parse ID from 1 to 3
            photo_id = int(re.findall('^Photo: ([0-9]+)$', line)[0])
            print 'Photoresistor #{0} detected'.format(photo_id)
            self.on_photo_detected(photo_id)

        # Detect PHOTO lost
        if line.startswith('Lost Photo'):
            # Photo found, parse ID from 1 to 3
            photo_id = int(re.findall('^Lost Photo: ([0-9]+)$', line)[0])
            print 'Photoresistor #{0} lost'.format(photo_id)
            self.on_photo_lost(photo_id)

    def on_rfid_detected(self, rfid_idx):
        assert rfid_idx
        self.sensor_state[0] = rfid_idx  # from 1 to 5
        self.on_sensor_state_changed()

    def on_rfid_lost(self):
        self.sensor_state[0] = 0
        self.on_sensor_state_changed()

    def on_photo_detected(self, photo_id):
        # photo ID is from 1 to 3 so no need to offset index
        self.sensor_state[photo_id] = True
        self.on_sensor_state_changed()

    def on_photo_lost(self, photo_id):
         # photo ID is from 1 to 3 so no need to offset index
        self.sensor_state[photo_id] = False
        self.on_sensor_state_changed()

    def toggle_photo_state(self, photo_id):
        if not self.sensor_state[photo_id]:
            self.on_photo_detected(photo_id)
        else:
            self.on_photo_lost(photo_id)

    def on_sensor_state_changed(self):
        # play video based on new state (OpenCV VideoCapture interface will also release previous video automatically)
        video_key = tuple(self.sensor_state)
        if video_key in self.sensor_state_to_video_name:
            # lookup corresponding video in dictionary (convert list to tuple since we need hashable keys)
            print 'Play video for RFID/Photo combination: {}'.format(self.sensor_state)
            self.play_video(self.sensor_state_to_video_name[video_key], looping=True, same_frame=True)
        else:
            # if possible, play video with closest sensor state; else
            print 'WARNING: undefined RFID/Photo combination: {}'.format(self.sensor_state)
            self.stop_video()

    def play_video(self, filename, looping=False, same_frame=False):
        if same_frame:
            self.video.open_same_frame(filename, looping)
        else:
            self.video.open(filename, looping)

    def stop_video(self):
        """Stop current video and show white frame"""
        self.video.close()

