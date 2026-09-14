from pathlib import Path

import subprocess


# =============================================================================
# Public Function
# =============================================================================


def BACKUP_ENGINE(yamlDictionary, syncSummary):

    backupSummary = {
        "successfulProjects": [],
        "failedProjects": [],
        "successfulItems": [],
        "failedItems": [],
    }

    for backupItem in syncSummary["backupItems"]:
        projectID = backupItem["projectID"]

        itemID = backupItem["itemID"]

        item = _GET_ITEM(yamlDictionary, projectID, itemID)

        destination = _CREATE_PROJECT_FOLDER(yamlDictionary, projectID)

        success = _COPY_ITEM(item, destination)

        if success:
            backupSummary["successfulItems"].append(itemID)

            if projectID not in backupSummary["successfulProjects"]:
                backupSummary["successfulProjects"].append(projectID)

        else:
            backupSummary["failedItems"].append(itemID)

            if projectID not in backupSummary["failedProjects"]:
                backupSummary["failedProjects"].append(projectID)

    _PRINT_BACKUP_SUMMARY(backupSummary)

    return backupSummary


def _GET_ITEM(yamlDictionary, projectID, itemID):

    for project in yamlDictionary["projects"]:
        if project["projectID"] != projectID:
            continue

        for item in project["items"]:
            if item["itemID"] == itemID:
                return item

    raise ValueError(f"{itemID} not found.")


def _CREATE_PROJECT_FOLDER(yamlDictionary, projectID):

    destination = Path(yamlDictionary["hardDisk"]) / "backups" / projectID

    destination.mkdir(parents=True, exist_ok=True)

    return destination


def _COPY_ITEM(item, destination):

    source = Path(item["itemLocation"])

    destination = destination / item["itemID"]

    destination.mkdir(parents=True, exist_ok=True)

    command = ["rsync", "-a","--no-owner","--no-group","--progress"]

    for folder in item["excludeFolders"]:
        command.append(f"--exclude={folder}")

    for file in item["excludeFiles"]:
        command.append(f"--exclude={file}")

    # Important:
    # Trailing '/' copies contents only

    if source.is_dir():
        source = str(source) + "/"

    else:
        source = str(source)

    destination = str(destination) + "/"

    command.extend([source, destination])

    try:
        subprocess.run(command, check=True)

        return True

    except subprocess.CalledProcessError:
        return False


def _PRINT_BACKUP_SUMMARY(backupSummary):

    print()

    print("=" * 80)

    print("BACKUP SUMMARY")

    print("=" * 80)

    print()

    print(f"Successful Items : {len(backupSummary['successfulItems'])}")

    for item in backupSummary["successfulItems"]:
        print(f"  - {item}")

    print()

    print(f"Failed Items : {len(backupSummary['failedItems'])}")

    for item in backupSummary["failedItems"]:
        print(f"  - {item}")

    print()

    print("=" * 80)

    print()
