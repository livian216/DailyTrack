#define MyAppName "DailyTrack"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DailyTrack Project"
#define MyAppExeName "DailyTrack.exe"

[Setup]
AppId={{F3AE1DF5-EFC3-4D4D-9F72-EE184CF51A89}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DailyTrack
DefaultGroupName=DailyTrack
OutputDir=..\installer_output
OutputBaseFilename=DailyTrack_Setup_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"

[Files]
Source: "..\dist\DailyTrack\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DailyTrack"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DailyTrack"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 DailyTrack"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 默认不删除用户数据目录（%APPDATA%\DailyTrack 或用户自定义目录）

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    MsgBox(
      '卸载前建议先在软件中导出全部数据（JSON/CSV）并手动备份数据库。' + #13#10#13#10 +
      '说明：' + #13#10 +
      '1) 卸载将清理软件安装目录中的程序文件。' + #13#10 +
      '2) 软件不会自动删除你的任务数据目录（默认在 %APPDATA%\DailyTrack 或你自定义的目录）。' + #13#10 +
      '3) 如需彻底删除数据，请在卸载后手动删除数据目录。',
      mbInformation, MB_OK
    );
  end;
end;
