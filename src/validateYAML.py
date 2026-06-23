# src/validateYAML.py


def VALIDATE_YAML(yamlDictionary):

    if yamlDictionary is None:

        raise ValueError(
            "YAML file is empty."
        )

    if "hardDisk" not in yamlDictionary:

        raise KeyError(
            "Missing hardDisk."
        )

    if "localPC" not in yamlDictionary:

        raise KeyError(
            "Missing localPC."
        )

    if "projects" not in yamlDictionary:

        raise KeyError(
            "Missing projects."
        )

    return yamlDictionary