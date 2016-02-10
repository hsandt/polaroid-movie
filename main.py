from app import App

# Arduino parameters
transmission_rate = 115200  # serial baud rate

# Video parameters
fps = 25

# UIDs of the RFID tags, their simplified IDs being their respective indices in the list
rfid_uids = [
    '0x00 0x00 0x00 0x00',  # 0 (dummy)
    '0xB4 0xE2 0xE7 0x53',  # 1
    '0xA4 0xE1 0xE7 0x53',  # 2
    '0xC4 0xE2 0xE7 0x53',  # 3
    '0x24 0xDD 0xE7 0x53',  # 4
    '0x44 0xDE 0xE7 0x53'   # 5
]

# List of names of the video files associated to the RFID tags,
# where their indices in the list matches the one of the UIDs in rfid_uids
video_filenames = [
    'SampleVideo_720x480_1mb.mp4',
    'SampleVideo_720x480_2mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
]

sensor_state_to_video_name = {
    (1, False, False, False): 'SampleVideo_720x480_1mb.mp4',
    (1, False, False, True): 'SampleVideo_720x480_2mb.mp4',
    (1, True, False, False): 'SampleVideo_640x360_1mb.mp4',
    (1, False, True, False): 'SampleVideo_640x360_1mb.mp4',
    (2, True, True, False): 'SampleVideo_640x360_1mb.mp4',
    (2, True, False, False): 'SampleVideo_640x360_1mb.mp4',
    (3, True, True, False): 'SampleVideo_640x360_1mb.mp4',
    (3, False, True, False): 'SampleVideo_640x360_1mb.mp4',
    (4, True, False, False): 'SampleVideo_640x360_1mb.mp4',
    (4, True, True, False): 'SampleVideo_640x360_1mb.mp4',
}


def main():
    app = App(rfid_uids, video_filenames, sensor_state_to_video_name, 'window', transmission_rate, fps, fullscreen=False)
    app.run()


if __name__ == '__main__':
    main()
