@Echo OFF

:: Update environment variables
pushd %~dp0\..\
SET "PROJECT_DIR=%CD%"
popd

:: Activate virtual environment
CALL %~dp0\..\venv\Scripts\activate.bat
