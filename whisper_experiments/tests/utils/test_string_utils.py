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


@pytest.mark.parametrize(
    "line_1, line_2, diff_words",
    [
        ("", "", []),
        ("a", "", [RW("a")]),
        ("", "a", [AW("a")]),
        ("a", "b", [RW("a"), AW("b")]),
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
        # word_differences() should not include unchanged words (e.g. "foobar")
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


@pytest.mark.parametrize(
    "text_1, text_2, diff_lines",
    [
        ("", "", []),
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
