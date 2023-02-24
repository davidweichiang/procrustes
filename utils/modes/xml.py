from typing import List, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from utils.modes.alignment import Alignment


class XMLAlignment(Alignment):
    def __init__(self, source_line: str, **alignment_kwargs):
        super().__init__()
        self.xml = ElementTree.fromstring(source_line)

    def __str__(self):
        return ElementTree.tostring(self.xml, encoding='unicode', method='xml')

    def get_characters(self):
        return ElementTree.tostring(self.xml, encoding='unicode', method='text')

    def project(self, target_spaced_line, character_alignment: List[Tuple[int, int]]):
        # Inserted characters arbitrarily go to the right, except for appended characters, which go to the left.
        subsequences: List[str] = []
        source_index = target_index = 0
        for alignment_index, alignment in enumerate(character_alignment):
            while source_index < alignment[0]:
                subsequences.append('')
                source_index += 1
            subsequences.append(target_spaced_line[target_index:(alignment[1] + 1)])
            source_index += 1
            target_index = alignment[1] + 1
        while source_index < len(self.get_characters()):
            subsequences.append('')
            source_index += 1
        subsequences[-1] += target_spaced_line[target_index:]

        def visit(node: Element, source_index: int):
            node_length: int = len(node.text)
            node.text = ''.join(subsequences[source_index:(source_index + node_length)])
            source_index += node_length
            for child in node:
                source_index = visit(child, source_index)
            if node.tail is not None:
                tail_length: int = len(node.tail)
                node.tail = ''.join(subsequences[source_index:(source_index + tail_length)])
                source_index += tail_length
            return source_index

        visit(self.xml, 0)
