#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

import pandas as pd
from cdp_data import CDPInstances, datasets

###############################################################################

INFRASTRUCTURE_SLUG = CDPInstances.Seattle
AUDIO_URI_TEMPLATE = "gs://{instance}.appspot.com/{session_content_hash}-audio.wav"
ARCHIVED_DATA_PATH = (
    Path(__file__).parent / "assets" / "cdp-whisper-experiments-data.zip"
)
UNPACKED_ARCHIVE_DATA_DIR = Path("cdp-whisper-experiments-data/")

###############################################################################


class GroundTruthDatasetFields:
    id_ = "id"
    key = "key"
    session_datetime = "session_datetime"
    session_index_in_event = "session_index_in_event"
    session_content_hash = "session_content_hash"
    audio_uri = "audio_uri"
    ground_truth_transcript_path = "ground_truth_transcript_path"


ALL_GROUND_TRUTH_DATASET_FIELDS = [
    getattr(GroundTruthDatasetFields, attr)
    for attr in dir(GroundTruthDatasetFields)
    if "__" not in attr
]


class FullDatasetFields:
    id_ = "id"
    key = "key"
    session_datetime = "session_datetime"
    session_index_in_event = "session_index_in_event"
    session_content_hash = "session_content_hash"
    audio_uri = "audio_uri"
    ground_truth_transcript_path = "ground_truth_transcript_path"
    gsr_transcript_path = "gsr_transcript_path"
    gsr_transcription_time = "gsr_transcription_time"


ALL_FULL_DATASET_FIELDS = [
    getattr(FullDatasetFields, attr)
    for attr in dir(FullDatasetFields)
    if "__" not in attr
]

###############################################################################


def get_ground_truth_dataset(test: bool = False) -> pd.DataFrame:
    """
    Get the dataset we are using for testing Google Speech-to-Text and Whisper.

    Parameters
    ----------
    test: bool
        If true, get a smaller, 5 file, test set.
        Default: False (use the full ~50 file dataset)

    Returns
    -------
    pd.DataFrame
        DataFrame returned from cdp_data.datasets.get_session_dataset.
        Additional "audio_uri" column is added.

    See Also
    --------
    cdp_data.dataset.get_session_dataset
        The primary function this function wraps.
    """
    # Handle small test dataset or full
    start_dt = "2020-08-01"
    if test:
        end_dt = "2020-08-15"
    else:
        end_dt = "2020-11-01"

    # Pull data
    sessions = datasets.get_session_dataset(
        infrastructure_slug=INFRASTRUCTURE_SLUG,
        start_datetime=start_dt,
        end_datetime=end_dt,
        store_transcript=True,
    )

    # For each session, generate the audio URI
    sessions[GroundTruthDatasetFields.audio_uri] = sessions[
        GroundTruthDatasetFields.session_content_hash
    ].apply(
        lambda session_content_hash: AUDIO_URI_TEMPLATE.format(
            instance=INFRASTRUCTURE_SLUG,
            session_content_hash=session_content_hash,
        )
    )

    # Rename columns
    sessions = sessions.rename(
        columns={
            "session_index": GroundTruthDatasetFields.session_index_in_event,
            "transcript_path": GroundTruthDatasetFields.ground_truth_transcript_path,
        }
    )

    # Subset fields
    return sessions[ALL_GROUND_TRUTH_DATASET_FIELDS]


def _archive_dataset(
    sessions: pd.DataFrame,
    archive_name: Path = ARCHIVED_DATA_PATH.with_suffix(""),
    temp_work_dir: Path = Path(".tmp-archive-work-dir/"),
) -> Path:
    """
    Prepare the stored archive of the data used in this lil' experiment.
    """
    try:
        # Empty working directory
        if temp_work_dir.exists():
            shutil.rmtree(temp_work_dir)

        # Create working directory
        temp_work_dir.mkdir(parents=True)

        # Helper to copy to new location and return relative path from working dir
        def _copy_return_relative_path(
            current_path: str,
            new_filepath: Path,
            working_dir: Path,
        ) -> str:
            shutil.copy(current_path, new_filepath)
            relative_path = new_filepath.relative_to(working_dir)
            return str(relative_path)

        # Move each file into dir and update paths
        for i, row in sessions.iterrows():
            # Make the session sub-dir
            session_dir = temp_work_dir / row[FullDatasetFields.id_]
            session_dir.mkdir()

            # Copy and update the transcript paths
            for path_col, fname in (
                (FullDatasetFields.ground_truth_transcript_path, "ground-truth.json"),
                (FullDatasetFields.gsr_transcript_path, "gsr.json"),
            ):
                sessions.at[i, path_col] = _copy_return_relative_path(
                    row[path_col],
                    session_dir / fname,
                    temp_work_dir,
                )

        # Store updated sessions df to archive
        sessions.to_parquet(temp_work_dir / "data.parquet")

        # Create archive
        shutil.make_archive(str(archive_name), "zip", temp_work_dir)
        return archive_name.with_suffix(".zip")

    # Always cleanup work dir
    finally:
        shutil.rmtree(temp_work_dir)


def load_cdp_whisper_experiment_data(
    storage_dir: Path = UNPACKED_ARCHIVE_DATA_DIR,
) -> pd.DataFrame:
    """
    Load the archived and packaged data shipped with this library back into a
    pandas DataFrame with transcript paths fully resolved.

    Will empty the provided storage_dir prior to unpacking.
    """
    # Empty working directory
    if storage_dir.exists():
        shutil.rmtree(storage_dir)

    # Create working directory
    storage_dir.mkdir(parents=True)

    # Unpack archive
    shutil.unpack_archive(ARCHIVED_DATA_PATH, storage_dir)

    # Load data and fix paths
    sessions = pd.read_parquet(storage_dir / "data.parquet")
    for i, row in sessions.iterrows():
        # Copy and update the transcript paths
        for path_col in (
            FullDatasetFields.ground_truth_transcript_path,
            FullDatasetFields.gsr_transcript_path,
        ):
            sessions.at[i, path_col] = (storage_dir / row[path_col]).resolve()

    return sessions
