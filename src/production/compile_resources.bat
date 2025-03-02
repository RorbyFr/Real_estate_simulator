@Echo OFF

IF NOT DEFINED VIRTUAL_ENV (
	CALL %~dp0\_env.bat
)

SET "RESOURCES_FOLDER=%~dp0\..\resources"

echo.
echo =========== Compile UI resources files in py file ===========
echo.

:: Compile ui resource file into python file
for %%f in ("%RESOURCES_FOLDER%\*.ui") do (
    echo Compilation of %%f...
    pyside6-uic "%%f" -o "%%~dpnf.py"
	python %~dp0\compatibility_uic_translate.py %%~dpnf.py
)

echo.

if "%1" == "pause" (
	pause
)
