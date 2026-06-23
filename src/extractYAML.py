# src/extractYAML.py

from pathlib import Path
import yaml


def EXTRACT_YAML(yamlFile):

    yamlFile = Path(yamlFile)

    if not yamlFile.exists():

        raise FileNotFoundError(
            f"YAML file not found:\n{yamlFile}"
        )

    with open(yamlFile, "r", encoding="utf-8") as file:

        yamlDictionary = yaml.safe_load(file)

    return yamlDictionary