#!/usr/bin/env python3


def lexical_density(text, open_tags):
    """Proportion of content words."""
    n_content_words = len([t for t in text.tags if t in open_tags])
    return n_content_words / text.text_length


def rarity(text, reference_frequency_list, open_tags_ex_names):
    """Proportion of content words (excluding proper names) that are NOT
    in reference_frequency_list.

    """
    assert len(open_tags_ex_names) > 0, "You need to define proper names and open word classes in the language definition file"
    content_words = [t for t in zip(text.tokens, text.tags) if t[1] in open_tags_ex_names]
    rare = [t for t in content_words if t not in reference_frequency_list]
    return len(rare) / len(content_words)
