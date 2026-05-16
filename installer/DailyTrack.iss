#define MyAppName "DailyTrack"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "DailyTrack Project"
#define MyAppExeName "DailyTrack.exe"
#define MyAppId "{{F3AE1DF5-EFC3-4D4D-9F72-EE184CF51A89}"
#define MyAppIdReg "{F3AE1DF5-EFC3-4D4D-9F72-EE184CF51A89}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DailyTrack
DefaultGroupName=DailyTrack
OutputDir=..\installer_output
OutputBaseFilename=DailyTrack_Setup_v1.1.1
Compression=lzma
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

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

[Code]
function TryGetExistingUninstaller(var UninstallerPath: string): Boolean;
var
  UninstallKey: string;
  UninstallCmd: string;
begin
  Result := False;
  UninstallerPath := '';
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppIdReg}_is1';

  if not RegQueryStringValue(HKLM64, UninstallKey, 'UninstallString', UninstallCmd) then
    if not RegQueryStringValue(HKLM, UninstallKey, 'UninstallString', UninstallCmd) then
      if not RegQueryStringValue(HKCU, UninstallKey, 'UninstallString', UninstallCmd) then
        Exit;

  UninstallerPath := RemoveQuotes(UninstallCmd);
  Result := (UninstallerPath <> '') and FileExists(UninstallerPath);
end;

function InitializeSetup(): Boolean;
var
  ExistingUninstaller: string;
  ExecOk: Boolean;
  ExitCode: Integer;
begin
  Result := True;

  if TryGetExistingUninstaller(ExistingUninstaller) then
  begin
    ExecOk := Exec(
      ExistingUninstaller,
      '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES',
      '',
      SW_HIDE,
      ewWaitUntilTerminated,
      ExitCode
    );

    if (not ExecOk) or (ExitCode <> 0) then
    begin
      MsgBox(
        '检测到旧版本，但自动卸载失败或被取消。' + #13#10 +
        '请先手动卸载旧版本后再安装新版本。',
        mbError,
        MB_OK
      );
      Result := False;
      Exit;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    MsgBox(
      '卸载前建议先在软件中导出全部数据（JSON/CSV），并手动备份数据库。' + #13#10#13#10 +
      '说明：' + #13#10 +
      '1) 卸载将清理安装目录中的程序文件。' + #13#10 +
      '2) 软件不会自动删除你的任务数据目录（默认在 %APPDATA%\DailyTrack 或你自定义的目录）。' + #13#10 +
      '3) 如需彻底删除数据，请在卸载后手动删除数据目录。',
      mbInformation, MB_OK
    );
  end;
end;
