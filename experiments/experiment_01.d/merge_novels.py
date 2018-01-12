#!/usr/bin/env python3

import itertools

import numpy as np
import pandas as pd


def merge_novels(data):
    groups = data.groupby(["file_id", "fold_size"])
    mean = groups.mean()
    ci = 1.96 * groups.std().div(groups.size().apply(np.sqrt), axis=0)
    mean = pd.DataFrame(mean.add_suffix("_mean").reset_index())
    mean.drop("year_mean", axis=1, inplace=True)
    ci = pd.DataFrame(ci.add_suffix("_ci").reset_index())
    ci.drop("year_ci", axis=1, inplace=True)
    ci.drop("file_id", axis=1, inplace=True)
    ci.drop("fold_size", axis=1, inplace=True)
    result = pd.concat([mean, ci], axis=1)
    columns = result.columns.tolist()
    columns = [columns[1]] + [columns[0]] + list(itertools.chain.from_iterable(zip(columns[2:int(len(columns) / 2) + 1], columns[int(len(columns) / 2) + 1:])))
    result = result[columns]
    result.insert(2, "author", [data[data['file_id'] == f]["author"].unique()[0] for f in result["file_id"]])
    result.insert(3, "title", [data[data['file_id'] == f]["title"].unique()[0] for f in result["file_id"]])
    result.insert(4, "year", [data[data['file_id'] == f]["year"].unique()[0] for f in result["file_id"]])
    return result


results_files = ("results_delta_de.tsv", "results_delta_de_no_punctuation.tsv", "results_delta_en.tsv", "results_delta_en_no_punctuation.tsv", "results_delta_fr.tsv", "results_delta_fr_no_punctuation.tsv", "results_gutenberg.tsv", "results_gutenberg_no_punctuation.tsv")
for rf in results_files:
    data = pd.read_csv(rf, sep="\t", header=0, index_col=0)
    per_novel = merge_novels(data)
    per_novel.to_csv("per_novel_" + rf, sep="\t")
