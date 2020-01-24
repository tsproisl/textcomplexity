# N-gram language models with KenLM

[KenLM](https://kheafield.com/code/kenlm/) is an open source language
modelling toolkit.


## Word n-gram models

  1. Reformat the training corpus: One sentence per line, tokens
     separated by spaces.
  2. Train a language model:
```sh
zcat /path/to/corpus.txt.gz | bin/lmplz -o3 -S 24G -T /path/to/tmp/ > /path/to/language_model.arpa
```
  3. Build a binary file (this needs a lot of memory):
    ```sh
bin/build_binary /path/to/language_model.arpa /path/to/language_model.binary
    ```
  4. Reformat the input file(s): One sentence per line, tokens
     separated by spaces.
  5. Query the model:
    ```sh
cat /path/to/input.txt | bin/query -v word /path/to/language_model.binary > /path/to/output.txt
    ```

## Character n-gram models

  1. Reformat the training corpus: One sentence per line, characters
     separated by spaces, words separated by " </w> ".
  2. Train a language model (10-grams):
    ```sh
zcat /path/to/corpus.txt.gz | bin/lmplz -o10 -S 24G -T /path/to/tmp/ > /path/to/language_model.arpa
    ```
  3. Build a binary file (this needs a lot of memory):
    ```sh
bin/build_binary /path/to/language_model.arpa /path/to/language_model.binary
    ```
  4. Reformat the input file(s): One sentence per line, characters
     separated by spaces, tokens separated by " </w> ".
  5. Query the model:
    ```sh
cat /path/to/input.txt | bin/query -v word /path/to/language_model.binary > /path/to/output.txt
    ```

## Analysis

Assuming the detailed output files (created with `-v word`) are in
directory `/path/to/perplexities/`:
```sh
./analyze_detailed_complexity.py -o trigram_perplexity /path/to/perplexities/
```

Creates files `trigram_perplexity_file_dist.tsv.gz`,
`trigram_perplexity_sentence_dist.tsv.gz` and
`trigram_perplexity_token_dist.tsv.gz`.
