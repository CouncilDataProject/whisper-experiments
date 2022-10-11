#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from cdp_backend.sr_models.google_cloud_sr_model import GoogleCloudSRModel
from tqdm.contrib.concurrent import thread_map

from .data import FullDatasetFields

###############################################################################


@dataclass
class GSRTranscribeParams:
    row: pd.Series
    credentials_file: str
    storage_dir: Path


def _wrapped_gsr_transcribe(
    params: GSRTranscribeParams,
) -> pd.Series:
    # Init
    model = GoogleCloudSRModel(credentials_file=params.credentials_file)

    # Transcribe
    start_time = time.time()
    transcript = model.transcribe(
        params.row.audio_uri,
    )
    end_time = time.time()

    # Dump to disk
    local_storage_path = params.storage_dir / f"{params.row.id}.json"
    with open(local_storage_path, "w") as open_f:
        open_f.write(transcript.to_json(indent=4))

    # Add local storage path to row and return
    params.row[FullDatasetFields.gsr_transcript_path] = local_storage_path
    params.row[FullDatasetFields.gsr_transcription_time] = end_time - start_time
    return params.row


def generate_google_sr_dataset(
    sessions: pd.DataFrame,
    credentials_file: str,
    storage_dir: Path = Path("gsr-transcripts/"),
) -> pd.DataFrame:
    """
    Process the audio files from the dataset with Google Speech-to-Text.

    Parameters
    ----------
    sessions: pd.DataFrame
        The source dataset to use for processing.
    credentials_file: str
        The path to the Google Service Account Credentials JSON for the
        processing account / project.
    storage_dir: Path
        The path to a directory to store the generated transcripts in.
        Default: gsr-transcripts/

    Returns
    -------
    pd.DataFrame
        The same session dataset with GSR transcription columns added.
        Note: the rows may be in different order due to threading.

    See Also
    --------
    whisper_experiments.data.get_ground_truth_dataset
        The data that should be provided to this function.

    Note
    ----
    Whatever directory is provided as the storage_dir be emptied prior to run.
    """
    # Empty Directory
    if storage_dir.exists():
        shutil.rmtree(storage_dir)

    # Create again
    storage_dir.mkdir(parents=True)

    # Transcribe
    transcribed_results = thread_map(
        _wrapped_gsr_transcribe,
        [
            GSRTranscribeParams(
                row,
                credentials_file=credentials_file,
                storage_dir=storage_dir,
            )
            for _, row in sessions.iterrows()
        ],
    )

    # Merge back to DataFrame and return
    return pd.DataFrame(transcribed_results)
