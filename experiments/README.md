# Experiments #

This file is here to give a brief overview of the experiments. Do not
expect the experiment scripts to run on your machine. They are likely
to contain hard-coded paths and the like.

## Experiment 1 ##

We use the `vocabulary_richness.bootstrap` function to look at how
stable the performance of the measures is when we change the window
size aka fold size.

Data: German novels with at least 10,000 tokens written by native
speakers between 1789 and 1914; Delta corpora in German, English and
French.

### Observations ###

Observations hold true for all corpora, numbers are taken from the German Delta corpus

#### Properties of measures ####

  * Brunet's W: uses sample size and vocabulary size; value increases with fold size; ranking is stable (ρ ≥ 0.92)
  * Carroll's CTTR: uses sample size and vocabulary size; value increases with fold size; ranking is stable (ρ ≥ 0.92)
  * Dugast's U: uses sample size and vocabulary size; value is stable; ranking is stable (ρ ≥ 0.92)
  * Dugast's k: uses sample size and vocabulary size; value increases with fold size; ranking is stable (ρ ≥ 0.92)
  * Entropy: uses the whole frequency spectrum; value increases with fold size; ranking is stable (ρ ≥ 0.94)
  * Guiraud's R: uses sample size and vocabulary size; value increases with fold size; ranking is stable (ρ ≥ 0.92)
  * Herdan's C: uses sample size and vocabulary size; value decreases with fold size; ranking is stable (ρ ≥ 0.92)
  * Herdan's V<sub>m</sub>: uses the whole frequency spectrum; value is stable; ranking is very stable (ρ ≈ 1.00)
  * Honoré's H: uses part of the frequency spectrum; value is almost stable (noticeable increase at the beginning); ranking stable for larger fold sizes, less so for the greates differences (ρ ≥ 0.84)
  * MTLD: uses the whole text; value is stable; ranking is very stable (ρ ≥ 0.99)
  * Maas' a<sup>2</sup>: uses sample size and vocabulary size; value is stable; ranking is stable (ρ ≥ 0.92)
  * McCarthy and Jarvis' HD-D: uses the whole frequency spectrum; value decreases with fold size; ranking is only stable for similar fold sizes, otherwise completely different (ρ ≥ 0.16)
  * Michéa's M: uses part of the frequency spectrum; value decreases with fold size; ranking is only stable for similar fold sizes (ρ ≥ 0.70)
  * Sichel's S: uses part of the frequency spectrum; value increases with fold size; ranking is only stable for similar fold sizes (ρ ≥ 0.70)
  * Simpson's D: uses the whole frequency spectrum; value is stable; ranking is very stable (ρ ≥ 0.99)
  * Summer's S: uses sample size and vocabulary size; value decreases with fold size; ranking is stable (ρ ≥ 0.92)
  * Tuldava's LN: uses sample size and vocabulary size; value increases with fold size (much more than differences between individual texts); ranking is stable (ρ ≥ 0.92)
  * Type-token ratio: uses sample size and vocabulary size; value decreases with fold size; ranking is stable (ρ ≥ 0.92)
  * Yule's K: uses the whole frequency spectrum; value is stable; ranking is very stable (ρ ≥ 0.99)

#### Correlations between measures ####

  * Group 1: Herdan's V<sub>m</sub>, Simpson's D and Yule's K correlate perfectly
  * Group 2: Maas' a<sup>2</sup> and Tuldava's LN correlate perfectly
  * Group 3: Brunet's W, Carroll's CTTR, Dugast's U, Dugast's k, Guiraud's R, Herdan's C, Summer's S and Type-token ratio correlate perfectly
  * Group 2 and group 3 have a perfect negative correlation, i.e. all measures that use sample size and vocabulary size show perfect (negative) correlation
  * Entropy and Honoré's H correlate strongly with group 3 (ρ = 0.92 and 0.94) but less so with each other (ρ = 0.81)
  * Michea's M and Sichel's have a perfect negative correlation and correlate strongly with Honoré's H (ρ = ±0.92) and somewhat with group 2 or 3 (ρ = 0.82)
  * MTLD is its own group (all ρ < 0.8); most similar to entropy (ρ = 0.78)
  * McCarthy and Jarvis' HD-D is its own group (all ρ < 0.8)

## Experiment 2 ##

Dependency-based measures of syntactic complexity and their
correlations.

## Experiment 3 ##

Sentence-level distributions of dependency-based measures of syntactic
complexity.

## Experiment 4 ##

Distributions of (classes of) part-of-speech tags.
