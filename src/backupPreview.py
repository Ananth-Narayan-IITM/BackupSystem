# src/backupPreview.py

import sys


# ================================================================
# Terminal formatting
# ================================================================

_BOLD = "\033[1m"
_RESET = "\033[0m"


def BACKUP_PREVIEW(
        comparisonResults
):
    """
    Display the backup preview.

    If no unattended items are present, the backup proceeds
    automatically.

    If unattended items are present, the user must inspect
    the affected projects before the backup can proceed.

    Parameters
    ----------
    comparisonResults : list
        Comparison results returned by COMPARE_PROJECT().

    Returns
    -------
    bool
        True if the backup can proceed.
    """

    # ------------------------------------------------------------
    # Check for unattended items.
    # ------------------------------------------------------------

    if not _HAS_UNATTENDED_ITEMS(
            comparisonResults
    ):

        _PRINT_PROJECT_SUMMARY(
            comparisonResults
        )

        print()

        print(
            "All projects are properly declared in YAML."
        )
        backupComment = GET_BACKUP_COMMENT()

        print()

        print(
            "Proceeding with backup..."
        )

        print()

        return backupComment

    # ------------------------------------------------------------
    # Attention is required.
    #
    # Enter interactive preview mode.
    # ------------------------------------------------------------

    while True:

        _PRINT_PROJECT_SUMMARY(
            comparisonResults
        )

        command = input(
            "\nEnter project number to inspect "
            "(number = inspect, exit = terminate): "
        ).strip().lower()

        # --------------------------------------------------------
        # Terminate complete BackupSystem.
        # --------------------------------------------------------

        if command == "exit":

            print(
                "\nBackupSystem terminated by user.\n"
            )

            sys.exit(0)

        # --------------------------------------------------------
        # Empty input.
        # --------------------------------------------------------

        if command == "":

            print(
                "\nPlease enter a project number "
                "or type 'exit'."
            )

            continue

        # --------------------------------------------------------
        # Convert input to project number.
        # --------------------------------------------------------

        try:

            projectNumber = int(command)

        except ValueError:

            print(
                "\nInvalid input."
            )

            continue

        # --------------------------------------------------------
        # Verify project number.
        # --------------------------------------------------------

        if (
            projectNumber < 1
            or projectNumber > len(
                comparisonResults
            )
        ):

            print(
                "\nInvalid project number."
            )

            continue

        # --------------------------------------------------------
        # Inspect selected project.
        # --------------------------------------------------------

        _INSPECT_PROJECT(
            comparisonResults,
            projectNumber
        )


def _PRINT_PROJECT_SUMMARY(
        comparisonResults
):
    """
    Print the top-level project summary.
    """

    print()

    print("=" * 60)
    print("BACKUP PREVIEW")
    print("=" * 60)

    attentionProjects = []

    for index, comparisonResult in enumerate(
            comparisonResults,
            start=1
    ):

        unattendedCount = sum(
            1
            for item in comparisonResult["items"]
            if item["status"] == "UNATTENDED"
        )

        if unattendedCount > 0:

            attentionProjects.append(
                (
                    index,
                    comparisonResult["projectID"],
                    unattendedCount
                )
            )

    # ------------------------------------------------------------
    # Projects requiring attention.
    # ------------------------------------------------------------

    if attentionProjects:

        print()

        print(
            f"{_BOLD}"
            "ATTENTION REQUIRED"
            f"{_RESET}"
        )

        print()

        print(
            f"{'#':>3}   "
            f"{'PROJECT':<20} "
            f"ISSUE"
        )

        print("-" * 45)

        for (
                projectNumber,
                projectID,
                unattendedCount
        ) in attentionProjects:

            print(
                f"{projectNumber:>3}   "
                f"{projectID:<20} "
                f"{unattendedCount} unattended"
            )

    else:

        print()

        print(
            f"{_BOLD}"
            "NO ATTENTION REQUIRED"
            f"{_RESET}"
        )

    # ------------------------------------------------------------
    # Projects without unattended items.
    # ------------------------------------------------------------

    otherProjectCount = (
        len(comparisonResults)
        - len(attentionProjects)
    )

    if otherProjectCount > 0:

        print()

        print(
            "ALL OTHER PROJECTS"
        )

        print()

        print(
            f"{otherProjectCount} projects OK"
        )

    print()

    print("=" * 60)


