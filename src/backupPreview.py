# src/backupPreview.py

import os
import sys


# ================================================================
# Terminal formatting
# ================================================================

_BOLD = "\033[1m"
_RESET = "\033[0m"

_WIDTH = 64


# ================================================================
# Public function
# ================================================================

def BACKUP_PREVIEW(comparisonResults):
    """
    Display the interactive backup preview and obtain
    permission to proceed with the backup.

    The preview enforces three safety rules:

    1. UNATTENDED items require correction and prevent backup.
    2. DISABLED items/projects are shown explicitly and require
       user confirmation before backup can proceed.
    3. Fully declared and enabled projects can proceed normally.

    Parameters
    ----------
    comparisonResults : list
        Comparison results returned by COMPARE_PROJECT().

    Returns
    -------
    bool
        True if the backup can proceed.
        False if the user cancels the backup.

    @throws SystemExit
        If the user terminates BackupSystem.
    """

    # ------------------------------------------------------------
    # UNATTENDED items are always a hard stop.
    # ------------------------------------------------------------

    if _HAS_UNATTENDED_ITEMS(comparisonResults):

        while True:
            _CLEAR_SCREEN()
            _PRINT_PROJECT_SUMMARY(comparisonResults)

            command = input(
                "\nEnter project number to inspect "
                "(number = inspect, exit = terminate): "
            ).strip().lower()

            if command == "exit":
                _TERMINATE()

            if command == "":
                continue

            try:
                projectNumber = int(command)
            except ValueError:
                continue

            if (
                projectNumber < 1
                or projectNumber > len(comparisonResults)
            ):
                continue

            _INSPECT_PROJECT(
                comparisonResults,
                projectNumber,
            )

        # --------------------------------------------------------
        # This point is never reached while unattended items exist.
        # --------------------------------------------------------

    # ------------------------------------------------------------
    # No unattended items.
    #
    # Allow the user to inspect the projects if disabled
    # items/projects exist.
    # ------------------------------------------------------------

    if _HAS_DISABLED_ENTRIES(comparisonResults):

        while True:
            _CLEAR_SCREEN()
            _PRINT_PROJECT_SUMMARY(comparisonResults)

            command = input(
                "\nEnter project number to inspect "
                "(number = inspect, exit = terminate): "
            ).strip().lower()

            if command == "exit":
                _TERMINATE()

            if command == "":
                continue

            # ----------------------------------------------------
            # User can finish the preview and move to confirmation.
            # ----------------------------------------------------

            if command == "continue":
                break

            try:
                projectNumber = int(command)
            except ValueError:
                continue

            if (
                projectNumber < 1
                or projectNumber > len(comparisonResults)
            ):
                continue

            _INSPECT_PROJECT(
                comparisonResults,
                projectNumber,
            )

        # --------------------------------------------------------
        # Final disabled-item/project confirmation.
        # --------------------------------------------------------

        if not _CONFIRM_DISABLED_BACKUP(comparisonResults):
            return False

    # ------------------------------------------------------------
    # No unattended and no disabled entries.
    #
    # Backup can proceed normally.
    # ------------------------------------------------------------

    _CLEAR_SCREEN()
    _PRINT_PROJECT_SUMMARY(comparisonResults)

    print()
    print("All filesystem items are declared in YAML.")
    print("All active items are enabled for backup.")

    return True


# ================================================================
# Main project dashboard
# ================================================================

