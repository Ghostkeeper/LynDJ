# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

!define APP_NAME "LynDJ"
!define WEBSITE "https://github.com/Ghostkeeper/LynDJ"
!define DESCRIPTION "Plays music in a way that is easy for Lindy Hop DJs"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONPATCH 0

# Need administrative rights in order to install to Program Files.
RequestExecutionLevel admin

InstallDir "$PROGRAMFILES64\LynDJ"
LicenseData "..\LICENSE.md"
Name "${APP_NAME}"
outFile "${APP_NAME}-installer.exe"

# NSIS logic library.
!include LogicLib.nsh

# Pages in the installer.
Page license
Page directory
Page instfiles

# Check for admin rights on start-up.
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
	messageBox mb_iconstop "Administrator rights required to install to Program Files and register the program!"
	setErrorLevel 740
	quit
${EndIf}
!macroend
function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

section "install"
	setOutPath $INSTDIR
	file /r ..\dist\*.*

	# Create the uninstaller.
	writeUninstaller "$INSTDIR\uninstall.exe"

	# Desktop shortcut.
	createShortcut "$DESKTOP\LynDJ.lnk" "$INSTDIR\LynDJ.exe" "" "$INSTDIR\icon.ico"

	# Start menu entry.
	createDirectory "$SMPROGRAMS\LynDJ"
	createShortCut "$SMPROGRAMS\LynDJ\LynDJ.lnk" "$INSTDIR\LynDJ.exe" "" "$INSTDIR\icon.ico"

	# Registry entries for the program, so that it gets listed in add/remove program screen of Windows.
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "DisplayName" "LynDJ - ${DESCRIPTION}"
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "InstallLocation" "$\"$INSTDIR$\""
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "DisplayIcon" "$\"$INSTDIR\icon.ico$\""
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "Publisher" "Ghostkeeper"
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "HelpLink" "$\"${WEBSITE}$\""
	writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONPATCH}$\""
	writeRegDword HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "VersionMajor" ${VERSIONMAJOR}
	writeRegDword HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "VersionMinor" ${VERSIONMINOR}
	writeRegDword HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "NoModify" 1  # This uninstaller doesn't modify.
	writeRegDword HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ" "NoRepair" 1  # This uninstaller doesn't repair.
sectionEnd

function un.onInit
	setShellVarContext all

	messageBox mb_okcancel "Uninstall LynDJ, removing it permanently from your computer?" IDOK next
		abort
	next:
	!insertmacro VerifyUserIsAdmin
functionEnd
section "uninstall"
	rmDir /r $INSTDIR

	# Remove start menu entry.
	delete "$SMPROGRAMS\LynDJ\LynDJ.lnk"
	rmDir "$SMPROGRAMS\LynDJ"

	# Remove program from registry.
	deleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LynDJ"
sectionEnd