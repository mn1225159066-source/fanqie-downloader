; Inno Setup Script for FanqieDownloader Windows Installer
; Usage: Open in Inno Setup Compiler and click Build

[Setup]
AppName=FanqieDownloader
AppVersion=1.0.0
AppPublisher=南城出品
; 使用自适应 Program Files 路径：有管理员权限则安装到 Program Files；否则安装到用户本地程序目录
DefaultDirName={autopf}\bijianchuanqi
DefaultGroupName=FanqieDownloader
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename=FanqieDownloader-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
; 安装向导与卸载显示图标
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\FanqieDownloader.exe

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
