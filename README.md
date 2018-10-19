# Summary

The Swedish-Talbanken treebank is based on Talbanken, a treebank developed at Lund University
in the 1970s.

# Introduction

The Swedish-Talbanken treebank is a conversion of the Prose section of Talbanken (Einarsson,
1976), originally annotated by a team led by Ulf Teleman at Lund University according
to the MAMBA annotation scheme (Teleman, 1974). It consists of roughly 6,000 sentences
and 95,000 tokens taken from a variety of informative text genres, including textbooks,
information brochures, and newspaper articles. The syntactic annotation is converted
directly from the original MAMBA annotation, while the morphological annotation is
based on the reannotation performed when incorporating Talbanken into the Swedish
Treebank (Nivre and Megyesi, 2007). Tokenization mostly follows the standard of the
Stockholm-Umeå Corpus, Version 2.0 (2006), and lemmatization is based on Saldo
(Borin et al., 2008).

# Acknowledgments

The new conversion has been performed by Joakim Nivre and Aaron Smith at Uppsala
University. We thank everyone who has been involved in previous conversion efforts
at Växjö University and Uppsala University, including Bengt Dahlqvist, Sofia
Gustafson-Capkova, Johan Hall, Anna Sågvall Hein, Beáta Megyesi, Jens Nilsson, and
Filip Salomonsson. Special thanks also to Lars Borin and Markus Forsberg at
Språkbanken for help with the lemmatization. Finally, we owe a huge debt to the
team who produced the original treebank in the 1970s.

## References

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

# Data Splits

The test set (sv-ud-test.conllu) is the standard test set from the Swedish
Treebank, which is a balanced sample of complete documents from different
parts of the treebank.

The rest of the treebank has been split by taking the first 90% as the
training set (sv-ud-train.conllu) and the last 10% as the development set
(sv-ud-dev.conllu).

Document and paragraph boundaries are explicitly represented by comment
lines (# newdoc id = DOC_ID, # newpar id = PAR_ID), but genre classification
is not available for documents.

# Tokenization

The tokenization in the Swedish-Talbanken treebank follows the principles of the
Stockholm-Umeå Corpus, Version 2.0 (SUC, 2006), which has become the de facto
standard for Swedish tokenization and part-of-speech tagging. This is a
straightforward segmentation based on whitespace and punctuation, but the
following special cases deserve to be mentioned:

- Numerical expressions (including dates) are treated as single words and not
  segmented into their components as long as they do not contain spaces.
- Abbreviations are treated as single words regardless of whether they contain
  spaces or not.

The Swedish-Talbanken treebank contains the following tokens with spaces (all abbreviations):

Bl a
bl a
d v s
e d
f n
fr o m
Fr o m
m fl
m m
o s v
s k
t ex
t o m
t v

The Swedish-Talbanken treebank does not contain multiword tokens.

# Morphology

The morphological annotation in the Swedish-Talbanken treebank follows the general
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

# Syntax

The syntactic annotation in the Swedish-Talbanken treebank follows the general
guidelines but adds four language-specific relations:

- acl:relcl for relative clauses
- compound:prt for verb particles
- nmod:agent for agents of passive verbs
- nmod:poss for possessive/genitive modifiers

The syntactic annotation has been automatically converted from the original
MAMBA annotation scheme in Talbanken. The following phenomena are known to
deviate from the general guidelines and will be fixed in future versions:

- The remnant analysis of ellipsis has not been fully implemented.
- Comparative modifiers are sometimes not attached to the comparative element
  itself but to its head.

# Changelog

From v1 to v1.1, an extensive (but not complete) manual validation was
carried out, resulting in a large number of conversion errors being
corrected. Specifically, all non-projective trees were validated.

From v1.1 to v1.2, complex names and multiword expressions have been
manually validated. As a result, the annotation of complex names now
conforms to the universal guidelines.

From v1.2 to v1.3, we fixed the following annotation bugs/inconsistencies:
- All conj relations are now left-headed
- No mark relations are filled by PRON
- All punct relations are filled by PUNCT (and vice versa)
- All cop relations are filled by VERB (not AUX)
- All DET and PRON have a PronType feature
- All AUX and VERB have a VerbType feature
- All NUM have a NumType features
- No predicate has more than one subject (except expl + nsubj/csubj)
- No case relations attach to predicates

From v1.3 to v1.4, only the documentation has been updated to reflect
the fact that there are two treebanks for Swedish.

From v1.4 to v2.0, we have implemented the following changes to conform
to v2 of the guidelines:
- Rename CONJ -> CCONJ
- Retag copula verbs VERB -> AUX
- Rename dobj -> obj
- Rename nsubjpass -> nsubj:pass
- Rename csubjpass -> csubj:pass
- Rename auxpass -> aux:pass
- Rename mwe -> fixed
- Rename name -> flat:name
- Split nmod into obl and nmod
- Reattach cc and punct in coordination
- Reanalyze neg as advmod + Polarity=Neg
- Add features Abbr=Yes and Foreign=Yes
- Replace "_" by " " in words with spaces
- Add # sent_id and # text for all sentences

From v2.0 to v2.1, no changes have been made.

From v2.1 to v2.2:
- Repository renamed from UD_Swedish to UD_Swedish-Talbanken.
- Harmonization with other Swedish treebanks:
  - Possessives retagged DET -> PRON
  - Negations ("inte", "icke", "ej") retagged ADV -> PART
  - Comparative markers ("som", "än") retagged CCONJ -> SCONJ
  - Comparative with nominal complement relabeled advcl -> obl [mark -> case, SCONJ -> ADP]
  - Clefts reanalyzed as copula constructions and relabeled acl:relcl -> acl:cleft
  - Temporal subordinating conjunctions ("när", "då") retagged ADV -> SCONJ and relabeled advmod -> mark
- Fixed a small number of annotation errors
- Added enhanced dependencies

From v2.2 to v2.3:
- Fixed a small number of errors in both basic and enhanced dependencies
<pre>
=== Machine readable metadata ==============

Data available since: UD v1.0
License: CC BY-SA 4.0
Includes text: yes
Genre: news nonfiction
Lemmas: automatic with corrections
UPOS: converted with corrections
XPOS: manual native
Features: converted with corrections
Relations: converted with corrections
Contributors: Nivre, Joakim; Smith, Aaron
Contributing: elsewhere
Contact: joakim.nivre@lingfil.uu.se

============================================
</pre>
