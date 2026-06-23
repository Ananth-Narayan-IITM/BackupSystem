# src/generateRepositoryStructure.py

from datetime import datetime
from pathlib import Path


def GENERATE_REPOSITORY_STRUCTURE(
        yamlDictionary,
        outputFile=None
):

    repositoryLines = []

    separator = "=" * 80

    generatedTime = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    repositoryLines.append(
        "# Repository Structure\n"
    )

    repositoryLines.append(
        f"Generated On : {generatedTime}\n"
    )

    repositoryLines.append(
        separator
    )

    totalProjects = 0

    totalItems = 0

    classificationCounter = {}

    for project in yamlDictionary["projects"]:

        totalProjects += 1

        projectID = project["projectID"]

        projectDescription = project["projectDescription"]

        projectComment = project["projectComment"]

        projectEnabled = project["projectEnabled"]

        backupUnit = project["backupInterval"]["unit"]

        backupFrequency = project["backupInterval"]["frequency"]

        repositoryLines.append(
            f"\n\n## {projectID}"
        )

        repositoryLines.append(
            f"Description : {projectDescription}"
        )

        repositoryLines.append(
            f"Comment : {projectComment}"
        )

        repositoryLines.append(
            f"Enabled : {projectEnabled}"
        )

        repositoryLines.append(
            f"Backup Interval : Every {backupFrequency} {backupUnit}(s)"
        )

        repositoryLines.append(
            "\nItems\n"
        )

        items = project["items"]

        for itemIndex, item in enumerate(items):

            totalItems += 1

            itemClassification = item["itemClassification"]

            classificationCounter[itemClassification] = (
                classificationCounter.get(
                    itemClassification,
                    0
                ) + 1
            )

            branch = (
                "└──"
                if itemIndex == len(items)-1
                else "├──"
            )

            repositoryLines.append(

                f"{branch} {item['itemID']}"

            )

            repositoryLines.append(

                f"    Description : {item['itemDescription']}"

            )

            repositoryLines.append(

                f"    Comment : {item['itemComment']}"

            )

            repositoryLines.append(

                f"    Classification : {itemClassification}"

            )

            repositoryLines.append(

                f"    Location : {item['itemLocation']}"

            )

            repositoryLines.append(

                f"    Enabled : {item['itemEnabled']}"

            )

            repositoryLines.append(

                f"    Sync Policy : {item['syncPolicy']}"

            )

            repositoryLines.append(

                f"    Exclude Folders : {item['excludeFolders']}"

            )

            repositoryLines.append(

                f"    Exclude Files : {item['excludeFiles']}"

            )

            repositoryLines.append("")

        repositoryLines.append(
            separator
        )

    repositoryLines.append(
        "\n\n# Summary\n"
    )

    repositoryLines.append(
        f"Projects : {totalProjects}"
    )

    repositoryLines.append(
        f"Items : {totalItems}\n"
    )

    repositoryLines.append(
        "Item Classification Count\n"
    )

    for key, value in sorted(
            classificationCounter.items()
    ):

        repositoryLines.append(
            f"{key} : {value}"
        )

    repositoryText = "\n".join(
        repositoryLines
    )

    print(
        repositoryText
    )

    if outputFile is not None:

        outputFile = Path(
            outputFile
        )

        outputFile.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
                outputFile,
                "w",
                encoding="utf-8"
        ) as file:

            file.write(
                repositoryText
            )

    return repositoryText