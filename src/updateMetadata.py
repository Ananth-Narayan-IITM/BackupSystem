from pathlib import Path

from datetime import datetime

import json


# =============================================================================
# Public Function
# =============================================================================


def UPDATE_METADATA(yamlDictionary, backupSummary):

    metadataDictionary, metadataPath = _READ_METADATA(yamlDictionary)

    _UPDATE_REPOSITORY(metadataDictionary)

    _UPDATE_PROJECTS(metadataDictionary, backupSummary)

    _UPDATE_ITEMS(metadataDictionary, backupSummary)

    _WRITE_METADATA(metadataDictionary, metadataPath)

    _WRITE_METADATA(
        metadataDictionary,
        metadataPath=(Path(yamlDictionary["localPC"]) / "metadata" / "backupDatabase.json"),
    )

    _PRINT_METADATA_SUMMARY(backupSummary)


def _READ_METADATA(yamlDictionary):

    metadataPath = Path(yamlDictionary["hardDisk"]) / "metadata" / "backupDatabase.json"

    with open(metadataPath, "r", encoding="utf-8") as file:
        metadataDictionary = json.load(file)

    return metadataDictionary, metadataPath


def _UPDATE_REPOSITORY(metadataDictionary):

    metadataDictionary["repository"]["lastExecution"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _UPDATE_PROJECTS(metadataDictionary, backupSummary):

    today = datetime.now().strftime("%Y-%m-%d")

    for projectID in backupSummary["successfulProjects"]:
        if projectID not in metadataDictionary["projects"]:
            metadataDictionary["projects"][projectID] = {
                "firstBackup": today,
                "lastBackup": today,
                "lastStatus": "success",
                "backupCount": 1,
            }

        else:
            metadataDictionary["projects"][projectID]["lastBackup"] = today

            metadataDictionary["projects"][projectID]["lastStatus"] = "success"
            metadataDictionary["projects"][projectID]["backupCount"] += 1


def _UPDATE_ITEMS(metadataDictionary, backupSummary):

    today = datetime.now().strftime("%Y-%m-%d")

    for itemID in backupSummary["successfulItems"]:
        if itemID not in metadataDictionary["items"]:
            metadataDictionary["items"][itemID] = {
                "firstBackup": today,
                "lastBackup": today,
                "lastStatus": "success",
                "backupCount": 1,
            }

        else:
            metadataDictionary["items"][itemID]["lastBackup"] = today

            metadataDictionary["items"][itemID]["lastStatus"] = "success"
            metadataDictionary["items"][itemID]["backupCount"] += 1


def _WRITE_METADATA(metadataDictionary, metadataPath):

    with open(metadataPath, "w", encoding="utf-8") as file:
        json.dump(metadataDictionary, file, indent=4)


def _PRINT_METADATA_SUMMARY(backupSummary):

    print()

    print("=" * 80)

    print("METADATA UPDATED")

    print("=" * 80)

    print()

    print(f"Projects Updated : {len(backupSummary['successfulProjects'])}")

    print(f"Items Updated : {len(backupSummary['successfulItems'])}")

    print()

    print("=" * 80)

    print()
