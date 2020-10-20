# Linguistic and Stylistic Complexity

[![PyPI](https://img.shields.io/pypi/v/textcomplexity)](https://pypi.org/project/textcomplexity/)

This project implements various measures that assess the linguistic
and stylistic complexity of (literary) texts. All surface-based,
sentence-based and dependency-based complexity measures are language
independent. Some of the constituency-based measures are also language
independent, but most rely on the [NEGRA parsing
scheme](http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/knoten.html),
i.e. can only be applied to German data.

## Installation

The easiest way to install the toolbox is via pip (pip3 in some
distributions):

    pip install textcomplexity

Alternatively, you can download and decompress the [latest
release](https://github.com/tsproisl/textcomplexity/releases/latest)
or clone the git repository:

    git clone https://github.com/tsproisl/textcomplexity.git

In the new directory, run the following command:

    python3 setup.py install


## Usage

You can use the script `bin/txtcomplexity` to compute (a sensible
subset of) all implemented complexity measures from the command line.
The script currently supports two input formats: The widely used
[CoNLL-U format](https://universaldependencies.org/format.html)
(`--input-format conllu`) and a custom tab-separated input format
(`--input-format tsv`).

The CoNLL-U format consists of ten tab-separated columns that encode,
among other things, the dependency structure of the sentence. Missing
values can be represented by an underscore (`_`). Here is an example:

    # sent_id = hdt-s469
    # text = Netscape hatte den Browser-Markt noch 1994 zu fast 90 Prozent beherrscht .
    1	Netscape	Netscape	PROPN	NE	_	11	nsubj	_	_
    2	hatte	haben	AUX	VAFIN	_	11	aux	_	_
    3	den	den	DET	ART	_	4	det	_	_
    4	Browser-Markt	Markt	NOUN	NN	_	11	obj	_	_
    5	noch	noch	ADV	ADV	_	6	advmod	_	_
    6	1994	1994	NUM	CARD	_	11	obl	_	_
    7	zu	zu	ADP	APPR	_	10	case	_	_
    8	fast	fast	ADV	ADV	_	9	advmod	_	_
    9	90	90	NUM	CARD	_	10	nummod	_	_
    10	Prozent Prozent NOUN	NN	_	11	obl	_	_
    11	beherrscht	beherrschen	VERB	VVPP	_	0	root	_	_
    12	.	.	PUNCT	$.	_	11	punct	_	_

If you want to compute the constituency-based complexity measures, the
input should be CoNLL-style text files with six tab-separated columns
and an empty line after each sentence. The six columns are: word
index, word, part-of-speech tag, index of dependency head, dependency
relation, phrase structure tree. Missing values can be represented by
an underscore (`_`). Here is a short example with two sentences:

    1	Das	ART	3	NK	(TOP(S(NP*
    2	fremde	ADJA	3	NK	*
    3	Schiff	NN	4	SB	*)
    4	war	VAFIN	-1	--	*
    5	nicht	PTKNEG	6	NG	(AVP*
    6	allein	ADV	4	MO	*)
    7	.	$.	6	--	*))
    
    1	Sieben	CARD	2	NK	(TOP(S(NP*
    2	weitere	ADJA	3	MO	*)
    3	begleiteten	VVFIN	-1	--	*
    4	es	PPER	3	OA	*
    5	.	$.	4	--	*))

Without any further options, the script computes a sensible subset of
all applicable measures (see below):

    txtcomplexity --input-format conllu <file>

If you want to compute all applicable measures (including measures
that are perfectly correlated with other measures), you can use the
option `--all-measures`. You can also request specific subsets of the
measures via the `--sur`, `--sent` `--dep` and `--const` options for
surface-based, sentence-based, dependency-based and constituent-based
measures. By default, the script formats its output as JSON but you
can also request tab-separated values suitable for import in a
spreadsheet (`--output-format tsv`). More detailed usage information
is available via:

    txtcomplexity -h

### Utility scripts: From raw text to CONLL-U

Getting the input format right can sometimes be a bit tricky.
Therefore, we provide simple wrapper scripts around two
state-of-the-art NLP pipelines,
[stanza](https://stanfordnlp.github.io/stanza/) and
[spaCy](https://spacy.io/). You can find the scripts in the `utils/`
subdirectory of this repository.

#### stanza

First, you need to install stanza:

    pip install stanza

Now you can use the wrapper script to parse your text files:

    run_stanza.py --language <language> --output-dir <directory> <file> …

#### spaCy

First, you need to install spaCy:

    pip install -U spacy spacy-lookups-data

Now you can use the wrapper script to parse your text files:

    run_stanza.py --language <language> --output-dir <directory> <file> …

## Complexity measures

### Surface-based complexity measures

#### Measures that use sample size and vocabulary size

  * Type-token ratio
  * Guiraud's R
  * Herdan's C
  * Dugast's k
  * Maas' a<sup>2</sup>
  * Dugast's U
  * Tuldava's LN
  * Brunet's W
  * Carroll's CTTR
  * Summer's S

All of these measures correlate perfectly. Therefore, the default
setting is to only compute the type-token ratio. If you want to
compute all of these measures, use the option `--all-measures`.

#### Measures that use part of the frequency spectrum

  * Sichel's S
  * Michéa's M
  * Honoré's H

Michéa's M is simply the reciprocal of Sichel's S, therefore we only
compute Sichel's S by default. If you want to compute Michéa's M as
well, use the option `--all-measures`.

#### Measures that use the whole frequency spectrum

  * Entropy
  * Evenness
  * Yule's K
  * Simpson's D
  * Herdan's V<sub>m</sub>
  * McCarthy and Jarvis' HD-D

Yule's K, Simpson's D and Herdan's V<sub>m</sub> correlate perfectly.
Therefore, the default setting is to only compute Simpson's D (which
can be interpreted as the probability of two randomly drawn tokens
from the text being identical). If you also want to compute Yule's K
and Herdan's V<sub>m</sub>, use the option `--all-measures`.

#### Parameters of probabilistic models

  * Orlov's Z

#### Measures that use the whole text

  * Covington and McFall's MATTR
  * MTLD
  * Kubat and Milicka's STTR
  * Average token length
  * Gries' DP and DP<sub>norm</sub>
  * Kullback-Leibler divergence

DP/DP<sub>norm</sub> and KL-divergence are measures of dispersion. As
they require an additional parameter (the number of parts in which to
split the text), they are not computed in the command-line script.

### Sentence-based complexity measures

  * Sentence length in words and characters
  * Punctuation per sentence
  * Punctuation per token

### Dependency-based measures

  * Average dependency distance
  * Closeness centrality
  * Outdegree centralization
  * Closeness centralization
  * Longest shortest path
  * Dependents per token

### Constituency-based measures

Language-independent measures:
  * Constituents per sentence
  * Non-terminal constituents per sentence
  * Height of the parse trees

Language-dependent measures (defined for German):
  * t-units per sentence
  * Complex t-units per sentence
  * Clauses per sentence
  * Dependent clauses per sentence
  * Noun phrases per sentence
  * Verb phrases per sentence
  * Prepositional phrases per sentence
  * Coordinate phrases per sentence
