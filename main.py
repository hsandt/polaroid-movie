from time import sleep

import numpy as np
import cv2
import serial
import re

# FIND USB PORT FOR ARDUINO
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print p
# get port (often '/dev/ttyACM0' or '/dev/ttyACM1')
if len(ports) == 0:
    print 'No serial ports found, cannot run RFID application'
    exit()
acm_port = str(ports[0]).split(' ')[0]
print acm_port

# RFID info
rfid_uids = [
    '0xB4 0xE2 0xE7 0x53',
    '0xA4 0xE1 0xE7 0x53',
    '0xC4 0xE2 0xE7 0x53',
    '0x24 0xDD 0xE7 0x53',
    '0x44 0xDE 0xE7 0x53'
]

# VIDEO parameters
fps = 25
frameInterval = 1000/fps

video_filenames = [
    'SampleVideo_720x480_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
]


def read_serial():
    # ser = serial.Serial('/dev/tty.usbserial', 9600)
    # ser = serial.Serial('/dev/ttyUSB0', 9600)
    # ser = serial.Serial('COM0', 9600)
    # with serial.Serial('/dev/ttyACM0', 9600) as ser:
    with serial.Serial(acm_port, 9600) as ser:
        while True:
            # stop reading serial when user presses ESC
            if cv2.waitKey(frameInterval) & 0xFF == 27:
                break

            # try-catch adapted from http://stackoverflow.com/questions/28509398/handle-exception-in-pyserial-during-disconnection
            try:
                line = ser.readline()
            except serial.SerialException as e:
                # There is no new data from serial port, probably sensed RFID
                # but was removed too fast (continue elegantly
                # instead of throwing exception as it does usually)
                print 'Sensed RFID but could not receive new data from serial port'
                continue
            except TypeError as e:
                # Disconnect of USB->UART occured
                print 'Disconnect of USB->UART occured'
                # leave while loop to close port since we are inside a 'with' statement
                break

            # Some data was received
            # print line
            line = line.strip()
            if line.startswith('UID Value'):
                # RFID found, parse UID in 'UID Value: 0x44 0xDE 0xE7 0x53' for instance
                uid = re.findall('UID Value: ([0-9xA-F\s]+)$', line)[0]
                rfid_idx = rfid_uids.index(uid)
                print 'RFID #{0} detected (UID {1})'.format(rfid_idx, uid)
                success = on_rfid_detected(rfid_idx)
                if not success:
                    # video interrupted or failed
                    break

            sleep(.1)

    print 'END read_serial'


def on_rfid_detected(rfid_idx):
    return play_video(video_filenames[rfid_idx], True)

def show_image(filename):
    """
    Show a single image
    :param filename:
    :return:
    """
    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    if img is None:
        print 'Could not read image {}'.format(filename)
        return
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    # cv2.namedWindow('image', cv2.WINDOW_FREERATIO)
    # cv2.namedWindow('image', cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyWindow('image')


def play_video(filename, fullscreen=False):
    """
    Play a single video with optional fullscreen
    :return:
    """
    print 'Open fullscreen window'
    cv2.namedWindow('video', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)

    print 'Open video file {}'.format(filename)
    cap = cv2.VideoCapture(filename)

    while cap.isOpened():
        ret, frame = cap.read()

        # stop at end of video
        if not ret:
            return True

        cv2.imshow('video', frame)

        # STOP when user presses q, SKIP video if user presses s
        key = cv2.waitKey(frameInterval) & 0xFF
        if key in (ord('q'), 27):
            return False
        elif key == ord('s'):
            return True

    print 'Close video file'
    cap.release()
    cv2.destroyWindow('video')

def play_videos_window():
    """
    Play 2 videos in different windows

    :return:
    """
    caps = []

    for i, video_file in enumerate(video_filenames):
        print 'Open video file {}'.format(video_file)
        cap = cv2.VideoCapture(video_file)
        caps.append(cap)

    while any(map(lambda x: x.isOpened(), caps)):
        for i, cap in enumerate(caps):
            ret, frame = cap.read()

            # stop at end of video
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('window' + str(i), gray)

        # stop when user presses q
        if cv2.waitKey(frameInterval) & 0xFF == ord('q'):
            break

    for cap in caps:
        print 'Close video file'
        cap.release()
    cv2.destroyAllWindows()


def play_videos_horizontal():
    """
    Play 2 videos horizontally side by side

    :return:
    """
    caps = []

    for i, video_file in enumerate(video_filenames):
        print 'Open video file {}'.format(video_file)
        cap = cv2.VideoCapture(video_file)
        caps.append(cap)

    while any(map(lambda x: x.isOpened(), caps)):
        for i, cap in enumerate(caps):
            ret, frame = cap.read()

            # stop at end of video
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('frame' + str(i), gray)

        # stop when user presses q
        if cv2.waitKey(frameInterval) & 0xFF == ord('q'):
            break

    for cap in caps:
        print 'Close video file'
        cap.release()
    cv2.destroyAllWindows()

def main():
    # play_video(video_filenames[0])
    # play_video(video_filenames[0], true)
    # show_image('Earnslaw00.jpg')
    read_serial()
    # a = re.findall('UID Value: ([0-9xA-F\s]+)$', 'UID Value: 0x44 0xDE 0xE7 0x53')
    # print a

if __name__ == '__main__':
    main()