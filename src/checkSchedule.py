# src/checkSchedule.py

from pathlib import Path

from datetime import datetime

import json


# =============================================================================
# Public Function
# =============================================================================


def CHECK_SCHEDULE(yamlDictionary):

    scheduleSummary = {"dueProjects": [], "skippedProjects": [], "projectSchedule": []}

    metadataDictionary = _READ_METADATA(yamlDictionary)

    for project in yamlDictionary["projects"]:
        projectID = project["projectID"]

        if not project["projectEnabled"]:
            scheduleSummary["skippedProjects"].append(projectID)

            scheduleSummary["projectSchedule"].append(
                {"projectID": projectID, "status": "SKIPPED", "reason": "Project disabled"}
            )

            continue

        isDue, reason = _IS_BACKUP_DUE(project, metadataDictionary)

        if isDue:
            scheduleSummary["dueProjects"].append(projectID)

            status = "DUE"

        else:
            scheduleSummary["skippedProjects"].append(projectID)

            status = "SKIPPED"

        scheduleSummary["projectSchedule"].append(
            {"projectID": projectID, "status": status, "reason": reason}
        )

    _PRINT_SCHEDULE_SUMMARY(scheduleSummary)

    return scheduleSummary


# =============================================================================
# Read Metadata
# =============================================================================


def _READ_METADATA(yamlDictionary):

    metadataPath = Path(yamlDictionary["hardDisk"]) / "metadata" / "backupDatabase.json"

    with open(metadataPath, "r", encoding="utf-8") as file:
        return json.load(file)


# =============================================================================
# Determine Backup Schedule
# =============================================================================


def _IS_BACKUP_DUE(project, metadataDictionary):

    projectID = project["projectID"]

    projectData = metadataDictionary["projects"].get(projectID)

    # First backup

    if projectData is None:
        return True, "First backup"

    lastBackup = projectData.get("lastBackup")

    if not lastBackup:
        return True, "First backup"

    lastBackup = datetime.strptime(lastBackup, "%Y-%m-%d")

    today = datetime.today()

    elapsedDays = (today - lastBackup).days

    frequency = project["backupInterval"]["frequency"]

    unit = project["backupInterval"]["unit"]

    requiredDays = 7 * frequency if unit == "week" else 30 * frequency

    remainingDays = requiredDays - elapsedDays

    if elapsedDays >= requiredDays:
        return True, "Backup due"

    return False, f"{elapsedDays}/{requiredDays} day(s)"


# =============================================================================
# Print Summary
# =============================================================================


def _PRINT_SCHEDULE_SUMMARY(scheduleSummary):

    print()

    print("=" * 80)

    print("SCHEDULE SUMMARY")

    print("=" * 80)

    print()

    for project in scheduleSummary["projectSchedule"]:
        print(f"{project['projectID']}")

        print(f"Status : {project['status']}")

        if project["reason"] == "First backup":
            print("Progress : First backup")

        else:
            print(f"Progress : {project['reason']}")

        print()

    print("=" * 80)

    print()
