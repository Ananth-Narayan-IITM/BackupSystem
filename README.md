# BackupSystem (v1.0)

Author: Ananth Narayan

Version: v1.0

Language: Python

Purpose: Automated research backup system for CFD/OpenFOAM/DAFoam projects.

---

# 1. Introduction

BackupSystem is a lightweight Python-based automated backup utility developed specifically for research workflows involving:

- OpenFOAM
- DAFoam
- CFD simulations
- Validation cases
- Parametric studies
- Solver development
- Python automation scripts

The objective is to periodically backup only important files/folders instead of backing up entire simulation directories.

The system is YAML-driven, meaning users only modify the YAML configuration file and execute the Python script.

The backup engine will automatically:

- Check backup schedules
- Apply sync policies
- Copy selected files/folders
- Update metadata
- Generate logs
- Maintain repository information

This is the first stable release (v1.0).

---

# 2. Philosophy

The system is built on three components.

## YAML

User configuration.

Defines:

- What to backup
- When to backup
- Which files/folders to exclude

## JSON

Repository memory.

Stores:

- Backup history
- Last execution
- Backup counts

## LOGS

Historical execution records.

Stores:

- What happened during each execution

---

# 3. Repository Structure

External HDD structure:

userName/

    backups/

    logs/

        Jun-2026/

            backup_20260623_151308.json

    metadata/

        backupDatabase.json

        backupRepository.md

Local PC structure:

localPC/

    logs/

        Jun-2026/

            backup_20260623_151308.json

    metadata/

        backupRepository.md

---

# 4. Project Architecture

Project directory:

BackupSystem/

    main.py

    configYAML.yaml

    README.md

    src/

        extractYAML.py

        validateYAML.py

        generatebackupRepository.py

        initializeRepository.py

        checkSchedule.py

        checkSyncPolicy.py

        backupEngine.py

        updateMetadata.py

        logger.py

---

# 5. Execution Pipeline

```
main.py

↓

EXTRACT_YAML

↓

VALIDATE_YAML

↓

INITIALIZE_REPOSITORY

↓

GENERATE_REPOSITORY_STRUCTURE

↓

CHECK_SCHEDULE

↓

CHECK_SYNC_POLICY

↓

BACKUP_ENGINE

↓

UPDATE_METADATA

↓

LOGGER
```
---

# 6. Module Description

## extractYAML.py

Purpose:

Reads YAML file and converts it into Python dictionary.

Input:

configYAML.yaml

Output:

yamlDictionary

---

## validateYAML.py

Purpose:

Validates YAML configuration.

Checks:

- Mandatory fields
- Invalid options
- Missing entries
- Duplicate IDs
- Invalid paths

---

## initializeRepository.py

Purpose:

Creates repository structure inside HDD.

Creates:

backups/

logs/

metadata/

Creates:

backupDatabase.json

if repository is initialized for first time.

---

## generatebackupRepository.py

Purpose:

Generates backupRepository.md

Stores:

- Project information
- Item information
- Item classifications
- Summary statistics

Writes copies to:

HDD/metadata/

localPC/metadata/

---

## checkSchedule.py

Purpose:

Determines whether projects are due for backup.

Works at:

Project level

Example:

0/14 day(s)

8/14 day(s)

14/14 day(s)

---

## checkSyncPolicy.py

Purpose:

Determines which items should be backed up.

Works at:

Item level

Policies:

always

manual

protect

---

## backupEngine.py

Purpose:

Performs actual backup.

Uses:

rsync

Advantages:

- Fast
- Copies only modified files
- Preserves timestamps
- Preserves permissions
- Handles large OpenFOAM cases

---

## updateMetadata.py

Purpose:

Updates backupDatabase.json

Updates:

- lastExecution
- backupCount
- lastBackup
- lastStatus

---

## logger.py

Purpose:

Generates execution logs.

Stores:

- Schedule information
- Sync information
- Backup information

---

# 7. YAML Template

