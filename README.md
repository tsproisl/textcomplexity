# Linguistic and Stylistic Complexity #

This project is a collection of measures that assess the linguistic
and stylistic complexity of (literary) texts.

## Usage ##

You can use the script `bin/lascomplexity.py` to compute all
implemented complexity measures from the command line. The
vocabulary-based and dependency-based complexity measures are language
independent, the constituent-based measures rely on the NEGRA parsing
scheme, i.e. can only be applied to German data.

The input has to be a CoNLL-style text file with six tab-separated
columns and an empty line after each sentence. The six columns are:
word index, word, part-of-speech tag, index of dependency head,
dependency relation, phrase structure tree. Missing values can be
represented by an underscore (`_`). Here is a short example with two
sentences:

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

Without any options, the script computes all measures:

    lascomplexity.py <file>

You can also request subsets of the measures via the `-v`/`--voc`,
`-d`/`--dep` and `-c`/`--const` options for vocabulary-based,
dependency-based and constituent-based measures. More detailed usage
information is available via:

    lascomplexity.py -h

## Vocabulary-based complexity measures ##

### Measures that use sample size and vocabulary size ###

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

### Measures that use part of the frequency spectrum ###

  * Honoré's H
  * Sichel's S
  * Michéa's M

### Measures that use the whole frequency spectrum ###

  * Entropy
  * Yule's K
  * Simpson's D
  * Herdan's V<sub>m</sub>
  * McCarthy and Jarvis' HD-D

### Parameters of probabilistic models ###

  * Orlov's Z

### Measures that use the whole text ###

  * Covington and McFall's MATTR
  * MTLD
  * Kubat and Milicka's STTR

## Shallow syntactic complexity measures ##

  * Average sentence length
  * Average punctuation per sentence
  * Average punctuation per token

### Dependency-based measures

  * Average dependency distance
  * Average closeness centrality
  * Average outdegree centralization
  * Average closeness centralization
  * Average longest shortest path
  * Average dependents per token

### Constituent-based measures

Language-independent measures:
  * Average number of constituents
  * Average number of constituents without leaves
  * Average height of the parse trees

Language-dependent measures (defined for German):
  * Average number of t units
  * Average number of complex t units
  * Average number of clauses
  * Average number of dependent clauses
  * Average number of NPs
  * Average number of VPs
  * Average number of PPs
  * Average number of coordinate phrases
