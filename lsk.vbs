Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run """C:\Users\m_ren\lshk.bat"" " & WScript.Arguments.Item(0) & " " & WScript.Arguments.Item(1), 0
Set WshShell = Nothing
