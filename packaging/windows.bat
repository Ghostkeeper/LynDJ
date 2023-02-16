python -m pip install pyinstaller
python -m pip install -r "requirements.txt"

python -m PyInstaller LynDJ.spec

"C:\Program Files (x86)\NSIS\makensis.exe" packaging\lyndj.nsi