def _PRINT_PROJECT_SUMMARY(comparisonResults):
    """
    Print the main backup preview dashboard.

    Project numbers are generated here and are therefore
    contiguous regardless of the original comparison indices.
    """

    print()
    print("=" * _WIDTH)
    print("BACKUP PREVIEW".center(_WIDTH))
    print("=" * _WIDTH)

    attentionProjects = []
    disabledProjects = []
    readyProjects = []

    for comparisonResult in comparisonResults:

        projectID = comparisonResult["projectID"]

        # --------------------------------------------------------
        # Entire project disabled.
        # --------------------------------------------------------

        if comparisonResult.get("projectEnabled") is False:
            disabledProjects.append(
                {
                    "projectID": projectID,
                    "reason": "PROJECT DISABLED",
                    "comparisonResult": comparisonResult,
                }
            )
            continue

        # --------------------------------------------------------
        # Count item statuses.
        # --------------------------------------------------------

        unattendedCount = _COUNT_STATUS(
            comparisonResult,
            "UNATTENDED",
        )

        disabledCount = _COUNT_STATUS(
            comparisonResult,
            "DISABLED",
        )

        if unattendedCount > 0:
            attentionProjects.append(
                {
                    "projectID": projectID,
                    "count": unattendedCount,
                    "comparisonResult": comparisonResult,
                }
            )

        elif disabledCount > 0:
            disabledProjects.append(
                {
                    "projectID": projectID,
                    "reason": f"{disabledCount} disabled item(s)",
                    "comparisonResult": comparisonResult,
                }
            )

        else:
            readyProjects.append(
                {
                    "projectID": projectID,
                    "comparisonResult": comparisonResult,
                }
            )

    # ------------------------------------------------------------
    # Dashboard counts.
    # ------------------------------------------------------------

    print()
    print(
        f"  Attention required : "
        f"{len(attentionProjects):>2} projects"
    )

    print(
        f"  Disabled           : "
        f"{len(disabledProjects):>2} projects"
    )

    print(
        f"  Ready              : "
        f"{len(readyProjects):>2} projects"
    )

    # ------------------------------------------------------------
    # Attention required.
    # ------------------------------------------------------------

    if attentionProjects:

        print()
        print(f"{_BOLD}ATTENTION REQUIRED{_RESET}")
        print()
        print(
            f"{'#':>3}   "
            f"{'PROJECT':<28} "
            f"UNATTENDED"
        )
        print("-" * _WIDTH)

        projectNumber = 1

        for entry in attentionProjects:

            print(
                f"{projectNumber:>3}   "
                f"{entry['projectID']:<28} "
                f"{entry['count']}"
            )

            projectNumber += 1

    # ------------------------------------------------------------
    # Disabled projects/items.
    # ------------------------------------------------------------

    if disabledProjects:

        print()
        print(f"{_BOLD}DISABLED / NOT ACTIVE{_RESET}")
        print()
        print(
            f"{'#':>3}   "
            f"{'PROJECT':<28} "
            f"STATUS"
        )
        print("-" * _WIDTH)

        # Continue numbering from the previous section.
        # If ATTENTION REQUIRED was not printed, start at 1.
        if not attentionProjects:
            projectNumber = 1

        for entry in disabledProjects:

            print(
                f"{projectNumber:>3}   "
                f"{entry['projectID']:<28} "
                f"{entry['reason']}"
            )

            projectNumber += 1

    # ------------------------------------------------------------
    # Ready projects.
    # ------------------------------------------------------------

    if readyProjects:

        print()
        print(f"{_BOLD}READY{_RESET}")
        print()
        print(
            f"{'#':>3}   "
            f"{'PROJECT':<28} "
            f"STATUS"
        )
        print("-" * _WIDTH)

        # Continue numbering from the previous section.
        # If this is the first displayed section, start at 1.
        if not attentionProjects and not disabledProjects:
            projectNumber = 1

        for entry in readyProjects:

            print(
                f"{projectNumber:>3}   "
                f"{entry['projectID']:<28} "
                f"READY"
            )

            projectNumber += 1

    # ------------------------------------------------------------
    # Navigation.
    # ------------------------------------------------------------

    print()
    print("-" * _WIDTH)

    if _HAS_UNATTENDED_ITEMS(comparisonResults):

        print(
            "[number] Inspect project"
            "                    [exit] Terminate"
        )

    elif _HAS_DISABLED_ENTRIES(comparisonResults):

        print(
            "[number] Inspect project"
            "    [continue] Continue"
        )

        print(
            "                                      "
            "[exit] Terminate"
        )

    else:

        print(
            "All checks passed."
            "                           [exit] Terminate"
        )

    print("-" * _WIDTH)


