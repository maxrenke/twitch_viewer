Dim here, q
q = Chr(34)
here = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Enhanced VBS Script for launching streamlink with optimization options
' Usage: ls_optimized.vbs [channel] [quality] [config]
' Config: 1=minimal_gpu, 2=balanced, 3=ultra_low, 4=audio_only

Dim WshShell, command, channel, quality, config
Set WshShell = CreateObject("WScript.Shell")

' Get arguments
If WScript.Arguments.Count < 2 Then
    WScript.Quit 1
End If

channel = WScript.Arguments.Item(0)
quality = WScript.Arguments.Item(1)

' Default to minimal GPU config if not specified
config = "1"
If WScript.Arguments.Count >= 3 Then
    config = WScript.Arguments.Item(2)
End If

' Build command using the optimized config script
command = q & here & "\lsh_optimized_configs.bat" & q & " " & channel & " " & quality & " " & config

' Execute completely hidden (VLC will still show because streamlink launches it)
Dim result
result = WshShell.Run(command, 0, False)

Set WshShell = Nothing
WScript.Quit result
