[Setup]
AppName=Transcrip
AppVersion=0.1.0
DefaultDirName={pf}\Transcrip
DefaultGroupName=Transcrip
OutputDir=dist
OutputBaseFilename=Transcrip-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "..\dist\Transcrip.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\deps\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{#SourcePath}\..\deps\ffmpeg'))
Source: "..\deps\cuda\cuda_installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: FileExists(ExpandConstant('{#SourcePath}\..\deps\cuda\cuda_installer.exe'))
Source: "..\deps\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: FileExists(ExpandConstant('{#SourcePath}\..\deps\vc_redist.x64.exe'))

[Icons]
Name: "{group}\Transcrip"; Filename: "{app}\Transcrip.exe"
Name: "{commondesktop}\Transcrip"; Filename: "{app}\Transcrip.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Run]
Filename: "{app}\Transcrip.exe"; Description: "Abrir o Transcrip"; Flags: nowait postinstall skipifsilent
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/quiet /norestart"; Flags: runhidden; Check: FileExists(ExpandConstant('{tmp}\vc_redist.x64.exe'))
Filename: "{tmp}\cuda_installer.exe"; Parameters: "/silent"; Flags: runhidden; Check: FileExists(ExpandConstant('{tmp}\cuda_installer.exe'))
