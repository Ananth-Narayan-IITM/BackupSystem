from pathlib import Path

from datetime import datetime

import json


# =============================================================================
# Public Function
# =============================================================================

def LOGGER(

        yamlDictionary,

        scheduleSummary,

        syncSummary,

        backupSummary,

        _BACKUP_SYSTEM_VERSION,

        spaceSummary

):

    logDictionary = _BUILD_LOG(

        yamlDictionary,

        scheduleSummary,

        syncSummary,

        backupSummary,

        _BACKUP_SYSTEM_VERSION,

        spaceSummary

    )

    _WRITE_LOG(

        yamlDictionary["hardDisk"],

        logDictionary

    )

    _WRITE_LOG(

        yamlDictionary["localPC"],

        logDictionary

    )

    _PRINT_LOG_SUMMARY()

# =============================================================================
# Build Log
# =============================================================================

def _BUILD_LOG(

        yamlDictionary,

        scheduleSummary,

        syncSummary,

        backupSummary,

        _BACKUP_SYSTEM_VERSION,

        spaceSummary

):

    executionTime = datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    )

    executionStatus = (

        "success"

        if len(

            backupSummary["failedItems"]

        ) == 0

        else "partial"

    )

    return {

        "execution": {

            "version": _BACKUP_SYSTEM_VERSION,

            "executionTime": executionTime,

            "executionStatus": executionStatus

        },

        "repository": {

            "repositoryPath":

            yamlDictionary["hardDisk"]

        },

        "hddSpace": {

            "status": "PASS",

            "totalSpace": _FORMAT_SIZE(

                spaceSummary["total"]

            ),

            "usedSpace": _FORMAT_SIZE(

                spaceSummary["used"]

            ),

            "freeSpace": _FORMAT_SIZE(

                spaceSummary["free"]

            ),

            "requiredMargin": _FORMAT_SIZE(

                spaceSummary["margin"]

            ),

            "availableAfterMargin": _FORMAT_SIZE(

                spaceSummary["availableAfterMargin"]

            )

        },

        "schedule": {

            "dueProjects":

            scheduleSummary["dueProjects"],

            "skippedProjects":

            scheduleSummary["skippedProjects"]

        },

        "sync": {

            "backupItems": [

                item["itemID"]

                for item in

                syncSummary["backupItems"]

            ],

            "skippedItems": [

                item["itemID"]

                for item in

                syncSummary["skippedItems"]

            ]

        },

        "backup": {

            "successfulItems":

            backupSummary["successfulItems"],

            "failedItems":

            backupSummary["failedItems"]

        }

    }


# =============================================================================
# Write Log
# =============================================================================

def _WRITE_LOG(

        basePath,

        logDictionary

):

    now = datetime.now()

    month = now.strftime(

        "%b-%Y"

    )

    filename = now.strftime(

        "backup_%Y%m%d_%H%M%S.json"

    )

    logFolder = (

        Path(basePath)

        / "logs"

        / month

    )

    logFolder.mkdir(

        parents=True,

        exist_ok=True

    )

    logFile = (

        logFolder

        / filename

    )

    with open(

            logFile,

            "w",

            encoding="utf-8"

    ) as file:

        json.dump(

            logDictionary,

            file,

            indent=4

        )


# =============================================================================
# Print Summary
# =============================================================================

def _PRINT_LOG_SUMMARY():

    print()

    print("=" * 80)

    print("LOG FILE GENERATED")

    print("=" * 80)

    print()

def _FORMAT_SIZE(

        size

):

    if size >= 1024**3:

        return f"{size / 1024**3:.2f} GB"

    elif size >= 1024**2:

        return f"{size / 1024**2:.2f} MB"

    elif size >= 1024:

        return f"{size / 1024:.2f} KB"

    else:

        return f"{size} B"