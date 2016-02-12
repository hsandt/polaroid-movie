from app import App

# Arduino parameters
transmission_rate = 115200  # serial baud rate

# Video parameters
# if the videos have different FPS, use fps = self.capture.get(cv2.CAP_PROP_FPS) in the Video class instead
fps = 25

# UIDs of the RFID tags, their simplified IDs being their respective indices in the list
# Find out the UIDs of your own RFID tags by reading your serial port in Arduino IDE and replace the values with yours
rfid_uids = [
    '0x00 0x00 0x00 0x00',  # 0 (no tag found)
    '0xB4 0xE2 0xE7 0x53',  # 1
    '0xA4 0xE1 0xE7 0x53',  # 2
    '0xC4 0xE2 0xE7 0x53',  # 3
    '0x24 0xDD 0xE7 0x53',  # 4
    '0x44 0xDE 0xE7 0x53'   # 5
]

def main():
    sensor_state_to_video_name = generate_sensor_state_to_video_name()
    app = App(rfid_uids, sensor_state_to_video_name, 'window', transmission_rate, fps, fullscreen=False)
    app.run()


def generate_sensor_state_to_video_name():
    """
    Return dictionary of video filenames per sensor state tuple, in the format 'video_xxxx.mp4' where
    the 1st x is 0 for no RFID, 1, 2, 3 or 4 for the corresponding RFID tag
    the 2nd x is 0 for no photo on the photoresistor 1, 1 else
    the 3rd x is 0 for no photo on the photoresistor 2, 1 else
    the 4th x is 0 for no photo on the photoresistor 3, 1 else

    Example: video_2010.mp4

    Videos should be put in the 'videos' folder.

    """
    return {(rfid_idx, photo1, photo2, photo3): 'video_{}{}{}{}.mp4'.format(rfid_idx, int(photo1), int(photo2), int(photo3))
            for rfid_idx in (0, 1, 2, 3, 4) for photo1 in (True, False) for photo2 in (True, False) for photo3 in (True, False)}

if __name__ == '__main__':
    main()
