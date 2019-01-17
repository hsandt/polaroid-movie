# Project Name

Polaroid Movie is a project that consists in playing videos on a monitor
when the user puts Polaroid photographs on a physical grid panel. For each photo
put on a cell of the panel, a matching video which has been filmed beforehand
is played at the corresponding position in a virtual grid on the monitor.

The current code is only a prototype, however, so videos are been combined together beforehand
and only a few combinations are possible.

## Installation

Download the repository content or clone it to your computer.

### Dependencies

* OpenCV for Python 2.7
* FFmpeg for OpenCV
* Python package `pyserial`

*Note for FFmepg on Windows:*

Copy `opencv_ffmpeg[openCV version].dll` from `OpenCV\opencv\build\bin` to `[Python root path]`.

See http://stackoverflow.com/questions/13834399/cannot-open-mp4-video-files-using-opencv-2-4-3-python-2-7-in-windows-7-machi

## Usage

### Simulation

First, you need to provide the application with videos in the `videos` folder. You can find 40 sample videos on the theme of Tennis on [Google Drive](https://drive.google.com/open?id=0B0XMEiZjJ0njNmc2eFdJQm1hRzg). You can also use your own videos, provided:

* the videos are named `video_[wxyz].mp4` following the convention explained in `python/main.py`.
If you use another format than MP4, you need to adapt the code in main.py.
* all the videos have the same size and same duration
* the videos are composed of a grid of small clips, where 4 cells are associated with the values of w, x, y and z, and the clip played in the cell depends on the corresponding value: 0 for black screen, 1 to 4 for a specific clip.

For instance, in the sample videos, if we count rows and columns from the top-left:
* `w` corresponds to the center cell
* `x` corresponds to row 2, column 1
* `y` corresponds to row 1, column 2
* `z` corresponds to row 3, column 3

Run the main application: enter the python directory and run `python main.py`

Use the debug keys Y, U, I, O, P and J, K, L to simulate putting or removing a photo from
the physical panel.

### With physical device

1. Install a panel of 3x3 grid cells with MiFare-type RFID readers hidden behind the center cell,
and photoresistors inserted in holes in 3 other cells. Please refer to the installation diagram below (TODO)

2. Connect the RFID reader and the photoresistors to an Arduino card, following the wiring diagram (see `arduino/Wiring Diagram.pdf`)

3. Connect the Arduino to your computer, connect your computer to an external monitor, and run the application. Move the application window to the external monitor, which will play the role of virtual grid panel, and press F to enter fullscreen.

4. Make sure your room is lightened.

5. You can now add Polaroid photographs or any other object marked with an RFID tag on the center cell, and any opaque objects to hide the photoresistors, and you will see videos appearing and disappearing from the virtual panel at the corresponding positions.

6. Replace the videos in the videos folder, following the file name convention explained in python/main.py, to customize your experience!

## History

This project was done by students of Gobelins, l'école de l'image, in January - February 2016, as a project using the Internet of Things (IoT) making use of Polaroid photographs.
The client was photography agency Big Shot - Polanimation, an agency specialized in polaroid and digital photographs for special events.

## Improvements

The original project consisted in playing any combination of videos on the grid, for any combination of photos.

This can be done in 3 steps:

1. buy 9 NFC (RFID) readers, one per cell, and as many RFID tags
2. put individual videos in the `videos` folder, naming them `video_[number].mp4`
3. modify the code to play a combination of videos side-by-side based on the RFID IDs detected by the 9 sensors, using OpenCV video blitting feature

## Credits

The team behind the project is made of 4 students of Gobelins, who also acted for the [video samples](https://drive.google.com/open?id=0B0XMEiZjJ0njNmc2eFdJQm1hRzg):

* Mehdi Tebib
* Magali Monné
* Guillaume Raimbault
* Long Nguyen Huu

## License

For code license, see LICENSE.

The video samples have been shot by the same team of 4 students who made the project and acted in the videos.

The videos were shot in Gobelins, Paris. The team retains copyrights on the sample videos.
