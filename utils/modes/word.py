from collections import defaultdict
from typing import List, Tuple

from utils.modes.alignment import Alignment


class WordAlignment(Alignment):
    def __init__(self, source_line: str, is_flipped: bool = False, **alignment_kwargs):
        super().__init__()
        self.is_flipped = is_flipped

        fields = source_line.split("\t")
        self.source_words = fields[0].split()
        self.target_words = fields[1].split()
        if is_flipped is True:
            self.source_words, self.target_words = self.target_words, self.source_words

        alignment = defaultdict(set)
        for a in fields[2].split():
            source_index, target_index = a.split('-', 1)
            source_index, target_index = int(source_index), int(target_index)
            if self.is_flipped is True:
                source_index, target_index = target_index, source_index
            alignment[source_index].add(target_index)

        # Convert to character alignment (on source side)
        self.source_characters = []
        self.alignment = defaultdict(set)
        for source_index, source_word in enumerate(self.source_words):
            if source_index > 0:
                self.source_characters.append(" ")
            for target_index in alignment[source_index]:
                for source_character_index in \
                        range(len(self.source_characters), len(self.source_characters) + len(source_word)):
                    self.alignment[source_character_index].add(target_index)
            self.source_characters.extend(source_word)

    def __str__(self):
        # Convert back to word alignment (on source side)
        alignment = []
        source_character_index: int = 0
        for source_index, source_word in enumerate(self.source_words):
            if source_index > 0:
                source_character_index += 1
            word_alignment = set()
            for source_span_index in range(source_character_index, source_character_index + len(source_word)):
                word_alignment |= self.alignment[source_span_index]
            alignment.extend((source_index, target_index) for target_index in word_alignment)
            source_character_index += len(source_word)

        if self.is_flipped is False:
            return "%s\t%s\t%s" % (
                "".join(self.source_characters),
                " ".join(self.target_words),
                " ".join("%s-%s" % (source_index, target_index) for (source_index, target_index) in alignment)
            )
        else:
            return "%s\t%s\t%s" % (
                " ".join(self.target_words),
                "".join(self.source_characters),
                " ".join("%s-%s" % (target_index, source_index) for (source_index, target_index) in alignment)
            )

    def get_characters(self):
        return self.source_characters

    def project(self, target_spaced_line: str, character_alignment: List[Tuple[int, int]]):
        alignment = defaultdict(set)
        for source_character_index, target_character_index in character_alignment:
            alignment[target_character_index] |= self.alignment[source_character_index]
        self.alignment = alignment
        self.source_characters = target_spaced_line
        self.source_words = target_spaced_line.split()
