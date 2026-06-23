# main.py

from src.extractYAML import EXTRACT_YAML

from src.validateYAML import VALIDATE_YAML

from src.generateRepositoryStructure import GENERATE_REPOSITORY_STRUCTURE

from src.initializeRepository import INITIALIZE_REPOSITORY

from src.checkSchedule import CHECK_SCHEDULE

from src.checkSyncPolicy import CHECK_SYNC_POLICY

from src.backupEngine import BACKUP_ENGINE

from src.updateMetadata import UPDATE_METADATA

from src.logger import LOGGER

import argparse

_BACKUP_SYSTEM_VERSION = "1.0"

def GET_ARGUMENTS():

    parser = argparse.ArgumentParser(

        description="BackupSystem v1.0"

    )

    parser.add_argument(

        "yamlFile",

        help="Path to YAML configuration file"

    )

    return parser.parse_args()

def MAIN():

    arguments = GET_ARGUMENTS()

    yamlDictionary = EXTRACT_YAML(

        arguments.yamlFile

    )

    VALIDATE_YAML(

        yamlDictionary

    )

    INITIALIZE_REPOSITORY(

        yamlDictionary

    )

    GENERATE_REPOSITORY_STRUCTURE(

        yamlDictionary,

        _BACKUP_SYSTEM_VERSION

    ) 

    scheduleSummary = CHECK_SCHEDULE(

        yamlDictionary

    )

    syncSummary = CHECK_SYNC_POLICY(

        yamlDictionary,

        scheduleSummary

    )

    backupSummary = BACKUP_ENGINE(

        yamlDictionary,

        syncSummary

    )

    UPDATE_METADATA(

        yamlDictionary,

        backupSummary

    )

    LOGGER(

        yamlDictionary,

        scheduleSummary,

        syncSummary,

        backupSummary,

        _BACKUP_SYSTEM_VERSION

    )

    return scheduleSummary


if __name__ == "__main__":

    MAIN()