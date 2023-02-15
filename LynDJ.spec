# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

# Due to a failed lld, some libraries of PySide6 aren't found on some computers.
# For more information, see: https://github.com/pyinstaller/pyinstaller/issues/7197
# Here is a workaround: Manually add these libraries.
import os.path  # To get the installed location of PySide6.
import PySide6  # To get the installed location of PySide6.
pyside_location = os.path.dirname(PySide6.__file__)

block_cipher = None
a = Analysis(
	["lyndj.py"],
	pathex=[],
	binaries=[(os.path.join(pyside_location, "QtOpenGL.abi3.so"), "PySide6"), (os.path.join(pyside_location, "libpyside6qml.abi3.so.6.3"), ".")],
	datas=[("gui", "gui"), ("theme", "theme"), ("icon.svg", ".")],
	hiddenimports=["PySide6.QtOpenGL"],
	hookspath=[],
	hooksconfig={},
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
	pyz,
	a.scripts,
	[],
	exclude_binaries=True,
	name="LynDJ",
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=False,
	disable_windowed_traceback=False,
	argv_emulation=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	icon="packaging/icon.ico"
)
coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	upx_exclude=[],
	name="LynDJ",
)