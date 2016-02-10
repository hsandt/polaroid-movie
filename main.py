from app import App

# Arduino parameters
transmission_rate = 115200  # serial baud rate

# Video parameters
fps = 25

# UIDs of the RFID tags, their simplified IDs being their respective indices in the list
rfid_uids = [
    '0xB4 0xE2 0xE7 0x53',
    '0xA4 0xE1 0xE7 0x53',
    '0xC4 0xE2 0xE7 0x53',
    '0x24 0xDD 0xE7 0x53',
    '0x44 0xDE 0xE7 0x53'
]

# List of names of the video files associated to the RFID tags,
# where their indices in the list matches the one of the UIDs in rfid_uids
video_filenames = [
    'SampleVideo_720x480_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
    'SampleVideo_640x360_1mb.mp4',
]


def main():
    app = App(rfid_uids, video_filenames, 'window', transmission_rate, fps, fullscreen=False)
    app.run()


if __name__ == '__main__':
    main()
