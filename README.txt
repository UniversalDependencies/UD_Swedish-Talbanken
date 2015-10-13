UD_SWEDISH

The Swedish UD treebank is based on the Professional Prose section of 
Talbanken (Einarsson, 1976), originally annotated by a team led by Ulf Teleman
at Lund University according to the MAMBA annotation scheme (Teleman, 1974). 
It consists of roughly 6,000 sentences and 95,000 tokens taken from a variety
of genres, including text books, information brochures, and newspaper 
articles. The syntactic annotation is converted directly from the original 
MAMBA annotation, while the morphological annotation is based on the 
reannotation performed when incorporating Talbanken into the Swedish Treebank 
(Nivre and Megyesi, 2007). The new conversion has been performed by Joakim 
Nivre and Aaron Smith at Uppsala University. We thank everyone who has been 
involved in previous conversion efforts at Växjö University and Uppsala 
University, including Bengt Dahlqvist, Sofia Gustafson-Capkova, Johan Hall, 
Anna Sågvall Hein, Beáta Megyesi, Jens Nilsson, and Filip Salomonsson. Special 
thanks also to Lars Borin and Markus Forsberg at Språkbanken for help with the
lemmatization.

DATA SPLITS

The test set (sv-ud-test.conllu) is the standard test set from the Swedish 
Treebank, which is a balanced sample of complete documents from different 
parts of the treebank.

The rest of the treebank has been split by taking the first 90% as the 
training set (sv-ud-train.conllu) and the last 10% as the development set
(sv-ud-dev.conllu). 

BASIC STATISTICS

Tree count:  6026
Word count:  96819
Token count: 96819
Dep. relations: 39 of which 4 language specific
POS tags: 15
Category=value feature pairs: 27

TOKENIZATION

The tokenization in the Swedish UD treebank follows the principles of the 
Stockholm-Umeå Corpus, Version 2.0 (SUC, 2006), which has become the de facto 
standard for Swedish tokenization and part-of-speech tagging. This is a 
straightforward segmentation based on whitespace and punctuation, but the 
following special cases deserve to be mentioned:

- Abbreviations are treated as single words regardless of whether they contain 
  spaces or not (and internal spaces are replaced by underscore characters).
- Numerical expressions including dates are treated as single words and not 
  segmented into their components.

The Swedish UD treebank does not contain multiword tokens.

MORPHOLOGY

The morphological annotation in the Swedish UD treebank follows the general 
guidelines and does not add any language-specific features. The 
language-specific tags (including features) follow the guidelines of the 
Stockholm-Umeå Corpus.

The mapping from language-specific tags and features to universal tags and 
features was done automatically. We are not aware of any remaining errors or 
inconsistences but the mapping has not been validated manually.

Lemmas were assigned using SALDO (Borin et al., 2008) in combination with 
the language-specific SUC tags. Cases of remaining ambiguity were resolved 
heuristically, which may have introduced errors. For words and symbols not 
covered by SALDO, lemmas were added manually.

SYNTAX

The syntactic annotation in the Swedish UD treebank follows the general 
guidelines but adds four language-specific relations:

- acl:relcl for relative clauses
- compound:prt for verb particles
- nmod:agent for agents of passive verbs
- nmod:poss for possessive/genitive modifiers

The syntactic annotation has been automatically converted from the original 
MAMBA annotation scheme in Talbanken. The following phenomena are known to 
deviate from the general guidelines and will be fixed in future versions:

- The remnant analysis of ellipsis has not been fully implemented.
- Complex names with compositional internal structure are annotated in the 
  same way as non-compositional cases.
- Comparative modifiers are sometimes not attached to the comparative element 
  itself but to its head.

REFERENCES

* Lars Borin, Markus Forsberg, Lennart Lönngren. 2008. Saldo 1.0 (Svenskt 
  associationslexikon version 2). Språkbanken, Göteborg universitet.

* Einarsson, Jan. 1976. Talbankens skriftspråkskonkordans. Lund University: 
  Department of Scandinavian Languages.

* Joakim Nivre and Beáta Megyesi. 2007. Bootstrapping a Swedish treeebank 
  using cross-corpus harmonization and annotation projection. In Proceedings 
  of the 6th International Workshop on Treebanks and Linguistic Theories, 
  pages 97-102.

* Teleman, Ulf. 1974. Manual för grammatisk beskrivning av talad och skriven 
  svenska. Studentlitteratur.

* The Stockholm Umeå Corpus. Version 2.0. 2006. Stockholm University: 
  Department of Linguistics.




Documentation status: complete
Data source: automatic conversion + manual check
Data available since: UD v1.0
License: CC BY-SA 4.0
