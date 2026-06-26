# src/validateYAML.py

_ALLOWED_BACKUP_UNIT = [

    "week",

    "month"

]

_ALLOWED_ITEM_CLASSIFICATION = [

    "validation",

    "parametric",

    "development",

    "solver",

    "automation"

]

_ALLOWED_SYNC_POLICY = [

    "always",

    "manual"

]
def VALIDATE_YAML(yamlDictionary):

    try:

        validationSummary = {

            "status": True,

            "projectCount": 0,

            "itemCount": 0

        }

        _VALIDATE_REPOSITORY(

            yamlDictionary

        )

        _VALIDATE_PROJECTS(

            yamlDictionary,

            validationSummary

        )

        _PRINT_VALIDATION_SUMMARY(

            validationSummary

        )

        return validationSummary

    except Exception as error:

        print()

        print("=" * 80)

        print("YAML VALIDATION FAILED")

        print("=" * 80)

        print(error)

        print("=" * 80)

        print()

        raise
def _VALIDATE_REPOSITORY(yamlDictionary):

    requiredKeys = [

        "hardDisk",

        "localPC",

        "projects"

    ]

    for key in requiredKeys:

        if key not in yamlDictionary:

            raise ValueError(

                f"Missing repository key: {key}"

            )

    if not isinstance(

            yamlDictionary["hardDisk"],

            str

    ):

        raise ValueError(

            "hardDisk must be a string."

        )

    if not isinstance(

            yamlDictionary["localPC"],

            str

    ):

        raise ValueError(

            "localPC must be a string."

        )

    if not isinstance(

            yamlDictionary["projects"],

            list

    ):

        raise ValueError(

            "projects must be a list."

        )

    if len(

            yamlDictionary["projects"]

    ) == 0:

        raise ValueError(

            "projects cannot be empty."

        )

def _VALIDATE_PROJECTS(

        yamlDictionary,

        validationSummary

):

    projectIDs = set()

    itemIDs = set()

    for project in yamlDictionary["projects"]:

        validationSummary["projectCount"] += 1

        projectID = project["projectID"]

        if projectID in projectIDs:

            raise ValueError(

                f"Duplicate projectID: {projectID}"

            )

        projectIDs.add(

            projectID

        )

        _VALIDATE_PROJECT(

            project

        )

        _VALIDATE_ITEMS(

            project,

            itemIDs,

            validationSummary

        )
def _VALIDATE_PROJECT(

        project

):

    requiredKeys = [

        "projectID",

        "projectDescription",

        "projectComment",

        "projectEnabled",

        "backupInterval",

        "items"

    ]

    for key in requiredKeys:

        if key not in project:

            raise ValueError(

                "\n"

                f"Project : {projectID}\n"

                f"Missing field : {key}"

            )

    if not isinstance(

            project["projectEnabled"],

            bool

    ):

        raise ValueError(

            f"{project['projectID']} "

            f"projectEnabled must be boolean."

        )

    _VALIDATE_BACKUP_INTERVAL(

        project

    )
def _VALIDATE_BACKUP_INTERVAL(

        project

):

    projectID = project["projectID"]

    backupInterval = project["backupInterval"]

    requiredKeys = [

        "unit",

        "frequency"

    ]

    for key in requiredKeys:

        if key not in backupInterval:

            raise ValueError(

                f"{projectID} "

                f"backupInterval missing {key}"

            )

    unit = backupInterval["unit"]

    if unit not in _ALLOWED_BACKUP_UNIT:

        _RAISE_INVALID_OPTION(

            unit,

            "backupInterval.unit",

            _ALLOWED_BACKUP_UNIT

        )

    frequency = backupInterval["frequency"]

    if not isinstance(

            frequency,

            int

    ):

        raise ValueError(

            f"{projectID} "

            f"frequency must be integer."

        )

    if frequency <= 0:

        raise ValueError(

            f"{projectID} "

            f"frequency must be > 0."

        )
def _VALIDATE_ITEMS(

        project,

        itemIDs,

        validationSummary

):

    for item in project["items"]:

        validationSummary["itemCount"] += 1

        itemID = item["itemID"]

        if itemID in itemIDs:

            raise ValueError(

                f"Duplicate itemID: {itemID}"

            )

        itemIDs.add(

            itemID

        )

        _VALIDATE_ITEM(

            item

        )
def _VALIDATE_ITEM(

        item

):

    requiredKeys = [

        "itemID",

        "itemDescription",

        "itemComment",

        "itemClassification",

        "itemLocation",

        "itemEnabled",

        "syncPolicy",

        "excludeFolders",

        "excludeFiles"

    ]

    for key in requiredKeys:

        if key not in item:

            raise ValueError(

                f"{item['itemID']} missing {key}"

            )

    if item["itemClassification"] not in _ALLOWED_ITEM_CLASSIFICATION:

        _RAISE_INVALID_OPTION(

            item["itemClassification"],

            "itemClassification",

            _ALLOWED_ITEM_CLASSIFICATION

        )

    if item["syncPolicy"] not in _ALLOWED_SYNC_POLICY:

        _RAISE_INVALID_OPTION(

            item["syncPolicy"],

            "syncPolicy",

            _ALLOWED_SYNC_POLICY

        )

    if not isinstance(

            item["itemEnabled"],

            bool

    ):

        raise ValueError(

            f"{item['itemID']} "

            f"itemEnabled must be boolean."

        )

    if not isinstance(

            item["excludeFolders"],

            list

    ):

        raise ValueError(

            f"{item['itemID']} "

            f"excludeFolders must be list."

        )

    if not isinstance(

            item["excludeFiles"],

            list

    ):

        raise ValueError(

            f"{item['itemID']} "

            f"excludeFiles must be list."

        )
def _RAISE_INVALID_OPTION(

        currentValue,

        currentField,

        allowedValues

):

    allowedValues = "\n".join(

        f"  - {value}"

        for value in sorted(

            allowedValues

        )

    )

    raise ValueError(

        "\n"

        f"Invalid value detected\n\n"

        f"Field : {currentField}\n"

        f"Value : {currentValue}\n\n"

        f"Allowed Options:\n"

        f"{allowedValues}"

    )
def _PRINT_VALIDATION_SUMMARY(validationSummary):

    print()

    print("=" * 80)

    print("YAML VALIDATION SUMMARY")

    print("=" * 80)

    print(

        f"Projects Validated : {validationSummary['projectCount']}"

    )

    print(

        f"Items Validated    : {validationSummary['itemCount']}"

    )

    print(

        "Status             : PASSED"

    )

    print("=" * 80)

    print()