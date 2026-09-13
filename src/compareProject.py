# src/compareProject.py

from pathlib import Path


def _BUILD_GLOBAL_DECLARATIONS(allProjects):
    """
    Build a filesystem declaration map for all projects.

    Parameters
    ----------
    allProjects : list[dict]
        All parsed projects from the main YAML structure.

    Returns
    -------
    dict
        Dictionary mapping filesystem paths to project
        declarations.
    """

    declarations = {}

    for project in allProjects:

        projectID = project["projectID"]

        for item in project["items"]:

            itemLocation = Path(
                item["itemLocation"]
            ).resolve()

            pathString = str(
                itemLocation
            )

            if pathString not in declarations:

                declarations[pathString] = []

            declarations[pathString].append(
                {
                    "projectID": projectID,
                    "item": item,
                }
            )

    return declarations


def _GET_DECLARING_PROJECT(
    filesystemPath,
    currentProjectID,
    globalDeclarations,
):
    """
    Determine whether a filesystem path is declared by another
    project or covered by a directory declared by another project.

    Parameters
    ----------
    filesystemPath : Path
        Filesystem path being checked.

    currentProjectID : str
        ID of the project currently being compared.

    globalDeclarations : dict
        Global declaration map.

    Returns
    -------
    str or None
        Project ID of another declaring project, or None.
    """

    # ------------------------------------------------------------
    # First check exact declarations.
    # ------------------------------------------------------------

    exactDeclarations = globalDeclarations.get(
        str(filesystemPath),
        [],
    )

    for declaration in exactDeclarations:

        if declaration["projectID"] != currentProjectID:

            return declaration["projectID"]

    # ------------------------------------------------------------
    # Check whether the filesystem path is inside a directory
    # declared by another project.
    # ------------------------------------------------------------

    for declaredPath, declarations in globalDeclarations.items():

        declaredDirectory = Path(
            declaredPath
        )

        if not declaredDirectory.is_dir():

            continue

        if filesystemPath == declaredDirectory:

            continue

        try:

            filesystemPath.relative_to(
                declaredDirectory
            )

        except ValueError:

            continue

        for declaration in declarations:

            if declaration["projectID"] != currentProjectID:

                return declaration["projectID"]

    return None


