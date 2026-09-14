# Compilation

backupSystem: `pip install -e .` 

Documentation: `doxygen Doxyfile`, pdf: `cd docs/api/pdf && make`, HTML: `firefox docs/api/html/index.html`

To run the code, you can prefer to set `alias` in `~/.bashrc` as `alias BackupSystem='python3 /path/to/folder/main.py'`, then run as

```python
BackupSystem <mainConfigFile.yaml>
```
Augument `--force` can be passed on

**Note:**

This `BackupSystem` uses `rsync` to effectively determine which files to be copied which saves time over ignoring unchanged files. This `rsync` may not be available in `Windows` or similar platform. make sure `rsync` is installed (verify as `rsync --version`) before proceeding.

# BackupSystem (v3.0)

Author: Ananth Narayan

Version: v3.0

Language: Python

Purpose: Automated research backup system for CFD/OpenFOAM/DAFoam projects with improved architecture.

---
# Changes Log

## Changes (v2.0 to v3.0)
- Added first-level filesystem monitoring to detect unattended files/folders and reduce the risk of missing important research data.
- Added explicit `itemEnabled` handling: enabled items are backed up, while disabled items are intentionally excluded and shown during the final audit.
- Added cross-project declaration checking so items declared under another project are not incorrectly reported as unattended.
- Added automatic backup handling for `.git` directories so Git history is retained without requiring a separate YAML item.
- Added a final interactive backup audit showing project, item, classification, and backup status before execution.
- Added `--force` mode for testing, allowing the schedule check to be bypassed without bypassing safety checks or the final audit.
- Implemented Doxygen documentation and Ruff formatting.

## Changes (v1.0 to v2.0)
- Added `executeCommand`, `runCommand` for running certain script before backup inside item folder
- Check space (inclusive of `marginSpace`) in HDD and terminate when space is free space is less than `marginSpace`. Can be toggled with `verifyHDDSpace`
- Combines multiple YAML files to parent YAML for modularity
- Removed `syncPolicy: protect` as it didn't make sense later. Either take backup regularly or choose `syncPolicy: manual`
- Removed `verifyBackup` as this was not used anywhere. The logs files reveal these verification

---

# Backward compatability

v2.0 YAML file will continue to work provided all the itemID inside the project directory. Refer changes log.
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
- Validate the YAML configuration
- Check backup schedules
- Scan intended project locations for unattended files/folders
- Check HDD space
- Apply sync policies
- Copy selected files/folders
- Preserve Git history through automatic `.git` backup
- Update metadata
- Generate logs
- Maintain repository information
- Present a final backup audit before execution

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
    itemEnabled: true # Child level- true / false
    syncPolicy: always # always (backup when project is due) / manual
    excludeFolders: [<path/to/folder1>, <path/to/folder2>, "folder*"] # can be empty as []
    excludeFiles: [<path/to/file1>, <path/to/file2>, "file*.py"] # can be empty as []

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

Identifier used to identify an item within a project.

Normally itemIDs should be unique. The current implementation permits
`Archive` to be used in multiple projects where the same archive structure
is intentionally shared.

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

## Filesystem monitoring and backup safety

BackupSystem checks the first level of the intended project scan locations
before executing a backup.

- `BACKUP`: explicitly declared and enabled YAML item.
- `DISABLED`: explicitly declared but disabled YAML item.
- `DECLARED-<projectID>`: declared or covered by another project.
- `DECLARED_CONTAINER`: contains YAML-declared items belonging to the current project.
- `MASTER_CONTAINER`: structural parent of a declared item.
- `AUTO-BACKUP`: system-managed item such as `.git`.
- `UNATTENDED`: filesystem item not declared or covered by YAML.

An `UNATTENDED` item requires user attention and prevents the backup from
continuing. BackupSystem does not automatically modify the YAML configuration
to resolve such cases.

---

## Final backup audit

Before the backup engine starts, BackupSystem displays the complete project
and item audit, including item classifications and statuses. The user must
explicitly confirm the backup.

This final confirmation is performed even when all projects and items are
ready, providing a final opportunity to verify the backup intent.

---

## Force mode

For testing, the schedule check can be bypassed using:

```bash
python3 main.py <configFile.yaml> --force
```

`--force` only bypasses the normal due-project schedule. It does not bypass
filesystem safety checks, YAML validation, HDD-space verification, or the
final backup confirmation.

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

Review the final backup audit and confirm the backup.

Step 6

Verify:

- logs
- metadata
- backups

For testing without waiting for a project to become due:

`python3 main.py <configFile.yaml> --force`

---

# 7. Future Improvements (v3.0)

Planned features:

- Work on retaining selected OpenFOAM solution folders
- Improve backup progress UX with a progress bar and a rolling list of recently copied files
- Further improve backup failure/error reporting
- Refactor the whole code into a clean, presentable form

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



