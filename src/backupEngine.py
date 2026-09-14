from collections import deque
from pathlib import Path
import subprocess


# =============================================================================
# Runtime copy status
# =============================================================================

_LAST_COPY_ERROR = {
    "reason": "",
    "message": "",
}


# =============================================================================
# Public Function
# =============================================================================


def BACKUP_ENGINE(yamlDictionary, syncSummary):
    """
    Execute the backup for all items selected by CHECK_SYNC_POLICY().

    Symbolic links are skipped intentionally. Owner and group metadata are
    not preserved because the external HDD may not permit chown/chgrp.

    Parameters
    ----------
    yamlDictionary : dict
        Parsed YAML configuration.

    syncSummary : dict
        Backup items selected by the sync-policy stage.

    Returns
    -------
    dict
        Summary of successful and failed backup operations.
    """

    backupSummary = {
        "successfulProjects": [],
        "failedProjects": [],
        "successfulItems": [],
        "failedItems": [],
        "skippedSymlinks": [],
        "failureDetails": [],
    }

    for backupItem in syncSummary["backupItems"]:
        projectID = backupItem["projectID"]
        itemID = backupItem["itemID"]

        item = _GET_ITEM(
            yamlDictionary,
            projectID,
            itemID,
        )

        destination = _CREATE_PROJECT_FOLDER(
            yamlDictionary,
            projectID,
        )

        result = _COPY_ITEM(
            item,
            destination,
        )

        if result["success"]:
            backupSummary["successfulItems"].append(itemID)

            if projectID not in backupSummary["successfulProjects"]:
                backupSummary["successfulProjects"].append(projectID)

            if result["skippedSymlinks"]:
                backupSummary["skippedSymlinks"].extend(result["skippedSymlinks"])

        else:
            backupSummary["failedItems"].append(itemID)

            if projectID not in backupSummary["failedProjects"]:
                backupSummary["failedProjects"].append(projectID)

            backupSummary["failureDetails"].append(
                {
                    "projectID": projectID,
                    "itemID": itemID,
                    "reason": result["reason"],
                    "message": result["message"],
                }
            )

            if result["skippedSymlinks"]:
                backupSummary["skippedSymlinks"].extend(result["skippedSymlinks"])

    _PRINT_BACKUP_SUMMARY(backupSummary)

    return backupSummary


# =============================================================================
# YAML Item Lookup
# =============================================================================


def _GET_ITEM(yamlDictionary, projectID, itemID):
    """
    Return the YAML item matching a project and item ID.
    """

    for project in yamlDictionary["projects"]:
        if project["projectID"] != projectID:
            continue

        for item in project["items"]:
            if item["itemID"] == itemID:
                return item

    raise ValueError(f"{itemID} not found.")


# =============================================================================
# Destination
# =============================================================================


def _CREATE_PROJECT_FOLDER(yamlDictionary, projectID):
    """
    Create and return the project backup directory.
    """

    destination = Path(yamlDictionary["hardDisk"]) / "backups" / projectID

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    return destination


# =============================================================================
# Copy
# =============================================================================


