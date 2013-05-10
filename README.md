PPE
===

Phrase Pair Extraction

By Michael Cabot and Sander Nugteren

ppe.py
===

Extracts phrase pairs.

Command line arguments:

- -a (--alignments) File containing the alignments
- -l1 (--language1) File containing the sentences of language 1
- -l2 (--language2) File containing the sentences of language 2
- -o (--output File) name for output. Contains the phrase pair (l1,l2) their joint probability P(l1, l2) and conditional probabilities P(l1 | l2) and P(l2 | l1)
- -m (--max_length) Maximum length of phrase pairs (0 <= m)


ppc.py
===

Calculates phrase pair coverage.

Command line arguments:

- -t (--trainfile) File containing phrase table from the training set
- -v (--heldoutfile) File containing phrase table from the test set
- -m (--max_concat) Comma separated values denoting the maximum number of concatenations to cover a phrase pair. Each number must be greater or equal to 0. E.g -m 0,1,2

Assignment 4
===

The folder 'model' can be found on the 'deze' server at: /home/6047262/model/