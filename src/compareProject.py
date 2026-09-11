# src/compareProject.py

from pathlib import Path


def COMPARE_PROJECT(
        project,
        scanResult
):
    """
    Compare project YAML items with the first-level
    filesystem scan.

    The comparison is performed using itemLocation.

    Parameters
    ----------
    project : dict
        Parsed project dictionary from extractYAML.py.

    scanResult : dict
        Result returned by scanProject.py.

    Returns
    -------
    dict
        Comparison result for the project.
    """

    projectID = project["projectID"]

    # ------------------------------------------------------------
    # Build dictionary of YAML items using itemLocation.
    # ------------------------------------------------------------

    yamlItems = {}

    for item in project["items"]:

        itemLocation = str(
            Path(
                item["itemLocation"]
            ).resolve()
        )

        yamlItems[itemLocation] = item

    # ------------------------------------------------------------
    # Build dictionary of filesystem items using their path.
    # ------------------------------------------------------------

    filesystemItems = {}

    for item in scanResult["items"]:

        itemLocation = str(
            Path(
                item["path"]
            ).resolve()
        )

        filesystemItems[itemLocation] = item

    # ------------------------------------------------------------
    # Compare YAML items against filesystem items.
    # ------------------------------------------------------------

    comparisonItems = []

    for itemLocation, item in yamlItems.items():

        if itemLocation in filesystemItems:

            if item["itemEnabled"]:

                status = "BACKUP"

            else:

                status = "DISABLED"

            comparisonItems.append(
                {
                    "itemID": item["itemID"],
                    "itemLocation": itemLocation,
                    "status": status,
                    "yamlItem": item,
                    "filesystemItem": filesystemItems[
                        itemLocation
                    ],
                }
            )

        else:

            comparisonItems.append(
                {
                    "itemID": item["itemID"],
                    "itemLocation": itemLocation,
                    "status": "MISSING",
                    "yamlItem": item,
                    "filesystemItem": None,
                }
            )

    # ------------------------------------------------------------
    # Find filesystem items which are not declared in YAML.
    # ------------------------------------------------------------

    for itemLocation, filesystemItem in filesystemItems.items():

        if itemLocation not in yamlItems:

            comparisonItems.append(
                {
                    "itemID": None,
                    "itemLocation": itemLocation,
                    "status": "UNATTENDED",
                    "yamlItem": None,
                    "filesystemItem": filesystemItem,
                }
            )

    # ------------------------------------------------------------
    # Determine overall project status.
    # ------------------------------------------------------------

    unattendedItems = [
        item
        for item in comparisonItems
        if item["status"] == "UNATTENDED"
    ]

    if unattendedItems:

        projectStatus = "ATTENTION"

    else:

        projectStatus = "OK"

    # ------------------------------------------------------------
    # Return comparison result.
    # ------------------------------------------------------------

    return {
        "projectID": projectID,
        "projectStatus": projectStatus,
        "items": comparisonItems,
    }


def PRINT_COMPARISON_RESULT(
        comparisonResult
):
    """
    Print a compact comparison result.
    """

    print()

    print("=" * 60)
    print("PROJECT COMPARISON")
    print("=" * 60)

    print(
        f"\nProject : "
        f"{comparisonResult['projectID']}"
    )

    print("\nItems:")

    if not comparisonResult["items"]:

        print("    <none>")

    else:

        for item in comparisonResult["items"]:

            print(
                f"    {item['status']:<11}"
                f"{item['itemLocation']}"
            )

    print(
        f"\nStatus  : "
        f"{comparisonResult['projectStatus']}"
    )

    print("=" * 60)

    print()
