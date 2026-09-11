# src/extractYAML.py

from pathlib import Path
import yaml


def EXTRACT_YAML(yamlFile):

    yamlFile = Path(yamlFile).resolve()

    mainDictionary = _READ_YAML(yamlFile)

    projectList = _READ_PROJECTS(yamlFile, mainDictionary["projects"])

    mainDictionary["projects"] = projectList

    return mainDictionary


def _READ_YAML(yamlFile):

    if not yamlFile.exists():
        raise FileNotFoundError(f"\nYAML file not found:\n{yamlFile}")

    try:
        with open(yamlFile, "r", encoding="utf-8") as file:
            yamlDictionary = yaml.safe_load(file)

    except yaml.YAMLError as error:
        raise ValueError(f"\nInvalid YAML syntax:\n{yamlFile}\n\n{error}")

    if yamlDictionary is None:
        raise ValueError(f"\nEmpty YAML file:\n{yamlFile}")

    return yamlDictionary


def _READ_PROJECTS(mainYaml, projectFiles):

    projectList = []

    projectDirectory = mainYaml.parent

    for projectFile in projectFiles:
        projectPath = (projectDirectory / projectFile).resolve()

        projectDictionary = _READ_YAML(projectPath)

        projectDictionary["_projectYamlPath"] = projectPath

        projectList.append(projectDictionary)

    return projectList
