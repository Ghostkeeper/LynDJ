# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import platform  # For platform-specific tweaks.

# Due to a failed lld, some libraries of PySide6 aren't found on some computers.
# For more information, see: https://github.com/pyinstaller/pyinstaller/issues/7197
# Here is a workaround: Manually add these libraries.
if platform.system() == "Linux":
	import os.path  # To get the installed location of PySide6.
	import PySide6  # To get the installed location of PySide6.
	pyside_location = os.path.dirname(PySide6.__file__)
	additional_binaries = [(os.path.join(pyside_location, "QtOpenGL.abi3.so"), "PySide6"), (os.path.join(pyside_location, "libpyside6qml.abi3.so.6.3"), ".")]
else:
	additional_binaries = []

block_cipher = None
a = Analysis(
	["lyndj.py"],
	pathex=[],
	binaries=additional_binaries,
	datas=[("gui", "gui"), ("theme", "theme"), ("icon.svg", ".")],
	hiddenimports=["PySide6.QtOpenGL"],
	hookspath=[],
	hooksconfig={},
	runtime_hooks=[],
	excludes=["jedi", "matplotlib", "PIL", "tk", "tcl", "tk"],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False,
)
# Don't include system libraries on Posix, such as libEGL. Except a few that are necessary in AppImage. See https://github.com/AppImageCommunity/pkg2appimage/blob/master/excludelist
a.exclude_system_libraries(list_of_exceptions=[
	"libportaudio*", "libsqlite3*",  # Definitely needed by LynDJ.
	"libgio*", "libdconfsettings*", "libgvfsdbus*", "libgobject*", "libgiognomeproxy*", "libgiognutls*", "libgioenvironmentproxy*", "libglib*", "libgiolibproxy*", "libgioremote-volume-monitor*", "libgmodule*", "libgthread*", "libcairo*", "libpango*"  # Package GLib and related, workaround for undefined symbol: g_module_open_full
	"libselinux*",  # See https://github.com/AppImage/AppImages/issues/83. This makes it impossible to package on Arch Linux, but does allow it to run elsewhere.
	"libpcre*",  # Missing on Fedora 24, SLED 12 SP1, OpenSUSE Leap 42.2.
	"libkrb5support*", "libk5crypto*", "libkrb5*", "libgssapi",  # Missing on Arch Linux.
	"libkeyutils*",  # Missing on Void Linux.
	"libgdk_pixbuf*",  # Missing on Ubuntu.
	"libcrypto*", "libssl*",  # Missing on CentOS 7.
	"libblkid*", "libmount*", "libffi*", "libbsd*", "libbrotlidec*", "libbrotlicommon*", "libxkbcommon*", "libXau*", "libpng16*", "libgcrypt*", "libzstd*", "libdbus*", "libcap*", "libXdmcp*", "libsystemd*", "liblz4*", "liblzma*", "libmd*", "libxcb-xfixes*", "libxcb-render*", "libxcb-shape*", "libwayland-cursor*", "libwayland-client*", "libgvfscommon*", "libgraphite2*", "libXcursor*", "libgdk*", "libpixman*", "libwayland*", "libXdamage*", "libgtk*", "libXext*", "libXfixes*", "libatk*", "libXinerama*", "libXcomposite*", "libepoxy*", "libjpeg*", "libXrender*", "libdatrie*", "libXi*", "libXrandr*", "libatspi*", "libxcb-shm*", "libwayland-server*", "libnettle*", "libidn2*", "libhogweed*", "libgnutls*", "libtasn1*", "libunistring*", "libxcb-xkb*", "libX11-xcb*", "libxcb-sync*", "libxcb-render-util*", "libxkbcommon-x11*", "libxcb-randr*", "libxcb-image*", "libxcb-keysyms*", "libxcb-icccm*", "libxcb-util*", "libproxy*", "libxcb-glx*", "libmpdec*", "libbz2*", "libreadline*", "libtinfo*", "libyaml*", "libgirepository*", "libudev*", "libxxhash*", "libapt-pkg*", "libdb*", "libncursesw*", "libblas*", "liblapack*", "libquadmath*", "libgfortran*", "liblbfgsb*"  # Unknown status, including just to be sure.
])
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