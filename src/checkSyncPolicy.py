from pathlib import Path

import json


# =============================================================================
# Public Function
# =============================================================================

def CHECK_SYNC_POLICY(

        yamlDictionary,

        scheduleSummary

):

    syncSummary = {

        "backupItems": [],

        "skippedItems": [],

        "itemPolicy": []

    }

    metadataDictionary = _READ_METADATA(

        yamlDictionary

    )

    dueProjects = set(

        scheduleSummary["dueProjects"]

    )

    for project in yamlDictionary["projects"]:

        projectID = project["projectID"]

        if projectID not in dueProjects:

            continue

        for item in project["items"]:

            _EVALUATE_ITEM(

                projectID,

                item,

                metadataDictionary,

                syncSummary

            )

    _PRINT_SYNC_SUMMARY(

        syncSummary

    )

    return syncSummary


# =============================================================================
# Read Metadata
# =============================================================================

def _READ_METADATA(

        yamlDictionary

):

    metadataPath = (

        Path(

            yamlDictionary["hardDisk"]

        )

        / "metadata"

        / "backupDatabase.json"

    )

    with open(

            metadataPath,

            "r",

            encoding="utf-8"

    ) as file:

        return json.load(

            file

        )


# =============================================================================
# Evaluate Item
# =============================================================================

def _EVALUATE_ITEM(

        projectID,

        item,

        metadataDictionary,

        syncSummary

):

    itemID = item["itemID"]

    if not item["itemEnabled"]:

        _ADD_ITEM(

            syncSummary,

            projectID,

            itemID,

            "SKIPPED",

            "Item disabled"

        )

        return

    syncPolicy = item["syncPolicy"]

    if syncPolicy == "always":

        _ADD_ITEM(

            syncSummary,

            projectID,

            itemID,

            "BACKUP",

            "always"

        )

        return

    if syncPolicy == "manual":

        _ADD_ITEM(

            syncSummary,

            projectID,

            itemID,

            "SKIPPED",

            "manual"

        )

        return

# =============================================================================
# Add Item
# =============================================================================

def _ADD_ITEM(

        syncSummary,

        projectID,

        itemID,

        status,

        reason

):

    itemData = {

        "projectID": projectID,

        "itemID": itemID,

        "status": status,

        "reason": reason

    }

    syncSummary["itemPolicy"].append(

        itemData

    )

    if status == "BACKUP":

        syncSummary["backupItems"].append(

            {

                "projectID": projectID,

                "itemID": itemID

            }

        )

    else:

        syncSummary["skippedItems"].append(

            {

                "projectID": projectID,

                "itemID": itemID

            }

        )


# =============================================================================
# Summary
# =============================================================================

def _PRINT_SYNC_SUMMARY(

        syncSummary

):

    print()

    print("=" * 80)

    print("SYNC POLICY SUMMARY")

    print("=" * 80)

    print()

    for item in syncSummary["itemPolicy"]:

        print(

            f"{item['itemID']}"

        )

        print(

            f"Status : {item['status']}"

        )

        print(

            f"Reason : {item['reason']}"

        )

        print()

    print("=" * 80)

    print()