# main.py

from src.extractYAML import EXTRACT_YAML

from src.validateYAML import VALIDATE_YAML

from src.generateRepositoryStructure import GENERATE_REPOSITORY_STRUCTURE

from src.initializeRepository import INITIALIZE_REPOSITORY

from src.checkSchedule import CHECK_SCHEDULE

def MAIN():

    yamlDictionary = EXTRACT_YAML(

        "configYAML.yaml"

    )

    VALIDATE_YAML(

        yamlDictionary

    )

    GENERATE_REPOSITORY_STRUCTURE(

        yamlDictionary,

        outputFile="repositoryStructure.md"

    )

    INITIALIZE_REPOSITORY(

        yamlDictionary

    )

    scheduleSummary = CHECK_SCHEDULE(

        yamlDictionary

    )

    return scheduleSummary


if __name__ == "__main__":

    MAIN()