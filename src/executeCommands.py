# src/executeCommands.py

from pathlib import Path
from datetime import datetime
import subprocess
import time


def EXECUTE_COMMANDS(yamlDictionary, syncSummary):

    print()
    print("=" * 80)
    print("PRE-BACKUP COMMAND SUMMARY")
    print("=" * 80)
    print()

    commandSummary = []

    backupItems = syncSummary.get("backupItems", [])

    for backupItem in backupItems:
        projectID = backupItem["projectID"]

        itemID = backupItem["itemID"]

        item = _GET_ITEM(yamlDictionary, projectID, itemID)

        executeCommand = item.get("executeCommand", False)

        if not executeCommand:
            continue

        summary = _EXECUTE_ITEM(projectID, item)

        commandSummary.append(summary)

    print("=" * 80)
    print()

    return {"executedItems": commandSummary}


def _GET_ITEM(yamlDictionary, projectID, itemID):

    for project in yamlDictionary["projects"]:
        if project["projectID"] != projectID:
            continue

        for item in project["items"]:
            if item["itemID"] == itemID:
                return item

    raise ValueError(f"{itemID} not found.")


def _REMOVE_OLD_LOGS(itemLocation):

    itemLocation = Path(itemLocation)

    if not itemLocation.exists():
        return

    for logFile in itemLocation.glob("log.executeCommand*"):
        if logFile.is_file():
            logFile.unlink()


def _EXECUTE_ITEM(projectID, item):

    itemLocation = Path(item["itemLocation"])

    _REMOVE_OLD_LOGS(itemLocation)

    commands = item.get("runCommand", [])

    print(f"{projectID}/{item['itemID']}")

    startTime = time.time()

    for commandIndex, command in enumerate(commands, start=1):
        logFile = itemLocation / f"log.executeCommand{commandIndex:02d}.txt"

        success = _RUN_COMMAND(command, itemLocation, logFile)

        if success:
            print(f"  [{commandIndex}] PASS : {command}")

        else:
            raise RuntimeError(
                "\n" + "=" * 80 + "\n"
                "PRE-BACKUP COMMAND FAILED\n" + "=" * 80 + "\n"
                f"Project : {projectID}\n"
                f"Item    : {item['itemID']}\n"
                f"Command : {command}\n"
                f"Log     : {logFile}\n"
                "\nBackup aborted.\n" + "=" * 80
            )

    endTime = time.time()

    print()

    return {
        "projectID": projectID,
        "itemID": item["itemID"],
        "commandsExecuted": len(commands),
        "executionTime": round(endTime - startTime, 2),
        "status": "PASS",
    }


def _RUN_COMMAND(command, workingDirectory, logFile):

    with open(logFile, "w", encoding="utf-8") as log:
        log.write("\n" + "=" * 60 + "\n")

        log.write(f"Command : {command}\n")

        log.write(f"Started : {datetime.now()}\n")

        log.write("=" * 60 + "\n\n")

        result = subprocess.run(
            ["bash", "-i", "-c", command],
            cwd=workingDirectory,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

    return result.returncode == 0
