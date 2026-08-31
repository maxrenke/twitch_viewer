Dim here, q
q = Chr(34)
here = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run q & here & "\kickplay.bat" & q & " " & WScript.Arguments.Item(0) & " " & WScript.Arguments.Item(1), 0
Set WshShell = Nothing
