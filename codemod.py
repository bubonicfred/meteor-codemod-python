# pylint: disable=invalid-name
"""
This module is responsible for transforming files using a set of codemods.
It checks for errors during the transformation process and logs the progress.
If an error is encountered, the program will exit and report the error.
"""

import logging
import subprocess

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("transform.log", mode="w")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %I:%M:%S %p"
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

# Define codemods
CODEMODS = [
    "transform.ts",
    "transform-use-async-function.ts",
    "transform-export-async-function.ts",
    "transform-meteor-call.ts",
    "transform-rename-functions.ts",
    "transform-fix-async-overly.ts",
    "transform-find-await-without-async.ts",
]
# Set file to transform, set as a variable for testing. TODO make argument
file_to_transform = "../4minitz/server/end2end/end2end-helpers.js"


def run_codemod(file_to_transform, codemod):
    """
    Runs the specified codemod on the given file and logs the transformation.
    Args:
        file_to_transform (str): The path to the file to be transformed.
        codemod (str): The codemod to be applied.
    """
    cmd = "jscodeshift -t %s %s --parser=tsx >> codemod.temp" % (
        codemod,
        file_to_transform,
    )
    subprocess.run(cmd, shell=True, check=True)
    logger.info("Transforming %s with %s", file_to_transform, codemod)


def extract_stats():
    """
    Extracts statistics from the codemod.temp file and returns a dictionary of stats.
    """
    lines = []
    try:
        with open("codemod.temp", "r", encoding="utf-8") as file:
            lines = file.readlines()
    except IOError:
        logger.critical("Failed to open file")
        return

    if len(lines) < 5:
        logger.critical("File has fewer than 5 lines")
        return

    try:
        newstats = {}
        stats_names = ["errors", "unmodified", "skipped", "ok"]
        last_four_lines = lines[-5:-1]
        for name, line in zip(stats_names, last_four_lines):
            newstats[name] = int(line.split()[0])
    except ValueError:
        logger.critical("Failed to parse integer from line")
        return

    return newstats


def print_stats(stats):
    """
    Prints the statistics of the transformation.

    Args:
        stats (dict): A dictionary containing the statistics of the transformation.
    """
    for key, value in stats.items():
        logger.debug("%s:%s", key, value.strip())  # Remove trailing whitespace


def handle_error():
    """
    Handles errors encountered during transformation.
    """
    # TODO add logger functions
    run_codemod(file_to_transform, 5)
    run_codemod(file_to_transform, 6)


def next_step(stats):
    """
    Determines the next step based on the statistics of the transformation.

    Args:
        stats (dict): A dictionary containing the statistics of the transformation.

    Returns:
        int: Value to add to run_number for next run.
    """
    if stats["errors"] == 0:
        logger.info("No errors encountered during transformation")
        return 1
    else:
        handle_error()
        return 0


def main():
    """
    This is the main function that executes the codemods on the given file.
    """
    run_number = 0
    for codemod in CODEMODS:
        run_codemod(file_to_transform, codemod)
        stats = extract_stats()
        print_stats(stats)
        run_number += next_step(stats)
    if run_number == 3:
        if stats["ok"] != 0:
            # TODO add logger
            run_codemod(file_to_transform, CODEMODS[1])
            run_codemod(file_to_transform, CODEMODS[2])


# TODO add success detection
# TODO improve error handling

if __name__ == "__main__":
    main()
