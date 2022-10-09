#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from cdp_data import CDPInstances, datasets

###############################################################################

INFRASTRUCTURE_SLUG = CDPInstances.Seattle
AUDIO_URI_TEMPLATE = "gs://{instance}.appspot.com/{session_content_hash}-audio.wav"

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
    for attr in dir(GroundTruthDatasetFields) if "__" not in attr
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
    for attr in dir(FullDatasetFields) if "__" not in attr
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
    sessions[GroundTruthDatasetFields.audio_uri] = (
        sessions[GroundTruthDatasetFields.session_content_hash].apply(
            lambda session_content_hash: AUDIO_URI_TEMPLATE.format(
                instance=INFRASTRUCTURE_SLUG,
                session_content_hash=session_content_hash,
            )
        )
    )

    # Rename columns
    sessions = sessions.rename(columns={"session_index": GroundTruthDatasetFields.session_index_in_event, "transcript_path": GroundTruthDatasetFields.ground_truth_transcript_path,})

    # Subset fields
    return sessions[ALL_GROUND_TRUTH_DATASET_FIELDS]
