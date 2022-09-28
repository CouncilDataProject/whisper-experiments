import pytest
from whisper_experiments.utils.string_utils import (
    TextDiff,
    Line,
    AddedWord,
    RemovedWord,
    ModifiedWord,
    LineComparison,
    word_differences,
    line_differences,
)
from text_diff import AddedLine, RemovedLine, ModifiedLine, Mask
from typing import List

AL = AddedLine
RL = RemovedLine
ML = ModifiedLine
AW = AddedWord
RW = RemovedWord
MW = ModifiedWord
T = TextDiff
LC = LineComparison


# This test is just a sanity check for [Removed|Added|Modified]Line objects.
# - Objects of the different types must be evaluted as not equal.
# - Objects of same type and different underlying texts must be evaluated as not equal.
@pytest.mark.parametrize(
    "text_diff_1, text_diff_2, equality",
    [
        (AL(""), AL(""), True),
        (AL("a"), AL(""), False),
        (RL(""), AL(""), False),
        (
            ML(
                content_before="",
                mask_before=Mask(list()),
                content_after="",
                mask_after=Mask(list()),
            ),
            AL(""),
            False,
        ),
        (RL(""), RL(""), True),
        (RL("a"), RL(""), False),
        (
            RL(""),
            ML(
                content_before="",
                mask_before=Mask(list()),
                content_after="",
                mask_after=Mask(list()),
            ),
            False,
        ),
        (
            ML(
                content_before="",
                mask_before=Mask(list()),
                content_after="",
                mask_after=Mask(list()),
            ),
            ML(
                content_before="",
                mask_before=Mask(list()),
                content_after="",
                mask_after=Mask(list()),
            ),
            True,
        ),
        (
            ML(
                content_before="a",
                mask_before=Mask(list()),
                content_after="",
                mask_after=Mask(list()),
            ),
            ML(
                content_before="",
                mask_before=Mask(list()),
                content_after="",
                mask_after=Mask(list()),
            ),
            False,
        ),
    ],
)
def test_text_diff_eq(text_diff_1: Line, text_diff_2: Line, equality: bool) -> None:
    assert (T(text_diff_1) == T(text_diff_2)) == equality


# Test word_differences() i.e. comparing line 1 and 2 as lists of words
@pytest.mark.parametrize(
    "line_1, line_2, diff_words",
    [
        ("", "", []),
        # The word 'a' exists in left line, not in right line
        # so I expect the function to return RemovedWord('a')
        ("a", "", [RW("a")]),
        ("", "a", [AW("a")]),
        ("a", "b", [RW("a"), AW("b")]),
        # The lines are similar enough to be determined as modified
        # as opposed to completely removed or added
        (
            "ab",
            "abb",
            [
                MW(
                    content_before="ab",
                    mask_before=Mask(list()),
                    content_after="abb",
                    mask_after=Mask(list()),
                )
            ],
        ),
        # word_differences() should not include unchanged words (i.e. "foobar")
        # so the result should be same as above test case
        (
            "ab foobar",
            "abb foobar",
            [
                MW(
                    content_before="ab",
                    mask_before=Mask(list()),
                    content_after="abb",
                    mask_after=Mask(list()),
                )
            ],
        ),
    ],
)
def test_word_differences(line_1: str, line_2: str, diff_words: List[T]) -> None:
    words_1 = line_1.split()
    words_2 = line_2.split()
    assert list(word_differences(words_1, words_2)) == list(map(T, diff_words))


# Test text_differences() i.e.
# 1. compare two text blobs as lines of text
# 2. then compare the words in the removed/added/modified lines
@pytest.mark.parametrize(
    "text_1, text_2, diff_lines",
    [
        ("", "", []),
        # Left blob has a line with a single word 'a'
        # that is 'removed' going to the right line.
        # Thus, there is a RemovedLine('a'), which has a RemovedWord('a')
        ("a", "", [LC(T(RL("a")), [T(RW("a"))])]),
        ("", "a", [LC(T(AL("a")), [T(AW("a"))])]),
        ("a", "b", [LC(T(RL("a")), [T(RW("a"))]), LC(T(AL("b")), [T(AW("b"))])]),
        (
            "ab",
            "abb",
            [
                LC(
                    T(
                        ML(
                            content_before="ab",
                            mask_before=Mask(list()),
                            content_after="abb",
                            mask_after=Mask(list()),
                        )
                    ),
                    [
                        T(
                            MW(
                                content_before="ab",
                                mask_before=Mask(list()),
                                content_after="abb",
                                mask_after=Mask(list()),
                            )
                        )
                    ],
                )
            ],
        ),
        # - First line is the same in both blobs so should be excluded in response
        # - Second line is similar but changed from left to right (ModifiedLine)
        # - and in the line there is 1 word that is changed (ModifiedWord)
        (
            "hello world\nhow are you",
            "hello world\nhow are yoou",
            [
                LC(
                    T(
                        ML(
                            content_before="how are you",
                            mask_before=Mask(list()),
                            content_after="how are yoou",
                            mask_after=Mask(list()),
                        )
                    ),
                    [
                        T(
                            MW(
                                content_before="you",
                                mask_before=Mask(list()),
                                content_after="yoou",
                                mask_after=Mask(list()),
                            )
                        )
                    ],
                )
            ],
        ),
    ],
)
def test_line_differences(text_1: str, text_2: str, diff_lines: List[LC]) -> None:
    lines_1 = text_1.splitlines()
    lines_2 = text_2.splitlines()
    assert list(line_differences(lines_1, lines_2)) == diff_lines
