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

# sensor_state_to_video_name = {
#     (0, False, False, False): 'video_0000.mp4',
#     (0, False, False, True): 'video_0001.mp4',
#     (1, False, False, False): 'video_1000.mp4',
#     (1, False, True, False): 'video_1010.mp4',
#     (2, False, False, False): 'video_2000.mp4',
#     (2, True, False, False): 'video_2100.mp4',
#     (3, False, False, False): 'video_3000.mp4',
#     (3, True, True, False): 'video_3110.mp4',
#     (4, False, False, False): 'video_4000.mp4',
#     (4, True, True, True): 'video_4111.mp4',
# }




def main():
    sensor_state_to_video_name = generate_sensor_state_to_video_name()
    app = App(rfid_uids, video_filenames, sensor_state_to_video_name, 'window', transmission_rate, fps, fullscreen=False)
    app.run()


def generate_sensor_state_to_video_name():
    """
    Return dictionary of video filenames per sensor state tuple, in the format video_xxxx where
    the 1st x is 0 for no RFID, 1, 2, 3 or 4 for the corresponding RFID tag
    the 2nd x is 0 for no photo on the photoresistor 1, 1 else
    the 3rd x is 0 for no photo on the photoresistor 2, 1 else
    the 4th x is 0 for no photo on the photoresistor 3, 1 else

    """
    return {(rfid_idx, photo1, photo2, photo3): 'video_{}{}{}{}.mp4'.format(rfid_idx, int(photo1), int(photo2), int(photo3))
            for rfid_idx in (0, 1, 2, 3, 4) for photo1 in (True, False) for photo2 in (True, False) for photo3 in (True, False)}

if __name__ == '__main__':
    main()
