# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

# Script to package the application on Ubuntu.
# Tested using Ubuntu 22.04.

# Install dependencies.
sudo apt install python3-pip portaudio19-dev
wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
python3 -m pip install pyinstaller
python3 -m pip install -r "requirements.txt"

# Build the application.
rm -r dist
pyinstaller LynDJ.spec

# Package the build.
cp packaging/AppRun dist/LynDJ/AppRun
cp packaging/icon.png dist/LynDJ/.DirIcon
cp packaging/LynDJ.desktop dist/LynDJ/LynDJ.desktop
./appimagetool-x86_64.AppImage dist/LynDJ/
mv LynDJ-x86_64.AppImage LynDJ.AppImage