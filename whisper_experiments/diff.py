#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import filterfalse
from typing import (
    Callable,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

import rapidfuzz
import text_diff
from text_diff import AddedLine, ModifiedLine, RemovedLine, UnchangedLine

###############################################################################

# Aliases to just indicate the object refers to a word
ModifiedWord = ModifiedLine
RemovedWord = RemovedLine
AddedWord = AddedLine
Word = Union[ModifiedLine, RemovedLine, AddedLine]
Line = Union[ModifiedLine, RemovedLine, AddedLine]
TextType = Union[Word, Line]

###############################################################################


class TextDiff:
    """
    Wrapper for text_diff objects e.g. ModifiedLine.
    """

    def __init__(self, text_diff: TextType):
        """
        Parameters
        ----------
        text_diff: TextType
            The text_diff object to wrap
        """
        self.text_diff = text_diff

    def __eq__(self, other: object) -> bool:
        # Mypy typing tries it's hardest:
        # https://stackoverflow.com/a/54816069
        if not isinstance(other, TextDiff):
            raise NotImplementedError(
                "TextDiff can only assert equals when provided "
                "another TextDiff object."
            )

        return (
            self.is_removed == other.is_removed
            and self.is_added == other.is_added
            and self.is_modified == other.is_modified
            and self.content == other.content
            and self.content_before == other.content_before
            and self.content_after == other.content_after
        )

    def __str__(self) -> str:
        if self.is_modified:
            return f"Modified: {self.content_before} -> {self.content_after}"
        if self.is_removed:
            return f"Removed: {self.content}"
        return f"Added: {self.content}"

    @property
    def is_removed(self) -> bool:
        """
        Returns
        -------
        bool
            True if wrapped text is removed from left version to right
        """
        return isinstance(self.text_diff, RemovedLine)

    @property
    def is_added(self) -> bool:
        """
        Returns
        -------
        bool
            True if wrapped text is added from left version to right
        """
        return isinstance(self.text_diff, AddedLine)

    @property
    def is_modified(self) -> bool:
        """
        Returns
        -------
        bool
            True if wrapped text is modified from left version to right
        """
        return isinstance(self.text_diff, ModifiedLine)

    @property
    def content(self) -> Optional[str]:
        """
        Returns
        -------
        Optional[str]
            The wrapped text. None if is_modified() == True.

        Notes
        -----
        If wrapped text is modified, it cannot be decided which content to return,
        i.e. the left or the right version.
        """
        return getattr(self.text_diff, "content", None)

    @property
    def content_before(self) -> Optional[str]:
        """
        Returns
        -------
        Optional[str]
            The left version of the wrapped text.
            None if is_added() == True
        """
        if self.is_removed:
            return self.content
        return getattr(self.text_diff, "content_before", None)

    @property
    def content_after(self) -> Optional[str]:
        """
        Returns
        -------
        Optional[str]
            The right version of the wrapped text.
            None if is_removed() == True
        """
        if self.is_added:
            return self.content
        return getattr(self.text_diff, "content_after", None)


class LineComparison(NamedTuple):
    # Union[ModifiedLine, RemovedLine, AddedLine] wrapped in TextDiff
    line: TextDiff
    # List of different words in this line
    words: List[TextDiff]

    def __str__(self) -> str:
        words_str = ", ".join(map(str, self.words))
        return f"    line: {self.line}\n" f"    words: [{words_str}]\n"


class TextComparison(NamedTuple):
    # Similarity score between the left and the right text blobs
    similarity: float
    # List of different lines
    lines: List[LineComparison]

    def __eq__(self, other: object) -> bool:
        # Mypy typing tries it's hardest:
        # https://stackoverflow.com/a/54816069
        if not isinstance(other, TextComparison):
            raise NotImplementedError(
                "TextComparison can only assert equals when provided "
                "another TextComparison object."
            )

        return self.similarity == other.similarity and self.lines == other.lines

    def __str__(self) -> str:
        lines_str = "\n".join(map(str, self.lines))
        return f"similarity: {self.similarity}\n" f"lines: [\n{lines_str}\n]"


def _is_unchanged(text_diff: TextType) -> bool:
    """
    Helper function to filter out text does not change from left to right.
    """
    return isinstance(text_diff, UnchangedLine)


def word_differences(
    words_1: Iterable[str], words_2: Iterable[str]
) -> Iterator[TextDiff]:
    """
    Return list of removed/added/modified words bewteen the given lists of words.

    Parameters
    ----------
    words_1: Iterable[str]
        Left list of words
    words_2: Iterable[str]
        Right list of words

    Returns
    -------
    TextDiff
        Union[RemovedWord, AddedWord, ModifiedWord] wrapped as TextDiff

    See Also
    --------
    text_differences
        Calculate similarity of the texts and all line differences.

    Notes
    -----
    Unchanged words are excluded.
    """
    diff_words = text_diff.text_differences(words_1, words_2).diff_lines
    diff_words = filterfalse(_is_unchanged, diff_words)
    return map(TextDiff, diff_words)


def line_differences(
    lines_1: Iterable[str],
    lines_2: Iterable[str],
    word_split_func: Callable[[str], Iterable[str]] = str.split,
) -> Iterator[LineComparison]:
    """
    Return list of removed/added/modified lines.

    Parameters
    ----------
    lines_1: Iterable[str]
        Left list of lines
    lines_2: Iterable[str]
        Right list of lines
    word_split_func: Callable[[str], Iterable[str]]
        Function used to split a line into words.
        Default is str.split()

    Yields
    ------
    LineComparison
        Union[RemovedLine, AddedLine, ModifiedLine] wrapped as TextDiff
        List of different words in the line

    See Also
    --------
    text_differences
        Calculate similarity of the texts and all line differences.
    word_differences
        Calculate just word differences.

    Notes
    -----
    Unchanged lines are excluded.
    """

    def increment_line_num(
        line: Line, line_index_1: int, line_index_2: int
    ) -> Tuple[int, int]:
        """
        Return incremented line numbers.
        """
        if isinstance(line, (UnchangedLine, ModifiedLine)):
            return line_index_1 + 1, line_index_2 + 1
        if isinstance(line, AddedLine):
            return line_index_1, line_index_2 + 1
        if isinstance(line, RemovedLine):
            return line_index_1 + 1, line_index_2
        raise TypeError

    def get_words_to_compare(line: Line) -> Tuple[Iterable[str], Iterable[str]]:
        """
        Make lists of words from this line
        """
        if isinstance(line, ModifiedLine):
            # line is modified, so split both left and right versions of the line
            # in order to compare the words
            return word_split_func(line.content_before), word_split_func(
                line.content_after
            )

        words = word_split_func(line.content)
        if isinstance(line, RemovedLine):
            # Line is removed from left to right
            # so list of words is empty in the right version.
            return words, list()
        if isinstance(line, AddedLine):
            # Line is added from left to right
            # so list of words is empty in the left version.
            return list(), words
        return words, words

    line_num_1 = 0
    line_num_2 = 0

    # diff_line is RemovedLine, AddedLine, ModifiedLine, or UnchangedLine
    for diff_line in text_diff.text_differences(lines_1, lines_2).diff_lines:
        line_num_1, line_num_2 = increment_line_num(diff_line, line_num_1, line_num_2)

        # Same lines are excluded
        if not _is_unchanged(diff_line):
            words_1, words_2 = get_words_to_compare(diff_line)
            yield LineComparison(
                TextDiff(diff_line), list(word_differences(words_1, words_2))
            )


def text_differences(
    text_1: str,
    text_2: str,
    similarity_calc: Callable[[str, str], float] = rapidfuzz.fuzz.QRatio,
    word_split_func: Callable[[str], Iterable[str]] = str.split,
) -> TextComparison:
    """
    Compare left and right text blobs.
    They are first compared as lines, then as words for the changed lines.

    Parameters
    ----------
    text_1: str
        Left text
    text_2: str
        Right text
    similarity_calc: Callable[[str, str], float]
        Function used to calculate similarity score.
        Default is rapidfuzz.fuzz.QRatio()
    word_split_func: Callable[[str], Iterable[str]]
        Function used to split a line into words.
        Default is str.split()

    Returns
    -------
    TextComparison
        Similarity score
        List of different lines

    See Also
    --------
    line_differences
        Calculate just line differences.

    Notes
    -----
    Unchanged lines are excluded.
    """
    return TextComparison(
        similarity_calc(text_1, text_2),
        list(
            line_differences(text_1.splitlines(), text_2.splitlines(), word_split_func)
        ),
    )
