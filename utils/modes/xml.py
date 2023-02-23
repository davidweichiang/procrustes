from typing import List
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

    def project(self, target_spaced_line, character_alignment):
        # Inserted characters arbitrarily go to the right, except for appended characters, which go to the left.
        subsequences: List[str] = []
        si = di = 0
        for alignment_index, alignment in enumerate(character_alignment):
            while si < alignment[0]:
                subsequences.append('')
                si += 1
            subsequences.append(target_spaced_line[di:(alignment[1] + 1)])
            si += 1
            di = alignment[1] + 1
        while si < len(self.get_characters()):
            subsequences.append('')
            si += 1
        subsequences[-1] += target_spaced_line[di:]

        def visit(node: Element, si):
            node_length: int = len(node.text)
            node.text = ''.join(subsequences[si:(si + node_length)])
            si += node_length
            for child in node:
                si = visit(child, si)
            if node.tail is not None:
                tail_length: int = len(node.tail)
                node.tail = ''.join(subsequences[si:(si + tail_length)])
                si += tail_length
            return si

        visit(self.xml, 0)
