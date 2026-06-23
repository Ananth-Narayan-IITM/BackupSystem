from src.extractYAML import EXTRACT_YAML
from src.generateRepositoryStructure import GENERATE_REPOSITORY_STRUCTURE


yamlDictionary = EXTRACT_YAML(
    "configYAML.yaml"
)

GENERATE_REPOSITORY_STRUCTURE(
    yamlDictionary,
    outputFile="repositoryStructure.md"
)