# Real estate simulator project


## Presentation
This is a software to simulate real estate purchase. This software can find duration of loan, house size, contribution, monthly payment and interest rate parameters.
This software is a Pyside6 gui and use Qt translator.

## Quick start
To launch software with source code you must do before:
* Download Python 3.12.8 at https://www.python.org/downloads/release/python-3128/ and deploy in COTS\Python-3.12.8 folder
* Create virtual environment from src\production\requirements.txt thanks to src\production\make_env.bat call
* Compile ui file into py file thanks to src\production\compile_resources.bat call

After that, the software can be launch with src\launch.bat call.

## Compilation of delivery
To transform our source code into executable we use Nuitka library.
Before compiling this software you must to have Python 3.12.8 virtual environment (see 2 steps of Quick start).
This software can be compiled with src\production\make.bat call, it's generate bin folder which containing executable.
