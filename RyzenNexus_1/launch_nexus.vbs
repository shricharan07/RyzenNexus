Set WinScriptHost = CreateObject("WScript.Shell")
' This command runs the server and hides the window (0)
WinScriptHost.Run "python D:\RyzenNexus_1\engine\server.py", 0
Set WinScriptHost = Nothing