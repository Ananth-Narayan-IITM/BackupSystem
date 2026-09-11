# src/initializeRepository.py

from pathlib import Path

from datetime import datetime

import json


def INITIALIZE_REPOSITORY(yamlDictionary):

    initializationSummary = {"repositoryReady": True, "createdFolders": []}

    repositoryPath = Path(yamlDictionary["hardDisk"])

    _CHECK_REPOSITORY(repositoryPath)

    _CREATE_FOLDERS(repositoryPath, initializationSummary)

    _INITIALIZE_METADATA(repositoryPath)

    _PRINT_INITIALIZATION_SUMMARY(initializationSummary)

    return initializationSummary


# =============================================================================
# Repository Checks
# =============================================================================


def _CHECK_REPOSITORY(repositoryPath):

    if not repositoryPath.exists():
        raise FileNotFoundError(
            "\n"
            "Repository not found.\n\n"
            f"{repositoryPath}\n\n"
            "Please connect HDD or "
            "correct hardDisk in YAML."
        )


# =============================================================================
# Folder Creation
# =============================================================================


def _CREATE_FOLDERS(repositoryPath, initializationSummary):

    requiredFolders = ["backups", "logs", "metadata"]

    for folderName in requiredFolders:
        folderPath = repositoryPath / folderName

        if not folderPath.exists():
            folderPath.mkdir(parents=True, exist_ok=True)

            initializationSummary["createdFolders"].append(folderName)


# =============================================================================
# Metadata Initialization
# =============================================================================


def _INITIALIZE_METADATA(repositoryPath):

    metadataFile = repositoryPath / "metadata" / "backupDatabase.json"

    if metadataFile.exists():
        return

    metadataDictionary = {
        "repository": {
            "createdOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lastExecution": "",
            "repositoryPath": str(repositoryPath),
        },
        "projects": {},
        "items": {},
    }

    with open(metadataFile, "w", encoding="utf-8") as file:
        json.dump(metadataDictionary, file, indent=4)


# =============================================================================
# Summary
# =============================================================================


def _PRINT_INITIALIZATION_SUMMARY(initializationSummary):

    print()

    print("=" * 80)

    print("REPOSITORY INITIALIZATION")

    print("=" * 80)

    print()

    if len(initializationSummary["createdFolders"]) == 0:
        print("Folders : Already exist")

    else:
        print("Folders Created :")

        for folder in initializationSummary["createdFolders"]:
            print(f"  - {folder}")

    print()

    print("Status : READY")

    print("=" * 80)

    print()