def COMPARE_PROJECT(
    project,
    scanResult,
    allProjects,
):
    """
    Compare project YAML declarations with the filesystem.

    A directory declared in YAML covers its entire subtree.

    Filesystem items declared by another project are reported as:

        DECLARED-<projectID>

    This allows shared filesystem locations to remain visible
    without incorrectly classifying them as unattended.

    Parameters
    ----------
    project : dict
        Parsed project dictionary for the current project.

    scanResult : dict
        Result returned by scanProject().

    allProjects : list[dict]
        All parsed projects from the YAML configuration.

    Returns
    -------
    dict
        Comparison result for the project.
    """

    projectID = project["projectID"]

    # ------------------------------------------------------------
    # Build global declaration map.
    # ------------------------------------------------------------

    globalDeclarations = _BUILD_GLOBAL_DECLARATIONS(
        allProjects
    )

    # ------------------------------------------------------------
    # Build dictionary of current project's YAML items.
    # ------------------------------------------------------------

    yamlItems = {}

    for item in project["items"]:

        itemLocation = Path(
            item["itemLocation"]
        ).resolve()

        yamlItems[str(itemLocation)] = item

    # ------------------------------------------------------------
    # Build dictionary of current project's filesystem scan.
    # ------------------------------------------------------------

    filesystemItems = {}

    for item in scanResult["items"]:

        itemLocation = Path(
            item["path"]
        ).resolve()

        filesystemItems[str(itemLocation)] = item

    # ------------------------------------------------------------
    # Determine current project's declared directories.
    #
    # These directories cover their entire subtree.
    # ------------------------------------------------------------

    yamlDirectories = set()

    for itemLocation, item in yamlItems.items():

        path = Path(
            itemLocation
        )

        if path.is_dir():

            yamlDirectories.add(
                path
            )

    # ------------------------------------------------------------
    # Compare YAML items.
    # ------------------------------------------------------------

    comparisonItems = []

    for itemLocation, item in yamlItems.items():

        yamlPath = Path(
            itemLocation
        )

        # --------------------------------------------------------
        # YAML item exists.
        #
        # This includes directories that are themselves scan
        # scopes and files that are not scan scopes.
        # --------------------------------------------------------

        if yamlPath.exists():

            if item["itemEnabled"]:

                status = "BACKUP"

            else:

                status = "DISABLED"

            filesystemItem = {
                "name": yamlPath.name,
                "path": str(yamlPath),
                "type": (
                    "directory"
                    if yamlPath.is_dir()
                    else "file"
                ),
            }

            comparisonItems.append(
                {
                    "itemID": item["itemID"],
                    "itemLocation": itemLocation,
                    "status": status,
                    "yamlItem": item,
                    "filesystemItem": filesystemItem,
                }
            )

            continue

        # --------------------------------------------------------
        # YAML item does not exist.
        # --------------------------------------------------------

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
    # Compare scanned filesystem items.
    # ------------------------------------------------------------

    for itemLocation, filesystemItem in filesystemItems.items():

        filesystemPath = Path(
            itemLocation
        )

        # --------------------------------------------------------
        # Exact current-project YAML declaration.
        # --------------------------------------------------------

        if itemLocation in yamlItems:

            continue

        # --------------------------------------------------------
        # Current project's declared directory covers this item.
        #
        # This means the item does not need its own YAML entry.
        # --------------------------------------------------------

        insideCurrentProjectDirectory = False

        for yamlDirectory in yamlDirectories:

            if filesystemPath == yamlDirectory:

                continue

            try:

                filesystemPath.relative_to(
                    yamlDirectory
                )

                insideCurrentProjectDirectory = True

                break

            except ValueError:

                pass

        if insideCurrentProjectDirectory:

            continue

        # --------------------------------------------------------
        # Check whether another project has declared this item
        # or a parent directory containing it.
        # --------------------------------------------------------

        declaringProject = _GET_DECLARING_PROJECT(
            filesystemPath,
            projectID,
            globalDeclarations,
        )

        if declaringProject is not None:

            status = (
                f"DECLARED-{declaringProject}"
            )

            comparisonItems.append(
                {
                    "itemID": None,
                    "itemLocation": itemLocation,
                    "status": status,
                    "yamlItem": None,
                    "filesystemItem": filesystemItem,
                }
            )

            continue

        # --------------------------------------------------------
        # Check whether this filesystem directory contains a
        # YAML declaration belonging to the current project.
        #
        # Such a directory is a structural container.
        # --------------------------------------------------------

        containsYamlItem = False

        if filesystemItem["type"] == "directory":

            for yamlLocation in yamlItems:

                yamlPath = Path(
                    yamlLocation
                )

                try:

                    yamlPath.relative_to(
                        filesystemPath
                    )

                    containsYamlItem = True

                    break

                except ValueError:

                    pass

        # --------------------------------------------------------
        # Determine filesystem status.
        # --------------------------------------------------------

        if containsYamlItem:

            status = "DECLARED_CONTAINER"

        else:

            status = "UNATTENDED"

        comparisonItems.append(
            {
                "itemID": None,
                "itemLocation": itemLocation,
                "status": status,
                "yamlItem": None,
                "filesystemItem": filesystemItem,
            }
        )

    # ------------------------------------------------------------
    # Determine overall project status.
    #
    # DECLARED-<projectID> is not an issue because another
    # project explicitly owns the item.
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


def PRINT_COMPARISON_RESULT(comparisonResult):
    """
    Print a compact representation of the project comparison.

    Parameters
    ----------
    comparisonResult : dict
        Result returned by COMPARE_PROJECT().
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
                f"    {item['status']:<25}"
                f"{item['itemLocation']}"
            )

    print(
        f"\nStatus  : "
        f"{comparisonResult['projectStatus']}"
    )

    print("=" * 60)

    print()