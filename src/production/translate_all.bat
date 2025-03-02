@Echo OFF

:: Active environment
CALL %~dp0\_env.bat

:: Find translation in code
echo Generate .ts file from code
python translate_all.py
