from pathlib import Path

import subprocess


# =============================================================================
# Public Function
# =============================================================================

def BACKUP_ENGINE(

        yamlDictionary,

        syncSummary

):

    backupSummary = {

        "successfulProjects": [],

        "failedProjects": [],

        "successfulItems": [],

        "failedItems": []

    }

    for backupItem in syncSummary["backupItems"]:

        projectID = backupItem["projectID"]

        itemID = backupItem["itemID"]

        item = _GET_ITEM(

            yamlDictionary,

            projectID,

            itemID

        )

        destination = _CREATE_PROJECT_FOLDER(

            yamlDictionary,

            projectID

        )

        success = _COPY_ITEM(

            item,

            destination

        )

        if success:

            backupSummary["successfulItems"].append(

                itemID

            )

            if projectID not in backupSummary[

                    "successfulProjects"

            ]:

                backupSummary[

                    "successfulProjects"

                ].append(

                    projectID

                )

        else:

            backupSummary["failedItems"].append(

                itemID

            )

            if projectID not in backupSummary[

                    "failedProjects"

            ]:

                backupSummary[

                    "failedProjects"

                ].append(

                    projectID

                )

    _PRINT_BACKUP_SUMMARY(

        backupSummary

    )

    return backupSummary

def _GET_ITEM(

        yamlDictionary,

        projectID,

        itemID

):

    for project in yamlDictionary["projects"]:

        if project["projectID"] != projectID:

            continue

        for item in project["items"]:

            if item["itemID"] == itemID:

                return item

    raise ValueError(

        f"{itemID} not found."

    )

def _CREATE_PROJECT_FOLDER(

        yamlDictionary,

        projectID

):

    destination = (

        Path(

            yamlDictionary["hardDisk"]

        )

        / "backups"

        / projectID

    )

    destination.mkdir(

        parents=True,

        exist_ok=True

    )

    return destination

from pathlib import Path


def _GET_LATEST_TIME_FOLDER(

        sourcePath

):

    latestFolder = None

    latestValue = -1.0

    for folder in sourcePath.iterdir():

        if not folder.is_dir():

            continue

        try:

            value = float(

                folder.name

            )

        except ValueError:

            continue

        if value > latestValue:

            latestValue = value

            latestFolder = folder.name

    return latestFolder
def _COPY_LATEST_TIME(

        sourcePath,

        destinationPath,

        latestTime

):

    latestSource = (

        sourcePath /

        latestTime

    )

    command = [

        "rsync",

        "-a",

        str(

            latestSource

        ),

        str(

            destinationPath

        )

    ]

    subprocess.run(

        command,

        check=True

    )
def _COPY_ITEM(

        item,

        destination

):

    sourcePath = Path(

        item["itemLocation"]

    )

    destinationPath = (

        destination /

        item["itemID"]

    )

    destinationPath.mkdir(

        parents=True,

        exist_ok=True

    )

    command = [

        "rsync",

        "-a"

    ]

    for folder in item["excludeFolders"]:

        command.append(

            f"--exclude={folder}"

        )

    for file in item["excludeFiles"]:

        command.append(

            f"--exclude={file}"

        )

    # rsync copies contents only when source ends with '/'

    if sourcePath.is_dir():

        source = str(

            sourcePath

        ) + "/"

    else:

        source = str(

            sourcePath

        )

    destination = str(

        destinationPath

    ) + "/"

    command.extend([

        source,

        destination

    ])

    try:

        subprocess.run(

            command,

            check=True

        )

        # --------------------------------------------------
        # Copy latest OpenFOAM time folder
        # --------------------------------------------------

        if item.get(

                "retainLatestTime",

                False

        ):

            latestTime = _GET_LATEST_TIME_FOLDER(

                sourcePath

            )

            if latestTime is not None:

                _COPY_LATEST_TIME(

                    sourcePath,

                    destinationPath,

                    latestTime

                )

        return True

    except subprocess.CalledProcessError:

        return False
def _PRINT_BACKUP_SUMMARY(

        backupSummary

):

    print()

    print("=" * 80)

    print("BACKUP SUMMARY")

    print("=" * 80)

    print()

    print(

        f"Successful Items : "

        f"{len(backupSummary['successfulItems'])}"

    )

    for item in backupSummary["successfulItems"]:

        print(

            f"  - {item}"

        )

    print()

    print(

        f"Failed Items : "

        f"{len(backupSummary['failedItems'])}"

    )

    for item in backupSummary["failedItems"]:

        print(

            f"  - {item}"

        )

    print()

    print("=" * 80)

    print()
