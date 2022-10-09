#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import traceback
from pathlib import Path

from whisper_experiments import data, model

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

class Args(argparse.Namespace):
    def __init__(self) -> None:
        self.__parse()

    def __parse(self) -> None:
        p = argparse.ArgumentParser(
            prog="generate_and_archive_cdp_whisper_experiments_data",
            description=(
                "Pull the ground truth data, generate GSR and Whisper "
                "transcript versions, store to archive file."
            ),
        )
        p.add_argument(
            "credentials_path",
            type=str,
            help=(
                "The path to the Google Service Account Credentials JSON for "
                "the processing account / project."
            ),
        )
        p.add_argument(
            "-t",
            "--test",
            action="store_true",
            help="Pull and generate comparison transcripts for only five sessions.",
        )
        p.add_argument(
            "--debug",
            action="store_true",
            help="Run with debug logging",
        )
        p.parse_args(namespace=self)


###############################################################################

def _generate_and_archive_data(
    test: bool,
    credentials_path: str,
) -> Path:
    # Pull basic dataset and transcripts
    log.info("Pulling sessions and ground truth transcripts.")
    sessions = data.get_ground_truth_dataset(test=test)

    # Fill dataset with google generated transcripts
    log.info("Generating Google Speech Recognition transcripts.")
    sessions = model.generate_google_sr_dataset(
        sessions=sessions,
        credentials_file=credentials_path,
    )

    # TODO: add Whisper

    # Create archive
    log.info("Creating and storing data archive.")
    return data._archive_dataset(sessions)


def main() -> None:
    try:
        args = Args()

        # Handle logging
        if args.debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format="[%(levelname)4s: %(module)s:%(lineno)4s %(asctime)s] %(message)s",
        )

        # Run
        _generate_and_archive_data(
            test=args.test,
            credentials_path=args.credentials_path,
        )

    except Exception as e:
        log.error("=============================================")
        log.error("\n\n" + traceback.format_exc())
        log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)


# Allow running this file as a standalone
if __name__ == "__main__":
    main()
