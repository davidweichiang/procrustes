# Procrustes

**Note: the below, due to refactoring the interface, is outdated to some extent. 
It will be rewritten once changes are complete.**

Procrustes is a simple script for projecting annotations of various
kinds from one text to another highly similar text (e.g., with
different tokenization or differences in punctuation or encoding of
punctuation). (It was named long before the word embedding alignment
method!)

Usage:

    procrustes.py -m <mode> forcefile < infile

It currently has three modes. In all modes, `forcefile` is the text
with the target tokenization, and `infile` and `forcefile` must have
the same number of lines.

- In tree mode (default or `-m tree`), `infile` should contain
  Treebank-style trees, one per line. Not implemented. (It must have
  been implemented in a previous version, now lost.)

- In XML mode (`-m xml`), `infile` should be in XML.
  
- In alignment mode (`-m align`) should have the format

      τοὺς πόδας προέκρουεν \t he stretched their legs \t 0-2 1-3 2-0 2-1

  where the words are numbered starting from 0. By default the source
  (here, Greek) side is the one that will be forced to match the
  `forcefile`; the `--english` flag changes the target (here, English)
  side instead.
