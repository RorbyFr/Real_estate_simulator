# Real estate simulator project


## Presentation
This is a software to simulate real estate purchase. This software can find duration of loan, house size, contribution, monthly payment and interest rate parameters.
This software is a Pyside6 gui and use Qt translator.

## Quick start
To launch software with source code you must do before:
* Download Python 3.12.8 at https://www.python.org/downloads/release/python-3128/ and deploy in `COTS\Python-3.12.8` folder
* Create virtual environment from `src\production\requirements.txt` thanks to `src\production\make_env.bat` call
* Compile ui file into py file thanks to `src\production\compile_resources.bat` call

After that, the software can be launch with src\launch.bat call.

**For Penguin or Apple lovers: run the `src/production/setup.sh` script. It requires Python 3 to be in the path.**

In case you want to do the manual steps, here are them: 

1. Create a new Python environment in the root folder: `python3 -m venv venv` or if you have the `uv` tool installed: `uv venv --seed venv`. It will create a `venv` folder.
2. Enable the new virtual environment: `source venv/bin/activate`
3. Install the required packages with: `pip install -r src/production/requirements.txt`
4. Compile the resources so it's ready to run: `pyside6-project build src`.

This project uses the pyside6-project and the associated `.pyproject` file as it's easier to work with across all platforms and give an expected result.

## Compilation of delivery
To transform our source code into executable we use Nuitka library.
Before compiling this software you must to have Python 3.12.8 virtual environment (see 2 steps of Quick start).
This software can be compiled with `src\production\make.bat` call, it's generate bin folder which containing executable.
