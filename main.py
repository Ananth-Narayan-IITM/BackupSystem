# main.py

from extractYAML import EXTRACT_YAML

from validateYAML import VALIDATE_YAML

from generateRepositoryStructure import GENERATE_REPOSITORY_STRUCTURE

from initializeRepository import INITIALIZE_REPOSITORY

from verifyHDDSpace import VERIFY_HDD_SPACE

from checkSchedule import CHECK_SCHEDULE

from executeCommands import EXECUTE_COMMANDS

from checkSyncPolicy import CHECK_SYNC_POLICY

from backupEngine import BACKUP_ENGINE

from updateMetadata import UPDATE_METADATA

from logger import LOGGER

from scanProject import scanProject

from compareProject import COMPARE_PROJECT

from backupPreview import BACKUP_PREVIEW

import argparse


_BACKUP_SYSTEM_VERSION = "3.0"


def GET_ARGUMENTS():

    parser = argparse.ArgumentParser(description=f"BackupSystem v{_BACKUP_SYSTEM_VERSION}")

    parser.add_argument("yamlFile", help="Path to master YAML configuration file")

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force backup of all enabled projects regardless of schedule",
    )

    return parser.parse_args()


def MAIN():

    arguments = GET_ARGUMENTS()

    yamlDictionary = EXTRACT_YAML(arguments.yamlFile)

    VALIDATE_YAML(yamlDictionary)

    INITIALIZE_REPOSITORY(yamlDictionary)

    GENERATE_REPOSITORY_STRUCTURE(yamlDictionary, _BACKUP_SYSTEM_VERSION)

    scheduleSummary = CHECK_SCHEDULE(yamlDictionary)

    syncSummary = CHECK_SYNC_POLICY(yamlDictionary, scheduleSummary)

    # ------------------------------------------------------------
    # Scan projects and compare filesystem with YAML.
    # ------------------------------------------------------------

    comparisonResults = []

    for project in yamlDictionary["projects"]:
        projectID = project["projectID"]

        # ------------------------------------------------------------
        # Disabled project.
        #
        # Do not scan it or perform any backup preparation.
        # Add it only to the preview so the user can see that
        # the project exists but is intentionally disabled.
        # ------------------------------------------------------------

        if not project["projectEnabled"]:
            comparisonResults.append(
                {
                    "projectID": projectID,
                    "projectEnabled": False,
                    "projectStatus": "DISABLED",
                    "items": [
                        {
                            "itemID": item["itemID"],
                            "itemLocation": item["itemLocation"],
                            "status": "DISABLED",
                            "yamlItem": item,
                            "filesystemItem": None,
                        }
                        for item in project["items"]
                    ],
                }
            )

            continue

        # ------------------------------------------------------------
        # Only scan enabled projects which are due for backup.
        #
        # --force bypasses the schedule check for testing.
        # ------------------------------------------------------------
        if not arguments.force and projectID not in scheduleSummary["dueProjects"]:
            continue

        scanResult = scanProject(project)

        comparisonResult = COMPARE_PROJECT(
            project,
            scanResult,
            yamlDictionary["projects"],
        )

        comparisonResult["projectEnabled"] = True

        comparisonResults.append(comparisonResult)

    # ------------------------------------------------------------
    # Backup preview.
    # ------------------------------------------------------------

    backupComment = BACKUP_PREVIEW(comparisonResults)

    if backupComment is False:
        return

    # ------------------------------------------------------------
    # Verify HDD space.
    # ------------------------------------------------------------

    spaceSummary = VERIFY_HDD_SPACE(yamlDictionary)

    # ------------------------------------------------------------
    # Execute configured commands.
    # ------------------------------------------------------------

    commandSummary = EXECUTE_COMMANDS(yamlDictionary, syncSummary)

    # ------------------------------------------------------------
    # Perform backup.
    # ------------------------------------------------------------

    backupSummary = BACKUP_ENGINE(yamlDictionary, syncSummary)

    # ------------------------------------------------------------
    # Update metadata.
    # ------------------------------------------------------------

    UPDATE_METADATA(yamlDictionary, backupSummary)

    # ------------------------------------------------------------
    # Generate execution log.
    # ------------------------------------------------------------

    LOGGER(
        yamlDictionary,
        scheduleSummary,
        syncSummary,
        backupSummary,
        _BACKUP_SYSTEM_VERSION,
        spaceSummary,
        backupComment,
    )

    return scheduleSummary


if __name__ == "__main__":
    MAIN()
