# whisper-experiments

[![Build Status](https://github.com/councildataproject/whisper-experiments/workflows/CI/badge.svg)](https://github.com/councildataproject/whisper-experiments/actions)
[![Documentation](https://github.com/councildataproject/whisper-experiments/workflows/Documentation/badge.svg)](https://councildataproject.github.io/whisper-experiments)

Experiments and planning for potential integration of OpenAIs whisper Speech-to-Text model into CDP.

---

## Installation

**Stable Release:** `pip install whisper-experiments`<br>
**Development Head:** `pip install git+https://github.com/councildataproject/whisper-experiments.git`

## Quickstart

### Dataset Gather and Preprocessing

```python
# TODO
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
