import os
import json

def create_project_structure():
    structure = {
        "project-root": [
            ".venv/",
            "src/",
            "src/__init__.py",
            "src/main.py",
            "src/optimizer.py",
            "src/restore.py",
            "src/utils/",
            "src/utils/__init__.py",
            "src/utils/logger.py",
            "src/utils/config.py",
            "config/",
            "config/settings.json",
            "tests/",
            "tests/test_optimizer.py",
            "tests/test_restore.py",
            "requirements.txt",
            "README.md"
        ]
    }

    for folder in structure["project-root"]:
        if folder.endswith("/"):
            os.makedirs(folder, exist_ok=True)
        else:
            with open(folder, 'w') as f:
                if folder.endswith(".json"):
                    json.dump({}, f, indent=4)
                elif folder.endswith(".py"):
                    f.write("# Placeholder for {}\n".format(folder.split("/")[-1]))
                elif folder == "README.md":
                    f.write("# Project Documentation\n\nDescribe your project here.")
                elif folder == "requirements.txt":
                    f.write("# List your dependencies here\n")

if __name__ == "__main__":
    create_project_structure()
    print("Project structure created successfully.")

