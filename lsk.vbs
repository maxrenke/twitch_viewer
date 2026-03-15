' VBS Script for launching Kick.com streams silently
Dim WshShell, command, channel, quality
Set WshShell = CreateObject("WScript.Shell")

' Get arguments
If WScript.Arguments.Count < 2 Then
    WScript.Quit 1
End If

channel = WScript.Arguments.Item(0)
quality = WScript.Arguments.Item(1)

' Build command using local batch file
command = """C:\Users\m_ren\repos\twitch_viewer\lshk_local.bat"" " & channel & " " & quality

' Execute completely hidden (VLC will still show because streamlink launches it)
Dim result
result = WshShell.Run(command, 0, False)

Set WshShell = Nothing
WScript.Quit result