# ================================================================
# Project inspection
# ================================================================

def _INSPECT_PROJECT(comparisonResults, projectNumber):
    """
    Display the details of one project.

    The project number is based on the same ordering used
    by the main dashboard.
    """

    projectEntries = _GET_PROJECT_ENTRIES(
        comparisonResults
    )

    if (
        projectNumber < 1
        or projectNumber > len(projectEntries)
    ):
        return

    comparisonResult = projectEntries[
        projectNumber - 1
    ]

    while True:

        _CLEAR_SCREEN()

        projectID = comparisonResult["projectID"]

        print()
        print(
            f"BACKUP PREVIEW > {projectID}"
        )

        print()
        print("=" * _WIDTH)

        print(
            f"PROJECT: {projectID}".center(_WIDTH)
        )

        print("=" * _WIDTH)

        # --------------------------------------------------------
        # Project status.
        # --------------------------------------------------------

        if comparisonResult.get("projectEnabled") is False:

            projectStatus = "PROJECT DISABLED"

        elif _HAS_UNATTENDED_FOR_PROJECT(
            comparisonResult
        ):

            projectStatus = "ATTENTION REQUIRED"

        elif _COUNT_STATUS(
            comparisonResult,
            "DISABLED",
        ) > 0:

            projectStatus = "DISABLED ITEMS"

        else:

            projectStatus = "READY"

        backupCount = _COUNT_STATUS(
            comparisonResult,
            "BACKUP",
        )

        disabledCount = _COUNT_STATUS(
            comparisonResult,
            "DISABLED",
        )

        missingCount = _COUNT_STATUS(
            comparisonResult,
            "MISSING",
        )

        unattendedCount = _COUNT_STATUS(
            comparisonResult,
            "UNATTENDED",
        )

        print()
        print(
            f"  Status               : "
            f"{projectStatus}"
        )

        print(
            f"  Backup               : "
            f"{backupCount}"
        )

        print(
            f"  Disabled             : "
            f"{disabledCount}"
        )

        print(
            f"  Missing              : "
            f"{missingCount}"
        )

        print(
            f"  Unattended           : "
            f"{unattendedCount}"
        )

        # --------------------------------------------------------
        # Item table.
        # --------------------------------------------------------

        print()
        print(
            f"{'#':>3}   "
            f"{'ITEM':<32} "
            f"{'CLASSIFICATION':<16} "
            f"STATUS"
        )

        print("-" * _WIDTH)

        for index, item in enumerate(
            comparisonResult["items"],
            start=1,
        ):

            itemName = _GET_ITEM_NAME(item)

            yamlItem = item.get("yamlItem")

            if yamlItem is not None:
                classification = yamlItem.get(
                    "itemClassification",
                    "-",
                )
            else:
                classification = "-"

            print(
                f"{index:>3}   "
                f"{itemName:<32} "
                f"{classification:<16} "
                f"{item['status']}"
            )

        # --------------------------------------------------------
        # Navigation.
        # --------------------------------------------------------

        print()
        print("-" * _WIDTH)

        print(
            "[number] Inspect item"
            "   [b] Back"
            "   [exit] Terminate"
        )

        print("-" * _WIDTH)

        command = input("> ").strip().lower()

        if command == "exit":
            _TERMINATE()

        if command == "b":
            return

        try:
            itemNumber = int(command)
        except ValueError:
            continue

        if (
            itemNumber < 1
            or itemNumber > len(
                comparisonResult["items"]
            )
        ):
            continue

        _INSPECT_ITEM(
            comparisonResult,
            itemNumber,
        )


# ================================================================
# Item inspection
# ================================================================

