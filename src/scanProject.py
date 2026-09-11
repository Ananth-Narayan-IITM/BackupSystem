# src/scanProject.py

from pathlib import Path


def scanProject(
        project
):
    """
    Scan the first-level contents of the project directory.

    The project directory is determined from the parent directory
    of the configured itemLocation values.

    Parameters
    ----------
    project : dict
        Parsed project dictionary from extractYAML.py.

    Returns
    -------
    dict
        Information about the project directory and its
        first-level files/directories.
    """

    projectID = project["projectID"]

    # ------------------------------------------------------------
    # Determine project location from itemLocation.
    # ------------------------------------------------------------

    projectLocations = set()

    for item in project["items"]:

        itemLocation = Path(
            item["itemLocation"]
        ).resolve()

        projectLocations.add(
            itemLocation.parent
        )

    # ------------------------------------------------------------
    # Verify that project contains items.
    # ------------------------------------------------------------

    if len(projectLocations) == 0:

        raise ValueError(
            f"Project '{projectID}' contains no items."
        )

    # ------------------------------------------------------------
    # Verify that all itemLocations belong to the same
    # project directory.
    # ------------------------------------------------------------

    if len(projectLocations) > 1:

        locations = "\n".join(
            f"    {location}"
            for location in sorted(
                projectLocations,
                key=str
            )
        )

        raise ValueError(
            f"\nProject '{projectID}' contains itemLocations "
            f"from multiple directories:\n\n"
            f"{locations}\n\n"
            f"All itemLocation values must belong to the "
            f"same project directory."
        )

    projectLocation = next(
        iter(projectLocations)
    )

    # ------------------------------------------------------------
    # Verify that project directory exists.
    # ------------------------------------------------------------

    if not projectLocation.is_dir():

        raise FileNotFoundError(
            f"\nProject directory does not exist:\n"
            f"{projectLocation}"
        )

    # ------------------------------------------------------------
    # Scan only the first level.
    # ------------------------------------------------------------

    items = []

    for entry in projectLocation.iterdir():

        if entry.is_dir():

            itemType = "directory"

        elif entry.is_file():

            itemType = "file"

        else:

            itemType = "other"

        items.append(
            {
                "name": entry.name,
                "path": str(
                    entry.resolve()
                ),
                "type": itemType,
            }
        )

    # ------------------------------------------------------------
    # Keep output deterministic.
    # ------------------------------------------------------------

    items.sort(
        key=lambda item: item["name"].lower()
    )

    # ------------------------------------------------------------
    # Return scan result.
    # ------------------------------------------------------------

    return {
        "projectID": projectID,
        "projectLocation": str(
            projectLocation
        ),
        "items": items,
    }


def printScanResult(
        scanResult
):
    """
    Print a compact representation of the project scan.
    """

    print()

    print("=" * 60)
    print("PROJECT SCAN")
    print("=" * 60)

    print(
        f"\nProject : "
        f"{scanResult['projectID']}"
    )

    print(
        f"\nProject location:"
        f"\n    {scanResult['projectLocation']}"
    )

    print("\nFirst-level items:")

    if not scanResult["items"]:

        print("    <none>")

    else:

        for item in scanResult["items"]:

            if item["type"] == "directory":

                symbol = "DIR  "

            elif item["type"] == "file":

                symbol = "FILE "

            else:

                symbol = "OTHER"

            print(
                f"    {symbol:<5}"
                f"{item['name']}"
            )

    print("=" * 60)

    print()
