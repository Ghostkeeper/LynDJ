# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

# Script to package the application on Ubuntu.
# Tested using Ubuntu 22.04 and Debian 11.

# Install dependencies.
if [ $(dpkg-query -W -f='${Status}' python3-pip 2>/dev/null | grep -c "ok installed") -eq 0 && $(dpkg-query -W -f='${Status}' portaudio19-dev 2>/dev/null | grep -c "ok installed") -eq 0 && $(dpkg-query -W -f='${Status}' libfuse2 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
	sudo apt update
	sudo apt install python3-pip portaudio19-dev libfuse2
fi
if [[ ! -e appimagetool-x86_64.AppImage ]]; then
	wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
	chmod +x appimagetool-x86_64.AppImage
fi
python3 -m pip install pyinstaller
python3 -m pip install -r "requirements.txt"

# Build the application.
rm -rf dist
python3 -m PyInstaller LynDJ.spec

# Package the build.
cp packaging/AppRun dist/LynDJ/AppRun
chmod +x dist/LynDJ/AppRun
cp packaging/icon.png dist/LynDJ/.DirIcon
cp packaging/LynDJ.desktop dist/LynDJ/LynDJ.desktop
./appimagetool-x86_64.AppImage dist/LynDJ/
mv LynDJ-x86_64.AppImage LynDJ.AppImage