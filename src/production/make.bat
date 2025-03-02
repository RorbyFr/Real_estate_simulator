@Echo OFF

IF NOT DEFINED VIRTUAL_ENV (
	CALL %~dp0\_env.bat
)

SET "PAUSE="
if "%1" == "pause" (
	SET "PAUSE=pause"
)

:: Compile ui file into py file
CALL %~dp0\compile_resources.bat %PAUSE%

SET "MAIN_FILE=%PROJECT_DIR%\gui.py"

pushd %PROJECT_DIR%\..\bin
SET "BIN_DIR=%CD%"
popd

echo.
echo MAIN_FILE = %MAIN_FILE%
echo BIN_DIR = %BIN_DIR%
echo.

:: Compile project in Nuitka
echo.
echo =========== Compile project with Nuitka ===========
echo.
pushd %PROJECT_DIR%
python production\compile.py
popd

IF %PAUSE% == "pause" (
	pause
)