def _INSPECT_PROJECT(
        comparisonResults,
        projectNumber
):
    """
    Inspect one project.
    """

    comparisonResult = comparisonResults[
        projectNumber - 1
    ]

    while True:

        print()

        print("=" * 60)

        print(
            f"PROJECT: "
            f"{comparisonResult['projectID']}"
        )

        print("=" * 60)

        # --------------------------------------------------------
        # Create separate item categories.
        #
        # Item numbers remain continuous across all categories.
        # --------------------------------------------------------

        unattendedItems = []

        disabledItems = []

        backupItems = []

        for index, item in enumerate(
                comparisonResult["items"],
                start=1
        ):

            itemWithNumber = {
                "number": index,
                "item": item
            }

            if item["status"] == "UNATTENDED":

                unattendedItems.append(
                    itemWithNumber
                )

            elif item["status"] == "DISABLED":

                disabledItems.append(
                    itemWithNumber
                )

            elif item["status"] == "BACKUP":

                backupItems.append(
                    itemWithNumber
                )

        # --------------------------------------------------------
        # Display separate tables.
        # --------------------------------------------------------

        _PRINT_ITEM_TABLE(
            "UNATTENDED",
            unattendedItems,
            attention=True
        )

        _PRINT_ITEM_TABLE(
            "DISABLED",
            disabledItems
        )

        _PRINT_ITEM_TABLE(
            "BACKUP",
            backupItems
        )

        # --------------------------------------------------------
        # Navigation.
        # --------------------------------------------------------

        command = input(
            "\nEnter item number to inspect "
            "(b = back, exit = terminate): "
        ).strip().lower()

        # --------------------------------------------------------
        # Terminate complete BackupSystem.
        # --------------------------------------------------------

        if command == "exit":

            print(
                "\nBackupSystem terminated by user.\n"
            )

            sys.exit(0)

        # --------------------------------------------------------
        # Back to project summary.
        # --------------------------------------------------------

        if command == "b":

            return

        # --------------------------------------------------------
        # Convert input to item number.
        # --------------------------------------------------------

        try:

            itemNumber = int(command)

        except ValueError:

            print(
                "\nInvalid input."
            )

            continue

        # --------------------------------------------------------
        # Find item using its continuous number.
        # --------------------------------------------------------

        selectedItem = None

        for index, item in enumerate(
                comparisonResult["items"],
                start=1
        ):

            if index == itemNumber:

                selectedItem = item

                break

        if selectedItem is None:

            print(
                "\nInvalid item number."
            )

            continue

        # --------------------------------------------------------
        # Inspect selected item.
        # --------------------------------------------------------

        _INSPECT_ITEM(
            selectedItem
        )


def _PRINT_ITEM_TABLE(
        title,
        items,
        attention=False
):
    """
    Print one category of project items.
    """

    if not items:

        return

    print()

    if attention:

        print(
            f"{_BOLD}"
            f"{title}"
            f"{_RESET}"
        )

    else:

        print(
            f"{_BOLD}"
            f"{title}"
            f"{_RESET}"
        )

    print("-" * 60)

    print(
        f"{'#':>3}   "
        f"{'ITEM':<25} "
        f"STATUS"
    )

    print("-" * 60)

    for entry in items:

        itemNumber = entry["number"]

        item = entry["item"]

        # --------------------------------------------------------
        # YAML item exists.
        # --------------------------------------------------------

        if item["itemID"] is not None:

            itemName = item["itemID"]

        # --------------------------------------------------------
        # Unattended filesystem item.
        # --------------------------------------------------------

        else:

            itemName = item[
                "filesystemItem"
            ]["name"]

        if attention:

            print(
                f"{_BOLD}"
                f"{itemNumber:>3}   "
                f"{itemName:<25} "
                f"{item['status']}"
                f"{_RESET}"
            )

        else:

            print(
                f"{itemNumber:>3}   "
                f"{itemName:<25} "
                f"{item['status']}"
            )


def _INSPECT_ITEM(
        comparisonItem
):
    """
    Display the details of one comparison item.
    """

    while True:

        print()

        print("=" * 60)

        # --------------------------------------------------------
        # Determine item ID/name.
        # --------------------------------------------------------

        if comparisonItem["yamlItem"] is not None:

            itemID = comparisonItem[
                "yamlItem"
            ]["itemID"]

        else:

            itemID = comparisonItem[
                "filesystemItem"
            ]["name"]

        print(
            f"ITEM: {itemID}"
        )

        print("=" * 60)

        # --------------------------------------------------------
        # YAML item exists.
        # --------------------------------------------------------

        if comparisonItem["yamlItem"] is not None:

            print()

            print(
                "Parsed YAML item"
            )

            print("-" * 60)

            for key, value in (
                    comparisonItem["yamlItem"].items()
            ):

                print(
                    f"{key:<20}: {value}"
                )

            print("-" * 60)

        # --------------------------------------------------------
        # Unattended filesystem item.
        # --------------------------------------------------------

        else:

            print()

            print(
                f"{_BOLD}"
                "UNATTENDED ITEM"
                f"{_RESET}"
            )

            print()

            print(
                "This item exists on the filesystem "
                "but is not declared in the YAML."
            )

            print()

            print(
                "Filesystem location:"
            )

            print(
                f"    "
                f"{comparisonItem['itemLocation']}"
            )

        # --------------------------------------------------------
        # Navigation.
        # --------------------------------------------------------

        command = input(
            "\nb = back, exit = terminate: "
        ).strip().lower()

        # --------------------------------------------------------
        # Terminate complete BackupSystem.
        # --------------------------------------------------------

        if command == "exit":

            print(
                "\nBackupSystem terminated by user.\n"
            )

            sys.exit(0)

        # --------------------------------------------------------
        # Back to project.
        # --------------------------------------------------------

        if command == "b":

            return

        print(
            "\nInvalid input."
        )


def _HAS_UNATTENDED_ITEMS(
        comparisonResults
):
    """
    Return True if any project contains an
    unattended filesystem item.
    """

    for comparisonResult in comparisonResults:

        for item in comparisonResult["items"]:

            if item["status"] == "UNATTENDED":

                return True

    return False


def GET_BACKUP_COMMENT():
    """
    Get an optional comment from the user for this backup execution.

    Returns
    -------
    str
        User-provided backup comment.
    """

    print()

    print("=" * 60)
    print("BACKUP COMMENT")
    print("=" * 60)

    print()

    print(
        "Enter a comment for this backup."
    )

    print(
        "Press Enter to leave the comment empty."
    )

    print()

    comment = input(
        "Comment: "
    ).strip()

    print()

    return comment