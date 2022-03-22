# Linguistic and Stylistic Complexity

[![PyPI](https://img.shields.io/pypi/v/textcomplexity)](https://pypi.org/project/textcomplexity/)

This project implements various measures that assess the linguistic
and stylistic complexity of (literary) texts. There are
[surface-based](#surface-based-measures),
[sentence-based](#sentence-based-measures),
[pos-based](#pos-based-measures),
[dependency-based](#dependency-based-measures) and
[constituency-based](#constituency-based-measures) measures. Most of
the measures are language independent, but some of them rely on
language-specific information (see [language definition
files](#language-definition-files)) or are only defined for German
(this affects some of the constituency-based measures).

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

The **CoNLL-U format** consists of ten tab-separated columns that encode,
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
input should be in a **custom tab-separated format** with six
tab-separated columns and an empty line after each sentence. The six
columns are: word index, word, part-of-speech tag, index of dependency
head, dependency relation, phrase structure tree. Missing values can
be represented by an underscore (`_`). Here is a short example with
two sentences:

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

The script automatically includes measures that rely on
language-specific information, if you specify the input language. If
your texts are in German or English, you can use `--lang de` or
`--lang en`. If your texts are in another language, use `--lang other
--lang-def <file>` to provide a custom [language definition
file](#language-definition-files).

If you want to compute more (or fewer) measures, indicate one of the
predefined sets of measures (via `--preset`). You can choose to ignore
punctuation (`--ignore-punct`) or case (`--ignore-case`) and set the
window-size for the surface-based measures (`--window-size`). By
default, the script formats its output as JSON but you can also
request tab-separated values suitable for import in a spreadsheet
(`--output-format tsv`). More detailed usage information is available
via:

    txtcomplexity -h

### Utility script: From raw text to CONLL-U

Getting the input format right can sometimes be a bit tricky.
Therefore, we provide a simple wrapper script around
[stanza](https://stanfordnlp.github.io/stanza/), a state-of-the-art
NLP pipeline, which you can find in the `utils/` subdirectory of this
repository.

First, you need to install stanza:

    pip install stanza

Now you can use the wrapper script to parse your text files:

    run_stanza.py --language <language> --output-dir <directory> <file> …

## Complexity measures

### Core measures of lexical complexity

In our article on lexical complexity (currently in preparation) we
argue that there are several distinct aspects (or dimensions) of
lexical complexity and we propose a single measure for each of the
dimensions. Most of them are implemented here.

  - *Variability*: How large is the vocabulary? Measured via type-token ratio.
  - *Evenness*: How evenly are the tokens distributed among the
    different types? Measured via normalized entropy.
  - *Rarity*: How many rare words are used? Measured with the help of
    a reference frequency list.
      - General rarity: Rarity with respect to a representative sample
        of the language.
      - Genre rarity: Rarity with respect to a specific genre.
  - *Dispersion*: How evenly are the tokens of a type distributed
    throughout the text? Measured via Gini-based dispersion (without
    hapax legomena)
  - *Lexical density*: How many content words are used? Measured with
    the help of part-of-speech tags.
  - *Surprise*: How unexpected are word choices in the text? Not
    implemented here.
  - *Disparity*: How semantically dissimilar are the words? Not
    implemented here.

### Surface-based measures

#### Measures that use sample size and vocabulary size

  - Type-token ratio
  - Brunet's (1978) W
  - Carroll's (1964) CTTR
  - Dugast's (1978, 1979) U
  - Dugast's (1979) k
  - Guiraud's (1954) R
  - Herdan's (1960, 1964) C
  - Maas' (1972) a<sup>2</sup>
  - Summer's S
  - Tuldava's (1977) LN

All of these measures correlate perfectly.

<!-- Therefore, the default -->
<!-- setting is to only compute the type-token ratio. If you want to -->
<!-- compute all of these measures, use the option `--all-measures`. -->

#### Measures that use part of the frequency spectrum

  - Honoré's (1979) H
  - Michéa's (1969, 1971) M
  - Sichel's (1975) S

Michéa's M is the reciprocal of Sichel's S

<!-- , therefore we only -->
<!-- compute Sichel's S by default. If you want to compute Michéa's M as -->
<!-- well, use the option `--all-measures`. -->

#### Measures that use the whole frequency spectrum

  - Entropy (Shannon 1948)
  - Evenness (= [normalized entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)#Efficiency_(normalized_entropy)))
  - Herdan's (1955) V<sub>m</sub>
  - Jarvis' (2013) evenness (standard deviation of tokens per type)
  - McCarthy and Jarvis' (2010) HD-D
  - Simpson's (1949) D
  - Yule's (1944) K

Yule's K, Simpson's D and Herdan's V<sub>m</sub> correlate perfectly.
Simpson's D is perhaps the most intuitive of the three measures and
can be interpreted as the probability of two randomly drawn tokens
from the text being identical

<!-- Therefore, the default setting is to only compute Simpson's D (which -->
<!-- can be interpreted as the probability of two randomly drawn tokens -->
<!-- from the text being identical). If you also want to compute Yule's K -->
<!-- and Herdan's V<sub>m</sub>, use the option `--all-measures`. -->

#### Parameters of probabilistic models

  - Orlov's (1983) Z

#### Measures that use the whole text

  - Average token length
  - Covington and McFall's (2010) MATTR
  - Kubát and Milička's (2013) STTR
  - Log10 text length in characters
  - Log10 text length in tokens
  - MTLD (McCarthy and Jarvis 2010)

Measures of dispersion:
  - Evenness-based dispersion
  - Gini-based dispersion
  - Gries' DP and DP<sub>norm</sub> (Gries 2008, Lijffijt and Gries 2012)
  - Kullback-Leibler divergence (Kullback and Leibler 1951)

DP/DP<sub>norm</sub> and KL-divergence require an additional parameter
(the number of parts in which to split the text), therefore they are
not computed in the command-line script.

### Sentence-based measures

  - Sentence length in characters
  - Sentence length in tokens

Language-specific measures relying on a list of part-of-speech tags
that indicate punctuation, see [language definition
files](#language-definition-files):
  - Punctuation per sentence
  - Punctuation per token
  - Sentence length in words

### POS-based measures

  - Lexical density (Ure 1971)
  - Rarity (requires a reference frequency list)

These measures rely on language-specific information (lists of
part-of-speech tags that indicate open word classes and proper names
and lists of the most common word-tag pairs in a reference corpus),
see [language definition files](#language-definition-files).

### Dependency-based measures

  - Average dependency distance (Oya 2011)
  - Closeness centrality
  - Closeness centralization (Freeman 1978)
  - Dependents per token
  - Longest shortest path
  - Outdegree centralization (Freeman 1978)

### Constituency-based measures

Language-independent measures:
  - Constituents per sentence
  - Height of the parse trees
  - Non-terminal constituents per sentence

Language-dependent measures (defined for the German [NEGRA parsing
scheme](http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/knoten.html)):
  - Clauses per sentence
  - Complex t-units per sentence
  - Coordinate phrases per sentence
  - Dependent clauses per sentence
  - Noun phrases per sentence
  - Prepositional phrases per sentence
  - Verb phrases per sentence
  - t-units per sentence

## Language definition files

Some complexity measures (e.g. lexical density and rarity) require
language specific information that needs to be provided by *language
definition files*. For German and English, the built-in language
definition files will be used automatically (as long as you indicate
the language via the `--lang` option). For other languages (`--lang
other`), you need to provide the language definition files yourself.
Language definition files are in JSON format and contain the following
information:

  - `language`: Language code
  - `punctuation`: List of language-specific part-of-speech tags used
    for punctuation (column XPOS in CoNLL-U format)
  - `proper_names`: List of language-specific part-of-speech tags used
    for proper names
  - `open_classes`: List of language-specific part-of-speech tags used
    for open word classes (including proper names)
  - `most_common`: List of the most frequent content words (excluding
    proper names) and their part-of speech tags; for German and
    English, we use the 5.000 most frequent words according to the
    [COW frequency
    lists](https://www.webcorpora.org/opendata/frequencies/)

Here is an excerpt from the [German language definition
file](textcomplexity/de.json) (omitting most of the 5.000 most common
content words):

```json
{"language": "de",
 "punctuation": ["$.", "$,", "$("],
 "proper_names": ["NE"],
 "open_classes": ["ADJA", "ADJD", "ITJ", "NE", "NN", "TRUNC", "VVFIN", "VVIMP", "VVINF", "VVIZU", "VVPP"],
 "most_common": [["gibt", "VVFIN"],
                 ["gut", "ADJD"],
                 ["Zeit", "NN"],
                 …
                 ["Fahrzeugen", "NN"],
                 ["Kopie", "NN"],
                 ["Merkmale", "NN"]
                ]
}
```

Here is an excerpt from the [English language definition
file](textcomplexity/en.json) (omitting most of the 5.000 most common
content words). Note that the part-of-speech tags for punctuation look
like punctuation symbols – but we list pos tags, not punctuation
symbols:

```json
{"language": "en",
 "punctuation": [".", "," ,":", "\"", "``", "(", ")", "-LRB-", "-RRB-"],
 "proper_names": ["NNP", "NNPS"],
 "open_classes": ["AFX", "JJ", "JJR", "JJS", "NN", "NNS", "RB", "RBR", "RBS", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"],
 "most_common": [["is", "VBZ"],
                 ["be", "VB"],
                 ["was", "VBD"],
                 …
                 ["statistical", "JJ"],
                 ["appearing", "VBG"],
                 ["recipes", "NNS"]
                ]
}
```
