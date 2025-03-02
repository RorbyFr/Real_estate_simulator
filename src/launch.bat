@Echo OFF

CALL %~dp0\production\_env.bat

CALL python %~dp0\gui.py
