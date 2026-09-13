# src/scanProject.py

from pathlib import Path


def _GET_SCAN_SCOPES(project):
    """
    Determine the filesystem directories that should be scanned
    for a project.

    A directory containing multiple YAML declarations is treated
    as a project scan scope.

    A single isolated file declaration does not cause its parent
    directory to be scanned.

    A single explicitly declared directory is itself treated as
    a scan scope because the directory declaration covers its
    entire subtree.

    Parameters
    ----------
    project : dict
        Parsed project dictionary from extractYAML.py.

    Returns
    -------
    list[Path]
        List of directories that should be scanned.
    """

    scanScopes = []

    declarationsByParent = {}

    # ------------------------------------------------------------
    # Group all YAML declarations by their parent directory.
    # ------------------------------------------------------------

    for item in project["items"]:

        itemLocation = Path(
            item["itemLocation"]
        ).resolve()

        parentDirectory = itemLocation.parent

        if parentDirectory not in declarationsByParent:

            declarationsByParent[parentDirectory] = []

        declarationsByParent[parentDirectory].append(
            itemLocation
        )

    # ------------------------------------------------------------
    # Determine scan scopes.
    # ------------------------------------------------------------

    for parentDirectory, declarations in declarationsByParent.items():

        # --------------------------------------------------------
        # Multiple declarations in the same directory.
        #
        # Example:
        #
        # a_EHD/
        #   a0R8
        #   a0R9
        #   a1R8
        #
        # Therefore a_EHD/ must be scanned.
        # --------------------------------------------------------

        if len(declarations) >= 2:

            scanScopes.append(
                parentDirectory
            )

            continue

        # --------------------------------------------------------
        # Only one declaration exists in this directory.
        # --------------------------------------------------------

        declaration = declarations[0]

        # --------------------------------------------------------
        # If the single declaration is a directory, the directory
        # itself is a valid scan scope.
        #
        # Example:
        #
        # Bibliography_Files/
        #
        # Its entire subtree is covered by the YAML item.
        # --------------------------------------------------------

        if declaration.is_dir():

            scanScopes.append(
                declaration
            )

        # --------------------------------------------------------
        # If the single declaration is a file, do NOT scan its
        # parent directory.
        #
        # Example:
        #
        # /home/user/.bashrc
        #
        # We must not scan /home/user/.
        # --------------------------------------------------------

    # ------------------------------------------------------------
    # Remove duplicate scopes.
    # ------------------------------------------------------------

    scanScopes = list(
        set(scanScopes)
    )

    # ------------------------------------------------------------
    # Remove nested scopes.
    #
    # If:
    #
    #   project/
    #   project/case/
    #
    # are both scan scopes, project/ already covers case/.
    # ------------------------------------------------------------

    finalScopes = []

    for scope in sorted(
        scanScopes,
        key=lambda path: len(path.parts),
    ):

        alreadyCovered = False

        for existingScope in finalScopes:

            try:

                scope.relative_to(
                    existingScope
                )

                alreadyCovered = True

                break

            except ValueError:

                pass

        if not alreadyCovered:

            finalScopes.append(
                scope
            )

    return finalScopes

def scanProject(project):
    """
    Scan the filesystem scopes associated with a project.

    YAML-declared directories define scan scopes. YAML-declared
    files are not used to infer a parent directory because doing
    so could cause unrelated filesystem items to be classified
    as unattended.

    The scan is limited to the first level of each scan scope.
    It does not recursively inspect project items.

    Parameters
    ----------
    project : dict
        Parsed project dictionary from extractYAML.py.

    Returns
    -------
    dict
        Project scan information containing the scan scopes and
        first-level filesystem items.

    Raises
    ------
    FileNotFoundError
        If a configured directory scan scope does not exist.

    ValueError
        If the project contains no valid filesystem scan scope.
    """

    projectID = project["projectID"]

    # ------------------------------------------------------------
    # Determine scan scopes.
    # ------------------------------------------------------------

    scanScopes = _GET_SCAN_SCOPES(
        project
    )

    # ------------------------------------------------------------
    # Verify scan scopes.
    # ------------------------------------------------------------

    for scanScope in scanScopes:

        if not scanScope.exists():

            raise FileNotFoundError(
                f"\nScan scope does not exist:\n"
                f"{scanScope}"
            )

        if not scanScope.is_dir():

            raise NotADirectoryError(
                f"\nScan scope is not a directory:\n"
                f"{scanScope}"
            )

    # ------------------------------------------------------------
    # A project containing only file declarations has no
    # directory that should be scanned.
    #
    # This is intentional.
    # ------------------------------------------------------------

    items = []

    # ------------------------------------------------------------
    # Scan each scope.
    # ------------------------------------------------------------

    for scanScope in scanScopes:

        for entry in scanScope.iterdir():

            if entry.is_dir():

                itemType = "directory"

            elif entry.is_file():

                itemType = "file"

            else:

                itemType = "other"

            items.append(
                {
                    "name": entry.name,
                    "path": str(entry.resolve()),
                    "type": itemType,
                    "scanScope": str(scanScope),
                }
            )

    # ------------------------------------------------------------
    # Remove duplicates.
    #
    # This protects against overlapping scan scopes.
    # ------------------------------------------------------------

    uniqueItems = {}

    for item in items:

        uniqueItems[item["path"]] = item

    items = list(
        uniqueItems.values()
    )

    # ------------------------------------------------------------
    # Keep output deterministic.
    # ------------------------------------------------------------

    items.sort(
        key=lambda item: item["path"].lower()
    )

    # ------------------------------------------------------------
    # Return scan result.
    # ------------------------------------------------------------

    return {
        "projectID": projectID,
        "scanScopes": [
            str(scope)
            for scope in scanScopes
        ],
        "items": items,
    }


def printScanResult(scanResult):
    """
    Print a compact representation of the project scan.

    Parameters
    ----------
    scanResult : dict
        Result returned by scanProject().
    """

    print()

    print("=" * 60)
    print("PROJECT SCAN")
    print("=" * 60)

    print(
        f"\nProject : "
        f"{scanResult['projectID']}"
    )

    print("\nScan scopes:")

    if not scanResult["scanScopes"]:

        print("    <none>")

    else:

        for scanScope in scanResult["scanScopes"]:

            print(
                f"    {scanScope}"
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