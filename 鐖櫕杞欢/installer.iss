; Inno Setup Script for FanqieDownloader Windows Installer
; Usage: Open in Inno Setup Compiler and click Build

[Setup]
AppName=FanqieDownloader
AppVersion=1.0.0
DefaultDirName={pf}\FanqieDownloader
DefaultGroupName=FanqieDownloader
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename=FanqieDownloader-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern

[Files]
; Install all built files from PyInstaller onedir output
Source: "dist\FanqieDownloader\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\FanqieDownloader"; Filename: "{app}\FanqieDownloader.exe"
Name: "{commondesktop}\FanqieDownloader"; Filename: "{app}\FanqieDownloader.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "在桌面创建快捷方式"; Flags: unchecked

[Run]
Filename: "{app}\FanqieDownloader.exe"; Description: "安装完成后运行 FanqieDownloader"; Flags: nowait postinstall skipifsilent