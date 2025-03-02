import subprocess
import os


def main():
    exclude_folders = ["venv", "production", "bin"]     # list of folder to exclude in translation search
    list_to_translate = []      # list of python file to find translation in
    list_ts_file = ["fr.ts", "en.ts"]

    for root, dirs, files in os.walk(os.environ["PROJECT_DIR"]):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        list_to_translate.extend(os.path.join(root, f) for f in files if f.endswith(".py"))
    print()
    print(f"Find {len(list_to_translate)} python file in project")

    for ts in list_ts_file:
        ts_file = os.path.join("..", "resources", ts)

        lupdate_cmd = ["pyside6-lupdate"] + ["-noobsolete"] + list_to_translate + ["-ts", ts_file]

        # Find translation in code
        subprocess.run(lupdate_cmd, check=True)

        # Translate
        linguist_cmd = ["pyside6-linguist"] + [ts_file]
        print("It's now your turn to translate !")
        subprocess.run(linguist_cmd, check=True)

        # Generate translated file
        lrelease_cmd = ["pyside6-lrelease"] + [ts_file]
        print(f"Generate {ts_file}")
        subprocess.run(lrelease_cmd, check=True)


if __name__ == "__main__":
    main()
