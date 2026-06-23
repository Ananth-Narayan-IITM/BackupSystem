from src.extractYAML import EXTRACT_YAML

from src.validateYAML import VALIDATE_YAML

from src.generateRepositoryStructure import GENERATE_REPOSITORY_STRUCTURE


yamlDictionary = EXTRACT_YAML(

    "configYAML.yaml"

)

validationSummary = VALIDATE_YAML(

    yamlDictionary

)

GENERATE_REPOSITORY_STRUCTURE(

    yamlDictionary,

    outputFile="repositoryStructure.md"

)