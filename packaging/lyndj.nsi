# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

!define APP_NAME "LynDJ"
!define WEBSITE "https://github.com/Ghostkeeper/LynDJ"
!define DESCRIPTION "Plays music in a way that is easy for Lindy Hop DJs"

# Need administrative rights in order to install to Program Files.
RequestExecutionLevel admin

InstallDir "C:\Program Files\LynDJ"
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
	messageBox mb_iconstop "Administrator rights required to install to Program Files!"
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
	CreateShortcut "$desktop\LynDJ.lnk" "$instdir\LynDJ.exe"
sectionEnd