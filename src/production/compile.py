import os
import subprocess


command = [
    f"{os.environ['PROJECT_DIR']}\\venv\\Scripts\\nuitka.cmd",
    "--standalone",
    "--onefile",
    "--enable-plugin=pyside6",
    f"--output-dir={os.environ['BIN_DIR']}",
    "--include-data-file=resources/*.png=resources/",
    "--include-data-file=resources/*.css=resources/",
    "--include-data-file=resources/*.qm=resources/",
    "--windows-console-mode=disable",
    "--output-filename=real_estate_simulator",
    "--windows-icon-from-ico=resources/real_estate.ico",
    f"{os.environ['MAIN_FILE']}"
]

try:
    subprocess.run(command, check=True)
except FileNotFoundError as e:
    print("Erreur : Le fichier ou l'exécutable est introuvable.")
    print(f"Chemin de Nuitka : {command[0]}")
    print(f"Détails : {e}")
