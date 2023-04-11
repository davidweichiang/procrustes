from typing import Callable, List, Tuple, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from utils.modes.alignment import Alignment


class XMLAlignment(Alignment):
    def __init__(self, source_line: str, **alignment_kwargs):
        super().__init__()
        self.xml: Element = ElementTree.fromstring(source_line)
        self.segmentation_function: Union[Callable, None] = alignment_kwargs["segmentation_function"]

    def __str__(self):
        if self.segmentation_function is not None:
            self.postprocess(self.xml)
        resulting_xml: str = ElementTree.tostring(self.xml, encoding='unicode', method='xml')
        return resulting_xml

    def get_characters(self):
        return ElementTree.tostring(self.xml, encoding='unicode', method='text')

    def project(self, revised_target_line: str, character_alignment: List[Tuple[int, int]]):
        # Inserted characters arbitrarily go to the right, except for appended characters, which go to the left.
        subsequences: List[str] = []
        source_index = target_index = 0
        for alignment_index, alignment in enumerate(character_alignment):
            while source_index < alignment[0]:
                subsequences.append('')
                source_index += 1
            subsequences.append(revised_target_line[target_index:(alignment[1] + 1)])
            source_index += 1
            target_index = alignment[1] + 1

        while source_index < len(self.get_characters()):
            subsequences.append('')
            source_index += 1

        subsequences[-1] += revised_target_line[target_index:]

        def visit(node: Element, source_text_index: int):
            node_length: int = len(node.text)
            node.text = ''.join(subsequences[source_text_index:(source_text_index + node_length)])
            source_text_index += node_length
            for child in node:
                source_text_index = visit(child, source_text_index)
            if node.tail is not None:
                tail_length: int = len(node.tail)
                node.tail = ''.join(subsequences[source_text_index:(source_text_index + tail_length)])
                source_text_index += tail_length
            return source_text_index

        visit(self.xml, 0)

    def postprocess(self, current_node: Element, nesting_depth: int = 1, subsequent_children: int = 0):
        start_tabs: str = "\t" * nesting_depth
        end_tabs: str = "\t" * (nesting_depth - 1)
        segmented_node_text: List[str] = self.segmentation_function(current_node.text)
        current_node.text = "".join([("\n" + start_tabs + segment) for segment in segmented_node_text])

        child_count: int = len(current_node)
        if child_count > 0:
            current_node.text += "\n" + start_tabs
            for current_child_count, child in enumerate(current_node, 1):
                self.postprocess(child, nesting_depth + 1, child_count - current_child_count)
        else:
            current_node.text += "\n" + end_tabs

        if current_node.tail is not None:
            if subsequent_children > 0:
                outside_tabs: str = end_tabs
            elif subsequent_children == 0:
                outside_tabs: str = "\t" * max(0, nesting_depth - 2)
            else:
                raise ValueError(f"The number of subsequent children, <{subsequent_children}>, is invalid.")

            segmented_tail_text: List[str] = self.segmentation_function(current_node.tail)
            current_node.tail = "".join([("\n" + end_tabs + segment) for segment in segmented_tail_text])
            current_node.tail += "\n" + outside_tabs
