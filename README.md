LynDJ
=====
LynDJ is a desktop application designed for playing music for an audience. In particular, it is specialised to playing music for Lindy Hop socials. This DJ software allows playback of music easily and safely, and provides extra control and information for what is important for swing dancing.

Main features
-------------
* A graphical interface with a thematic design.
* The interface is designed to prevent accidentally starting/stopping playback, for use with fiddly touch pads.
* Select music from your library, and create a playlist.
* Control volume for playback, and store these volume changes for future play-throughs of that track.
* Track metadata on tracks such as BPM, recording age, style, energy level and wen it was last played.
* Sort your library by any metadata.
* Set an end time for your session and get a warning when that time is approaching.
* A frequency spectrograph to visualise upcoming musical cues.
* Toggling between mono and stereo, for use with bad speaker set-ups.
* An Auto-DJ will suggest the next track to play.

Development state
-----------------
This project is in alpha testing at the moment. It is in regular use by the developer in weekly socials in the local city. However, it is not feature-complete yet, and not considered stable yet, without some more stringent testing.

Installation
------------
There are several ways to install this application onto your computer. This outlines your options, from easy to hard. Each option includes instructions for various platforms. If your platform is not listed, please select the most similar platform (e.g. for Arch Linux, installation is probably similar to Ubuntu).

<details>
<summary>From source: Ubuntu 22.04</summary>
1. Install system dependencies. To do this, open a terminal (Ctrl+Alt+T) and type the following:
```
sudo apt install python3-pip git portaudio19-dev
```
2. Download the source code of LynDJ.
```
git clone https://github.com/Ghostkeeper/LynDJ
cd LynDJ
```
3. Install LynDJ's Python dependencies.
```
python3 -m pip install -r requirements.txt
```
4. You can now run the application from the terminal inside of this directory, by executing:
```
python3 lyndj.py
```
</details>