# Quickstart

[`string_utils.text_differences()`](./string_utils.py) is a wrapper around
[`text_diff.text_differences()`](https://github.com/Envinorma/text_diff/blob/33353ca34c63620ee8344a17f7e938c391785e04/text_diff/extract_diff.py#L158),
which in turn is a wrapper around [`difflib.unified_diff()`](https://docs.python.org/3.8/library/difflib.html#difflib.unified_diff).

```Python
from whisper_experiments.utils.string_utils import text_differences

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

Unchanged lines and words are omitted in the `TextComparison` return object from `text_differences()`.

# `TextDiff`

Every line or word is stored as a `TextDiff`.
In the above example, the second line was determined to be modified, going from the left to the right version.
Changes in modified lines (words) can be retrieved by `content_before` and `content_after` property methods.

```Python
print(
    f"content_before: {diffs.lines[0].line.content_before}\n"
    f"content_after: {diffs.lines[0].line.content_after}"
)

# content_before: How you doin'
# content_after: How yoou doin'
```

`content_before` and `content_after` are really not meaningful for removed or added lines.
Use the `content` property method for those.

```Python
print(f"content: {diffs.lines[1].line.content}")
# content: Nice to meet you
```

The content getter property methods will return `None` if illogical.

```Python
print(
    f"content_before: {diffs.lines[1].line.content_before}\n"
    # lines[1] is a removed line going from left to right, so content_after is None
    f"content_after: {diffs.lines[1].line.content_after}"
)

# content_before: Nice to meet you
# content_after: None

print(
    f"content_before: {diffs.lines[2].line.content_before}\n"
    f"content_after: {diffs.lines[2].line.content_after}"
)

# content_before: None
# content_after: Fine, thank you

# both content_before and content_after exist for this modified line
print(f"content: {diffs.lines[0].line.content}")
# content: None
```

## `is_removed`, `is_added`, `is_modified`

```Python
for line in diffs.lines:
    print(f"is_removed {line.line.is_removed}, is_added {line.line.is_added}, is_modified {line.line.is_modified}")

# is_removed False, is_added False, is_modified True
# is_removed True, is_added False, is_modified False
# is_removed False, is_added True, is_modified False
```

## `text_diff`

The wrapped `text_diff` object is available in every `TextDiff` object, via the `text_diff` attribute.

```Python
print(type(diffs.lines[0].line.text_diff))
print(diffs.lines[0].line.text_diff)

# <class 'text_diff.extract_diff.ModifiedLine'>
# ModifiedLine(content_before="How you doin'", mask_before="             ", content_after="How yoou doin'", mask_after="     +")
```

# Types

`text_differences()` returns `TextComparision`.

```Python
class TextComparison(NamedTuple):
    # Similarity score between the left and the right text blobs
    similarity: float
    # List of different lines
    lines: List[LineComparison]
```

Which contains a list of `LineComparison` for every removed, added or modified line.
`LineComparison` in turn contains a list of removed, added or modified words in the line.

```Python
class LineComparison(NamedTuple):
    # Union[ModifiedLine, RemovedLine, AddedLine] wrapped in TextDiff
    line: TextDiff
    # List of different words in this line
    words: List[TextDiff]
```

`TextDiff` is a simple wrapper for `text_diff` types, such as `ModifiedLine`.

```Python
print(type(diffs), end="\n\n")
for line in diffs.lines:
    print(type(line))
    print(f"line: TextDiff[{type(line.line.text_diff)}]")
    print(f"words: [{', '.join(list(map(lambda w: f'TextDiff[{type(w.text_diff)}', line.words)))}]]\n")

# <class 'whisper_experiments.utils.string_utils.TextComparison'>
#
# <class 'whisper_experiments.utils.string_utils.LineComparison'>
# line: TextDiff[<class 'text_diff.extract_diff.ModifiedLine'>]
# words: [TextDiff[<class 'text_diff.extract_diff.ModifiedLine'>]]
#
# <class 'whisper_experiments.utils.string_utils.LineComparison'>
# line: TextDiff[<class 'text_diff.extract_diff.RemovedLine'>]
# words: [TextDiff[<class 'text_diff.extract_diff.RemovedLine'>, TextDiff[<class 'text_diff.extract_diff.RemovedLine'>, TextDiff[<class 'text_diff.extract_diff.RemovedLine'>, TextDiff[<class 'text_diff.extract_diff.RemovedLine'>]]
#
# <class 'whisper_experiments.utils.string_utils.LineComparison'>
# line: TextDiff[<class 'text_diff.extract_diff.AddedLine'>]
# words: [TextDiff[<class 'text_diff.extract_diff.AddedLine'>, TextDiff[<class 'text_diff.extract_diff.AddedLine'>, TextDiff[<class 'text_diff.extract_diff.AddedLine'>]]
```
