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

        version="1.0"

):

    logDictionary = _BUILD_LOG(

        yamlDictionary,

        scheduleSummary,

        syncSummary,

        backupSummary,

        version

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

        version

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

            "version": version,

            "executionTime": executionTime,

            "executionStatus": executionStatus

        },

        "repository": {

            "repositoryPath":

            yamlDictionary["hardDisk"]

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