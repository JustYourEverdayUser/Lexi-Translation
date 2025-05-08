"""Module with methods for `invalidate_sort()` and `invalidate_filter()` methods"""

from lexi import shared
from lexi.ui.WordRow import WordRow


# pylint: disable=no-else-return
def sort_words(row1: WordRow, row2: WordRow) -> int:
    """
    Sort words in the list box based on the selected method and type.

    Parameters
    ----------
    row1 : WordRow
        The first word row to compare.
    row2 : WordRow
        The second word row to compare.

    Returns
    -------
    int
        -1 if row1 < row2, 1 if row1 > row2, 0 if they are equal.
    """
    sortable1: str | int
    sortable2: str | int

    if shared.win.sort_type == "word":
        sortable1 = row1.word.word.lower()
        sortable2 = row2.word.word.lower()
    elif shared.win.sort_type == "first_trnslt":
        sortable1 = row1.word.translations[0].lower() if row1.word.translations else ""
        sortable2 = row2.word.translations[0].lower() if row2.word.translations else ""
    else:
        sortable1 = row1.word.ref_count
        sortable2 = row2.word.ref_count

    if shared.win.sort_method == "up":
        if sortable1 > sortable2:
            return 1
        elif sortable1 < sortable2:
            return -1
        else:
            return 0
    else:
        if sortable1 < sortable2:
            return 1
        elif sortable1 > sortable2:
            return -1
        else:
            return 0