def _INSPECT_ITEM(
    comparisonResult,
    itemNumber,
):
    """
    Display detailed information for one item.
    """

    item = comparisonResult["items"][
        itemNumber - 1
    ]

    itemName = _GET_ITEM_NAME(item)

    while True:

        _CLEAR_SCREEN()

        print()
        print(
            "BACKUP PREVIEW > "
            f"{comparisonResult['projectID']} > "
            f"{itemName}"
        )

        print()
        print("=" * _WIDTH)

        print(
            "ITEM DETAILS".center(_WIDTH)
        )

        print("=" * _WIDTH)

        print()
        print(
            f"  Project : "
            f"{comparisonResult['projectID']}"
        )

        print(
            f"  Item    : "
            f"{itemName}"
        )

        print(
            f"  Status  : "
            f"{item['status']}"
        )

        # --------------------------------------------------------
        # Filesystem information.
        # --------------------------------------------------------

        print()
        print("FILESYSTEM")
        print("-" * _WIDTH)

        print(
            f"Path : {item['itemLocation']}"
        )

        filesystemItem = item.get(
            "filesystemItem"
        )

        if filesystemItem is not None:

            itemType = filesystemItem.get(
                "type"
            )

            if itemType is not None:
                print(
                    f"Type : {itemType}"
                )

        # --------------------------------------------------------
        # YAML information.
        # --------------------------------------------------------

        yamlItem = item.get(
            "yamlItem"
        )

        if yamlItem is not None:

            print()
            print("YAML CONFIGURATION")
            print("-" * _WIDTH)

            for key, value in yamlItem.items():

                print(
                    f"{key:<20}: {value}"
                )

        # --------------------------------------------------------
        # Status-specific explanation.
        # --------------------------------------------------------

        print()
        print("BACKUP DECISION")
        print("-" * _WIDTH)

        status = item["status"]

        if status == "BACKUP":

            print(
                "This item is declared in YAML "
                "and enabled for backup."
            )

            print(
                "This item will be included in "
                "the backup."
            )

        elif status == "DISABLED":

            print(
                "This item is declared in YAML."
            )

            print(
                "itemEnabled is set to false."
            )

            print(
                "No backup will be taken for this item."
            )

        elif status == "UNATTENDED":

            print(
                "This filesystem item exists but "
                "is not declared in YAML."
            )

            print()
            print(
                "Backup cannot proceed until this "
                "item is intentionally handled."
            )

        elif status == "MISSING":

            print(
                "This item is declared in YAML but "
                "does not currently exist on the filesystem."
            )

            print(
                "No backup will be taken for this item."
            )

        elif status == "DECLARED_CONTAINER":

            print(
                "This is a structural filesystem "
                "container for declared YAML items."
            )

        elif status.startswith("DECLARED-"):

            declaringProject = status[
                len("DECLARED-"):
            ]

            print(
                "This filesystem item is declared "
                "by another project."
            )

            print(
                f"Declaring project : "
                f"{declaringProject}"
            )

        # --------------------------------------------------------
        # Navigation.
        # --------------------------------------------------------

        print()
        print("-" * _WIDTH)

        print(
            "[b] Back                                      "
            "[exit] Terminate"
        )

        print("-" * _WIDTH)

        command = input("> ").strip().lower()

        if command == "exit":
            _TERMINATE()

        if command == "b":
            return


# ================================================================
# Final disabled confirmation
# ================================================================

