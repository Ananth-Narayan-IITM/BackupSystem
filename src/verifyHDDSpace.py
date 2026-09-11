# src/verifyHDDSpace.py

from pathlib import Path
import shutil


def VERIFY_HDD_SPACE(yamlDictionary):

    if not yamlDictionary.get("verifyHDDSpace", False):
        return None

    hardDisk = Path(yamlDictionary["hardDisk"])

    total, used, free = _GET_DISK_SPACE(hardDisk)

    margin = _PARSE_MARGIN(yamlDictionary["marginSpace"])

    if free < margin:
        raise RuntimeError(
            "\n" + "=" * 80 + "\n"
            "ERROR\n" + "=" * 80 + "\n"
            f"Insufficient HDD space.\n\n"
            f"Required Margin : {_FORMAT_SIZE(margin)}\n"
            f"Available Space : {_FORMAT_SIZE(free)}\n\n"
            "Please free HDD space before running BackupSystem.\n" + "=" * 80
        )

    summary = {
        "total": total,
        "used": used,
        "free": free,
        "margin": margin,
        "availableAfterMargin": free - margin,
    }

    _PRINT_SUMMARY(summary, hardDisk)

    return summary


def _GET_DISK_SPACE(hardDisk):

    usage = shutil.disk_usage(hardDisk)

    return (usage.total, usage.used, usage.free)


def _PARSE_MARGIN(marginString):

    marginString = marginString.upper().strip()

    if marginString.endswith("GB"):
        value = float(marginString[:-2])

        return int(value * 1024**3)

    elif marginString.endswith("MB"):
        value = float(marginString[:-2])

        return int(value * 1024**2)

    else:
        raise ValueError("\nmarginSpace must be specified as MB or GB.\nExamples:\n500MB\n5GB")


def _FORMAT_SIZE(size):

    if size >= 1024**3:
        return f"{size / 1024**3:.2f} GB"

    return f"{size / 1024**2:.2f} MB"


def _PRINT_SUMMARY(summary, hardDisk):

    print()

    print("=" * 80)

    print("HDD SPACE SUMMARY")

    print("=" * 80)

    print()

    print(f"HDD Location           : {hardDisk}")

    print(f"Total Space            : {_FORMAT_SIZE(summary['total'])}")

    print(f"Used Space             : {_FORMAT_SIZE(summary['used'])}")

    print(f"Free Space             : {_FORMAT_SIZE(summary['free'])}")

    print(f"Required Margin        : {_FORMAT_SIZE(summary['margin'])}")

    print(f"Available After Margin : {_FORMAT_SIZE(summary['availableAfterMargin'])}")

    print()

    print("Status : PASS")

    print("=" * 80)

    print()
