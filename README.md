To run the code, you can prefer to set `alias` in `~/.bashrc` as `alias BackupSystem='python3 /path/to/folder/main.py'`, then run as

```python
BackupSystem <mainConfigFile.yaml>
```
**Note:**

This `BackupSystem` uses `rsync` to effectively determine which files to be copied which saves time over ignoring unchanged files. This `rsync` may not be available in `Windows` or similar platform. make sure `rsync` is installed (verify as `rsync --version`) before proceeding.

# BackupSystem (v2.0)

Author: Ananth Narayan

Version: v2.0

Language: Python

Purpose: Automated research backup system for CFD/OpenFOAM/DAFoam projects with improved architecture.

---

# Changes (v1.0 to v2.0)
- Added `executeCommand`, `runCommand` for running certain script before backup inside item folder
- Check space (inclusive of `marginSpace`) in HDD and terminate when space is free space is less than `marginSpace`. Can be toggled with `verifyHDDSpace`
- Combines multiple YAML files to parent YAML for modularity
- Removed `syncPolicy: protect` as it didn't make sense later. Either take backup regularly or choose `syncPolicy: manual`
- Removed `verifyBack` as this was not used anywhere. The logs files reveal these verification

---

# Backward compatability

v1.0 YAML file will continue to work when deprecated keys are avoided. Refer changes log.

---

# 1. Introduction

BackupSystem is a lightweight Python-based automated backup utility developed specifically for research workflows involving:

- OpenFOAM
- CFD simulations
- Validation cases
- Parametric studies
- Solver development
- Python automation scripts

The objective is to periodically backup only important files/folders instead of backing up entire simulation directories.

The system is YAML-driven, meaning users only modify the YAML configuration file and execute the Python script.

The backup engine will automatically:

- Gather multiple YAML files
- Check backup schedules
- Check HDD space
- Apply sync policies
- Copy selected files/folders
- Update metadata
- Generate logs
- Maintain repository information

---

# 2. YAML Template
Refer `templates/backupConfig.yaml`
```yaml
hardDisk: <path/to/harddisk>
localPC: <path/to/localPC> # for storing logs, updates, metadata
verifyHDDSpace: true
marginSpace: <size> # in MB or GB like 10GB
# Item is subfolder of project, like storing validation, parametric study
projects:
    - path-to-yaml1.yaml
    - path-to-yaml2.yaml
```

For `path-to-yaml1.yaml`,

```yaml
projectID: ID of this Project
projectDescription: Description of Project
projectComment: Project Comment
projectEnabled: true # Master level- true/ false, overrides itemEnabled
backupInterval: 
    unit: week # Backup duration, week/ month
    frequency: 2 # Frequency for duration, integer
items:
  - itemID: unique item ID
    itemDescription: Description of folder
    itemComment: Easy tag to understand which item is under consideration.
    itemClassification: validation # validation/parametric/development/solver/automation
    itemLocation: <path/to/folder-or-file> # for files, excludeFolders and excludeFiles makes no sense
    itemEnabled: true # Child level- true/ false
    executeCommand: true # perform runCommand- true/ false (default)
    runCommand: ["<bash command or run script here>"]
    syncPolicy: always # always (backup when script is run)/ manual (manual backup)
    excludeFolders: [<path/to/folder1>, <path/to/folder2>, "folder*"] # can be empty as []
    excludeFiles: [<path/to/file1>, <path/to/file2>, "file*.py"] # use " " for parsing
    retainLatestTime: true    

```

---

# 3. YAML Field Description

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

Master switch to take backup or not. Boolean: `true` or `false`

Overrides all item settings.

---

## backupInterval

Controls backup schedule.

Example:

- Every 2 weeks

- Every 1 month

---

## itemClassification

`validation`: Validation case files

`parametric`: Parametric study case files

`development`: Files under development

`solver`: OpenFOAM solver files

`automation`: To automate few tasks like `graphPlot` etc.,

---

## itemEnabled

Enables/disables item backup.

---

## syncPolicy

`always`: Backup whenever project is due.

`manual`: User-controlled.

---

## excludeFolders

Exclude folders.

Example:

```yaml
excludeFolders: ["processor*","postProcessing","[1-9]*"]
```

---

## excludeFiles

Exclude files.

Example:

```yaml
excludeFiles: ["*.log", "*.tmp"]
```

---

# 4. backupDatabase.json Structure

```json
{
    "repository": {},
    "projects": {},
    "items": {}
}
```

repository: Stores repository information.

projects: Stores project history.

items: Stores item history.

---

# 5. Log Structure

Logs are stored in basis of monthly folders.

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

# 6. General Workflow

Step 1

Create multiple YAML files and add it to main YAML file.

Step 2

Add projects.

Step 3

Add items.

Step 4

Run:

`python3 main.py <configFile.yaml>`

Step 5

Verify:

- logs
- metadata
- backups

---

# 7. Future Improvements (v3.0)

Planned features:

- Work on `retainLatestTime` for retaining OpenFOAM solution folders
- Option for `purgeWrite` or `forced` write with flags to force backup again
- Implementation of doxygen- as code is getting complicated, doxygen should give some idea on code architecture
- Refactor the whole code into presentable form

---

# 8. Version History

**v2.0**

*Features:*

- Added `executeCommand`, `runCommand` for running certain script before backup inside item folder

- Check space (inclusive of `marginSpace`) in HDD and terminate when space is free space is less than `marginSpace`. Can be toggled with `verifyHDDSpace`

- Combines multiple YAML files to parent YAML for modularity

- Removed `syncPolicy: protect` as it didn't make sense later. Either take backup regularly or choose `syncPolicy: manual`

- Removed `verifyBack` as this was not used anywhere. The logs files reveal these verification

**v1.0**

Initial stable release.

*Features:*

- YAML driven

- Automated scheduling

- Sync policies

- Metadata tracking

- Repository generation

- Logging

- rsync backup engine

- OpenFOAM friendly



