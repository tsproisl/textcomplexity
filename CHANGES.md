# CHANGELOG

## Version 0.10.0, 2021-12-13

  - Add dispersion measures (Gini-based dispersion and evenness-based
    dispersion).
  - Add pos-based measures (lexical density, rarity).
  - Add Jarvis's (2013) evenness (standard deviation of tokens per
    type).
  - Language-specific information can be provided via language
    definition files (`--lang-def`); already built-in for German and
    English (simply specify `--lang de` or `--lang en`).
  - New presets of measures (lexical\_core, core, extended\_core, all);
    ignore measures that are not applicable.
  - New option `--ignore-case`.
  - Update documentation.
  - Improve warning about window size.

## Version 0.9.1, 2021-07-15

  - Bugfix: Use 0.172 instead of -0.172 as default value for alpha in
    Brunet’s W.
  - Bugfix in code for reading custom tsv format.

## Version 0.9.0, 2020-10-20

  - Initial release.
