





# YAML Configuration
- hardDisk: <path/to/harddisk>
- localPC: <path/to/localPC> # for storing logs, updates, metadata
- projects:
    - projectID: ID of this Project
        - projectDescription: Description of Project1
        - projectComment: Easy tag to understand which project is under consideration
        - projectClassification: validation/parametric/development/solver/automation
        - projectEnabled: true/false # Master level
        - verifyBackup: true
        - backupInterval: 
            - unit: week/month # Weeks or months
            - frequency: 2 # Frequency for weeks or months (once in 2 weeks/ months)
        - items:
            - itemID: Unique ID (usually folder name)- will edit manually
                - itemDescription: Description
                - itemComment: Easy tag to understand which item is under consideration
                - itemLocation: <path/to/folder/file>
                - itemEnabled: true/false
                - syncPolicy: always/manual/protect
                - excludeFolders
                    - <path/to/folder1>
                    - <path/to/folder2>
                - excludeFiles
                    - <path/to/file1>
                    - <path/to/file2>
    TODO
- [x] YAML configuration- decided
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