```yaml
hardDisk: <path/to/harddisk>
# for storing logs, metadata
localPC: <path/to/localPC> 

# Item is subfolder of project, like storing validation, parametric study
projects:
    - projectID: ID of this Project
      projectDescription: Description of Project
      projectComment: Project Comment
      # Master level- true/ false, overrides itemEnabled
      projectEnabled: true 
      # true/ false
      verifyBackup: true 
      backupInterval: 
          # Backup duration, week/ month
          unit: week 
          # Frequency for duration, integer
          frequency: 2 
      items:
          - itemID: ID for this folder
            itemDescription: Description of folder
            itemComment: Easy tag to understand which item is under consideration.
            # validation/parametric/development/solver/automation
            itemClassification: validation 
            # for files, excludeFolders and excludeFiles makes no sense
            itemLocation: <path/to/folder-or-file> 
            # Child level- true/ false
            itemEnabled: true 
            # always (backup when script is run)/ manual (manual backup)/ protect (finalized backup)
            syncPolicy: always 
            # can be empty as []
            excludeFolders: [<path/to/folder1>, <path/to/folder2>, "folder*"] 
            # use " " for parsing
            excludeFiles: [<path/to/file1>, <path/to/file2>, "file*.py"] 
```

---

# 8. YAML Field Description

## hardDisk

Root HDD location.

Example:

/media/user/HDD/userName

---

## localPC

Local storage location.

Stores:

- Logs
- Repository structure

---

## projectID

Unique project identifier.

Must never be duplicated.

Examples:

e_VOF

DAFoam

AdjointSolver

---

## itemID

Unique item identifier.

Must never be duplicated.

Examples:

e0R1

e0R2

e0R3

---

## projectEnabled

Master switch.

true

false

Overrides all item settings.

---

## backupInterval

Controls backup schedule.

Example:

Every 2 weeks

Every 1 month

---

## itemClassification

Allowed values:

validation

parametric

development

solver

automation

---

## itemEnabled

Enables/disables item backup.

---

## syncPolicy

always

Backup whenever project is due.

manual

User-controlled.

Currently skipped automatically.

protect

Backup only once.

Future executions are skipped.

---

## excludeFolders

Exclude folders.

Example:

```yaml
excludeFolders:

  - processor*

  - postProcessing

  - "[1-9]*"
```

---

## excludeFiles

Exclude files.

Example:

```yaml
excludeFiles:

  - "*.log"

  - "*.tmp"
```

---

# 9. backupDatabase.json Structure

```json
{
    "repository": {},
    "projects": {},
    "items": {}
}
```

repository:

Stores repository information.

projects:

Stores project history.

items:

Stores item history.

---

# 10. Log Structure

Logs are stored monthly.

Example:

logs/

    Jun-2026/

        backup_20260623_151308.json

Contains:

- Execution status
- Due projects
- Backup items
- Success items
- Failed items

---

# 11. General Workflow

Step 1

Create YAML file.

Step 2

Add projects.

Step 3

Add items.

Step 4

Run:

python main.py

Step 5

Verify:

- logs
- metadata
- backups

---

# 12. General Do's

✓ Keep itemID unique.

✓ Keep projectID unique.

✓ Keep HDD connected before execution.

✓ Backup only finalized cases.

✓ Exclude unnecessary OpenFOAM folders.

✓ Use comments to describe projects.

✓ Keep YAML updated.

✓ Periodically verify logs.

✓ Periodically verify backupRepository.md.

---

# 13. General Don'ts

✗ Do not backup entire CFD repositories unnecessarily.

✗ Do not duplicate itemIDs.

✗ Do not duplicate projectIDs.

✗ Do not modify backupDatabase.json manually.

✗ Do not delete metadata folder.

✗ Do not edit logs manually.

✗ Do not place backup repository inside source directories.

---

# 14. Recommended OpenFOAM Exclusions

Examples:

excludeFolders:

- processor*
- postProcessing
- "[1-9]*"

excludeFiles:

- "*.log"
- "*.tmp"

Modify according to case requirements.

---

# 15. Future Improvements (v1.1)

Planned features:

- restoreBackup.py
- diskSpaceCheck.py
- repositoryHealth.py
- dryRunMode.py
- retentionCleanup.py

---

# 16. Version History

v1.0

Initial stable release.

Features:

- YAML driven

- Automated scheduling

- Sync policies

- Metadata tracking

- Repository generation

- Logging

- rsync backup engine

- OpenFOAM friendly
