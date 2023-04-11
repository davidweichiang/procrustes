from enum import Enum


class HelpMessage(Enum):
    # Required Arguments
    SOURCE = "the filepath of the the source of alignment--where the tagged data is already present"
    TARGET = "the filepath of the target of alignment--where tagged data is lacking"

    # Optional Arguments
    COST_FUNCTION = "indicates the cost function that procrustes will use for alignment"
    FLIP = "if true, operates on target side instead of source"
    MODE = "designates the format that the source and target should take"
    OUTPUT = "indicates the filepath where the output (or outputs) of the alignment process should be stored"
    PROCESSES = "determines the number of processes that will be used in alignment; " \
                "currently only applicable to multi-file, independent alignments"
    SEGMENTER = "selects how text will be divided up in the output postprocessing"
    VERBOSE = "if true, outputs intermediate results of alignment to stderr"
    ZIPPER = "chooses what objects (e.g., lines, files) will be paired and how pairing will occur"
