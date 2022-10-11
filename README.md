# whisper-experiments

[![Build Status](https://github.com/councildataproject/whisper-experiments/workflows/CI/badge.svg)](https://github.com/councildataproject/whisper-experiments/actions)
[![Documentation](https://github.com/councildataproject/whisper-experiments/workflows/Documentation/badge.svg)](https://councildataproject.github.io/whisper-experiments)

Experiments and planning for potential integration of OpenAIs whisper Speech-to-Text model into CDP.

---

## Installation

**Stable Release:** `pip install whisper-experiments`<br>
**Development Head:** `pip install git+https://github.com/councildataproject/whisper-experiments.git`

## Quickstart

### Loading the Experiment Data

```python
from whisper_experiments import data

sessions = data.load_cdp_whisper_experiment_data()
print(sessions)

#    audio_uri                 ground_truth_transcript_path  ...  gsr_transcript_path  gsr_transcription_time
# 0  gs://cdp-seattle-2172...  /home/eva/active/...  ...  /home/eva/active/...             546.295414
# 1  gs://cdp-seattle-2172...  /home/eva/active/...  ...  /home/eva/active/...            2080.045368
# 2  gs://cdp-seattle-2172...  /home/eva/active/...  ...  /home/eva/active/...            2751.341955
# 3  gs://cdp-seattle-2172...  /home/eva/active/...  ...  /home/eva/active/...            1188.916651
# 4  gs://cdp-seattle-2172...  /home/eva/active/...  ...  /home/eva/active/...            1537.532535
#
# [5 rows x 9 columns]
```

### String Comparison

```python
from whisper_experiments.diff import text_differences

text_1 = (
    "Hello world\n"
    "How you doin'\n"
    "Nice to meet you\n"
)
text_2 = (
    "Hello world\n"
    "How yoou doin'\n"
    "Fine, thank you\n"
)
diffs = text_differences(text_1, text_2)
print(diffs)

# similarity: 83.33333333333334
# lines: [
#     line: Modified: How you doin' -> How yoou doin'
#     words: [Modified: you -> yoou]
# 
#     line: Removed: Nice to meet you
#     words: [Removed: Nice, Removed: to, Removed: meet, Removed: you]
# 
#     line: Added: Fine, thank you
#     words: [Added: Fine,, Added: thank, Added: you]
#
# ]
```

## Documentation

For full package documentation please visit [councildataproject.github.io/whisper-experiments](https://councildataproject.github.io/whisper-experiments).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

**MIT License**
