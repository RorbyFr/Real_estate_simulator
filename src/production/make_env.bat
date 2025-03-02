@Echo OFF

pushd %~dp0\..
SET "SRC_DIR=%CD%"
popd

:: Actualise python path
pushd %~dp0\..\..\COTS\Python-3.12.8
SET "PYTHON_DIR=%CD%"
popd
SET "PYTHONHOME=%PYTHON_DIR%"
SET "PYTHONPATH=%PYTHON_DIR%"

echo PYTHON_DIR=%PYTHON_DIR%
echo SRC_DIR=%SRC_DIR%

:: Create virtual environment
echo =========== Create virtual environment ===========
echo.
echo Create %SRC_DIR%\venv
CALL %PYTHON_DIR%\python.exe -m venv %SRC_DIR%\venv
echo.

:: Active virtual environment
CALL %SRC_DIR%\venv\Scripts\activate.bat

:: Download libraries
echo =========== Download librairies ===========
echo.
pip install -r %~dp0\requirements.txt
echo.


pause