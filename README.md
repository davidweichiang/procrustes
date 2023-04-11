# Procrustes (Gk. Προκρούστης)

Procrustes is a script for projecting annotations of various
kinds from one text to another highly similar text (*e.g.*, with
different tokenization or differences in punctuation or encoding of
punctuation). (It was named long before the [word embedding alignment](https://arxiv.org/pdf/1805.11222.pdf)
method!)

## Usage

    procrustes.py [-h] [--cost-function COST_FUNCTION] [--flip] [--mode MODE] [--output OUTPUT] [--processes PROCESSES] [--segmenter SEGMENTER] [--verbose] [--zipper ZIPPER] source target

By default, Procrustes requires two arguments. 
Those options are the `source` and `target` for alignment. 
Each of these should be a filepath.
The `source` file should contain the labeled data, 
whereas the `target` file should contain the unlabeled data.
Currently, Procrustes only accepts either two files (where the two files are aligned) 
or two directories (where complete files are aligned). In either case,
Procrustes requires that `source` and `target` files have the same number of lines. 
This requirement can be fulfilled without manual reformatting 
if an appropriate `--zipper` function is used to preprocess the data. 

In terms of optional arguments: 
  - the `--cost-function` option allows for an alignment function to be selected. 
  Alignments are done on the basis of edit distance, although different cost functions can be defined to produce results which fit better 
  with the differences displayed by variations on the same data. The default is the `procrustes-levenshtein` cost function.
  - the `--flip` flag allows `source` and `target` to be reversed. 
However, this is currently only implemented for the word-level alignment mode.
  - the `--mode` option allows for one to select the type of alignment that should occur, dictating the expected label format. (See below for more details.)
  - the `--output` option allows for a filepath to be supplied such that the result of the alignment (*i.e.*, the target data with the source labels applied to it) is written to a file (or files).
  - the `--processes` option allows for the number of processes desired to be specified, permitting multiprocessing. It is only used when independent files are being aligned.
  - the `--segmenter` option determines how the alignment output will be split up and formatted as a postprocessing step. This currently is only used for the XML alignment model.
  - the `--verbose` option prints out intermediate alignment results (*e.g.*, individual lines for alignment across a single file).
  - the `--zipper` option determines how the supplied data from `source` and `target` will be compared; can be done line-by-line or in aggregate (*e.g.*, alignment on the level of the whole file).

### Modes

Procrustes contains three modes of alignment.
Below, we list those modes and describe the expected formats for each of them.

- In Tree mode (default or `--mode tree`), `source` should contain Treebank-style trees, one per line. Not implemented. (It had been implemented in a previous version, but it was lost.)

- In XML mode (`--mode xml`), `source` should be in XML.
  
- In Word mode (`--mode word`), `source` should have the format:

      τοὺς πόδας προέκρουεν \t he stretched their legs \t 0-2 1-3 2-0 2-1

  where the words are numbered starting from 0. By default, the source
  (here, Greek) side is the one that will be forced to match the
  `target`; as mentioned above, the `--flip` flag changes the target (here, English) side instead.