def _CONFIRM_DISABLED_BACKUP(comparisonResults):
    """
    Ask the user for explicit confirmation when declared
    projects or items are disabled.

    Returns
    -------
    bool
        True if the user explicitly confirms.
        False otherwise.
    """

    _CLEAR_SCREEN()

    print()
    print("=" * _WIDTH)

    print(
        "BACKUP DECISION".center(_WIDTH)
    )

    print("=" * _WIDTH)

    print()
    print(
        "All filesystem items are declared in YAML."
    )

    print()
    print(
        "However, some declared projects or items "
        "are disabled."
    )

    print()
    print("DISABLED / NOT ACTIVE")
    print("-" * _WIDTH)

    for comparisonResult in comparisonResults:

        projectID = comparisonResult[
            "projectID"
        ]

        if comparisonResult.get(
            "projectEnabled"
        ) is False:

            print()
            print(
                f"Project: {projectID}"
            )

            print(
                "    PROJECT DISABLED"
            )

            continue

        disabledItems = [
            item
            for item in comparisonResult["items"]
            if item["status"] == "DISABLED"
        ]

        if disabledItems:

            print()
            print(
                f"Project: {projectID}"
            )

            for item in disabledItems:

                print(
                    f"    {_GET_ITEM_NAME(item)}"
                )

    print()
    print("-" * _WIDTH)

    print(
        "These projects/items are intentionally "
        "excluded from backup."
    )

    print()
    print(
        "No backup will be taken for them."
    )

    print()
    print(
        "Proceed with backup of all ENABLED items?"
    )

    print()
    print(
        "    [y] Yes, proceed"
    )

    print(
        "    [n] No, cancel"
    )

    print()
    print("-" * _WIDTH)

    while True:

        command = input("> ").strip().lower()

        if command == "y":

            print()
            print(
                "Backup confirmed by user."
            )

            return True

        if command == "n":

            print()
            print(
                "Backup cancelled by user."
            )

            return False


# ================================================================
# Helper functions
# ================================================================

def _GET_PROJECT_ENTRIES(comparisonResults):
    """
    Return projects in the same order and numbering
    used by the dashboard.
    """

    attentionProjects = []
    disabledProjects = []
    readyProjects = []

    for comparisonResult in comparisonResults:

        if comparisonResult.get(
            "projectEnabled"
        ) is False:

            disabledProjects.append(
                comparisonResult
            )

            continue

        if _HAS_UNATTENDED_FOR_PROJECT(
            comparisonResult
        ):

            attentionProjects.append(
                comparisonResult
            )

        elif _COUNT_STATUS(
            comparisonResult,
            "DISABLED",
        ) > 0:

            disabledProjects.append(
                comparisonResult
            )

        else:

            readyProjects.append(
                comparisonResult
            )

    return (
        attentionProjects
        + disabledProjects
        + readyProjects
    )


def _GET_ITEM_NAME(item):
    """
    Return the display name of a comparison item.
    """

    if item.get("itemID") is not None:
        return item["itemID"]

    filesystemItem = item.get(
        "filesystemItem"
    )

    if filesystemItem is not None:

        return filesystemItem.get(
            "name",
            "<unknown>",
        )

    return "<unknown>"


def _COUNT_STATUS(
    comparisonResult,
    status,
):
    """
    Count items having the requested status.
    """

    return sum(
        1
        for item in comparisonResult["items"]
        if item["status"] == status
    )


def _HAS_UNATTENDED_FOR_PROJECT(
    comparisonResult,
):
    """
    Return True if a project contains an
    unattended item.
    """

    return _COUNT_STATUS(
        comparisonResult,
        "UNATTENDED",
    ) > 0


def _HAS_UNATTENDED_ITEMS(comparisonResults):
    """
    Return True if any project contains
    an unattended filesystem item.
    """

    return any(
        _HAS_UNATTENDED_FOR_PROJECT(
            comparisonResult
        )
        for comparisonResult in comparisonResults
    )


def _HAS_DISABLED_ENTRIES(comparisonResults):
    """
    Return True if any project or item is disabled.
    """

    for comparisonResult in comparisonResults:

        if comparisonResult.get(
            "projectEnabled"
        ) is False:

            return True

        if _COUNT_STATUS(
            comparisonResult,
            "DISABLED",
        ) > 0:

            return True

    return False


def _CLEAR_SCREEN():
    """
    Clear the terminal screen.
    """

    os.system("clear")


def _TERMINATE():
    """
    Terminate BackupSystem immediately.
    """

    print()
    print("BackupSystem terminated by user.")
    print()

    sys.exit(0)