def _COPY_ITEM(item, destination):
    """
    Copy one configured item using rsync.

    Symbolic links are intentionally ignored.

    For directory backups, symbolic links encountered inside the directory
    are also excluded and are not followed.

    The last five transferred filesystem entries are displayed as a rolling
    history.

    Returns
    -------
    dict
        Copy result containing success state, failure information, and
        skipped symbolic links.
    """

    source = Path(item["itemLocation"])

    result = {
        "success": False,
        "reason": "",
        "message": "",
        "skippedSymlinks": [],
    }

    # -------------------------------------------------------------------------
    # Source validation
    # -------------------------------------------------------------------------

    if source.is_symlink():
        result["success"] = True
        result["reason"] = "SYMLINK_SKIPPED"
        result["message"] = "Configured item is a symbolic link and was intentionally skipped."
        result["skippedSymlinks"].append(str(source))

        print()
        print(f"  Skipping symbolic link: {source}")

        return result

    if not source.exists():
        result["reason"] = "SOURCE_NOT_FOUND"
        result["message"] = f"Configured source does not exist: {source}"

        print()
        print("  BACKUP ERROR")
        print(f"  Source not found: {source}")

        return result

    # -------------------------------------------------------------------------
    # Destination
    # -------------------------------------------------------------------------

    itemDestination = destination / item["itemID"]

    itemDestination.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------------------------------
    # rsync command
    # -------------------------------------------------------------------------

    command = [
        "rsync",
        "-a",
        "--no-owner",
        "--no-group",
        "--progress",
        "--out-format=%n",
    ]

    # Never follow symbolic links.
    command.append("--no-links")

    for folder in item.get(
        "excludeFolders",
        [],
    ):
        command.append(f"--exclude={folder}")

    for file in item.get(
        "excludeFiles",
        [],
    ):
        command.append(f"--exclude={file}")

    # -------------------------------------------------------------------------
    # Source / destination paths
    # -------------------------------------------------------------------------

    if source.is_dir():
        sourceArgument = str(source) + "/"
    else:
        sourceArgument = str(source)

    destinationArgument = str(itemDestination) + "/"

    command.extend(
        [
            sourceArgument,
            destinationArgument,
        ]
    )

    print()
    print("=" * 80)
    print(f"BACKUP : {item['itemID']}")
    print("=" * 80)
    print(f"Source : {sourceArgument}")
    print(f"Target : {destinationArgument}")
    print()

    # -------------------------------------------------------------------------
    # Run rsync
    # -------------------------------------------------------------------------

    recentFiles = deque(maxlen=5)

    errorLines = []

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        if process.stdout is None:
            result["reason"] = "RSYNC_OUTPUT_ERROR"
            result["message"] = "Unable to read rsync output."
            process.wait()
            return result

        for rawLine in process.stdout:
            line = rawLine.rstrip()

            if not line:
                continue

            stripped = line.strip()

            # -----------------------------------------------------------------
            # rsync progress information
            # -----------------------------------------------------------------

            if _IS_RSYNC_PROGRESS_LINE(stripped):
                print(f"  Progress : {stripped}")
                continue

            # -----------------------------------------------------------------
            # rsync error messages
            # -----------------------------------------------------------------

            if stripped.startswith("rsync:"):
                errorLines.append(stripped)

                print(f"  ERROR    : {stripped}")

                continue

            if stripped.startswith("rsync error"):
                errorLines.append(stripped)

                print(f"  ERROR    : {stripped}")

                continue

            # -----------------------------------------------------------------
            # rsync informational lines
            # -----------------------------------------------------------------

            if stripped.startswith("sending incremental file list"):
                continue

            if stripped.startswith("sent "):
                print(f"  {stripped}")
                continue

            if stripped.startswith("total size is "):
                print(f"  {stripped}")
                continue

            if stripped.startswith("speedup is "):
                print(f"  {stripped}")
                continue

            # -----------------------------------------------------------------
            # File name from --out-format=%n
            # -----------------------------------------------------------------

            if _IS_SKIPPED_SYMLINK_NAME(
                source,
                stripped,
            ):
                result["skippedSymlinks"].append(stripped)
                continue

            recentFiles.append(stripped)

            _PRINT_COPY_PROGRESS(recentFiles)

        returnCode = process.wait()

        if returnCode == 0:
            result["success"] = True

            print()
            print(f"  Completed : {item['itemID']}")

            return result

        result["reason"] = "RSYNC_ERROR"

        if errorLines:
            result["message"] = " | ".join(errorLines)
        else:
            result["message"] = f"rsync exited with code {returnCode}."

        print()
        print(f"  FAILED : {item['itemID']}")
        print(f"  Reason: {result['message']}")

        return result

    except OSError as error:
        result["reason"] = "RSYNC_EXECUTION_ERROR"
        result["message"] = str(error)

        print()
        print(f"  FAILED : {item['itemID']}")
        print(f"  Reason: {error}")

        return result


# =============================================================================
# Progress Helpers
# =============================================================================


def _IS_RSYNC_PROGRESS_LINE(line):
    """
    Return True when a line resembles rsync's --progress output.
    """

    if not line:
        return False

    firstToken = line.split(maxsplit=1)[0]

    numericToken = firstToken.replace(",", "").replace(".", "")

    return numericToken.isdigit()


def _PRINT_COPY_PROGRESS(recentFiles):
    """
    Display the five most recently reported files.
    """

    print()
    print("  Recent files:")

    for filename in recentFiles:
        print(f"    - {filename}")


def _IS_SKIPPED_SYMLINK_NAME(
    source,
    name,
):
    """
    Detect a symbolic-link entry when rsync reports its name.

    This is intentionally conservative. The source filesystem is not scanned
    recursively here; rsync itself is instructed not to follow links.
    """

    if not source.is_dir():
        return False

    candidate = source / name

    return candidate.is_symlink()


# =============================================================================
# Backup Summary
# =============================================================================


def _PRINT_BACKUP_SUMMARY(backupSummary):
    """
    Print the final backup summary including failure reasons.
    """

    print()
    print("=" * 80)
    print("BACKUP SUMMARY")
    print("=" * 80)
    print()

    print(f"Successful Items : {len(backupSummary['successfulItems'])}")

    for item in backupSummary["successfulItems"]:
        print(f"  - {item}")

    print()

    print(f"Failed Items : {len(backupSummary['failedItems'])}")

    for item in backupSummary["failedItems"]:
        print(f"  - {item}")

    if backupSummary.get("failureDetails"):
        print()
        print("FAILURE DETAILS")
        print("-" * 80)

        for failure in backupSummary["failureDetails"]:
            print(f"  Project : {failure['projectID']}")

            print(f"  Item    : {failure['itemID']}")

            print(f"  Reason  : {failure['reason']}")

            print(f"  Message : {failure['message']}")

            print()

    if backupSummary.get("skippedSymlinks"):
        print("SKIPPED SYMBOLIC LINKS")
        print("-" * 80)

        print(f"Count : {len(backupSummary['skippedSymlinks'])}")

        for link in backupSummary["skippedSymlinks"]:
            print(f"  - {link}")

        print()

    print("=" * 80)
    print()
