#!/usr/bin/env python3

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import seaborn as sns


def plot_distributions(results, measures, fold_sizes, directory):
    for measure in measures:
        fig, ax = plt.subplots(figsize=(12, 8))
        # ax.set_title(measure)
        ax.set_xlabel("fold size")
        ax.set_ylabel(measure[:-5])
        x = np.array(fold_sizes)
        y = np.array([results[results["fold_size"] == fold_size][measure] for fold_size in fold_sizes])
        ax.boxplot(y.T)
        plt.xticks(range(1, 11), x)
        plt.savefig(os.path.join(directory, "fold_size_%s.pdf" % (measure[:-5],)), format="pdf")


def correlations_between_measures(results, measures, fold_sizes, spearman=False):
    correlations = np.zeros((len(measures), len(measures)))
    for i, measure1 in enumerate(measures):
        values1 = np.array([results[results["fold_size"] == fold_size][measure1] for fold_size in fold_sizes])
        for j, measure2 in enumerate(measures):
            values2 = np.array([results[results["fold_size"] == fold_size][measure2] for fold_size in fold_sizes])
            if spearman:
                corrs = np.array([scipy.stats.spearmanr(values1[i], values2[i])[0] for i in range(10)])
            else:
                corrs = np.array([scipy.stats.pearsonr(values1[i], values2[i])[0] for i in range(10)])
            mean, std = corrs.mean(), corrs.std()
            correlations[i, j] = mean
    correlations = pd.DataFrame(correlations, index=[m[:-5] for m in measures], columns=[m[:-5] for m in measures])
    return correlations


def correlations_between_folds(results, measures, fold_sizes, spearman=False):
    correlations = []
    for measure in measures:
        corr = np.zeros((10, 10))
        for i, fold_size1 in enumerate(fold_sizes):
            values1 = results[results["fold_size"] == fold_size1][measure]
            for j, fold_size2 in enumerate(fold_sizes):
                values2 = results[results["fold_size"] == fold_size2][measure]
                if spearman:
                    c = scipy.stats.spearmanr(values1, values2)[0]
                else:
                    c = scipy.stats.pearsonr(values1, values2)[0]
                corr[i, j] = c
        corr = pd.DataFrame(corr, index=fold_sizes, columns=fold_sizes)
        correlations.append(corr)
    return correlations


files = ("per_novel_results_delta_de_no_punctuation.tsv.gz", "per_novel_results_delta_de.tsv.gz", "per_novel_results_delta_en_no_punctuation.tsv.gz", "per_novel_results_delta_en.tsv.gz", "per_novel_results_delta_fr_no_punctuation.tsv.gz", "per_novel_results_delta_fr.tsv.gz", "per_novel_results_gutenberg_no_punctuation.tsv.gz", "per_novel_results_gutenberg.tsv.gz")
for f in files:
    results = pd.read_csv(f, sep="\t", header=0, index_col=0)
    fold_sizes = list(range(1000, 10001, 1000))
    measures = [c for c in results.columns if c.endswith("_mean")]
    directory = "plots_" + f[:-7]
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

    # stability with regard to fold length
    plot_distributions(results, measures, fold_sizes, directory)

    # pearson correlation between measures
    correlations = correlations_between_measures(results, measures, fold_sizes, spearman=False)
    plt.figure(figsize=(15, 15))
    clustergrid = sns.clustermap(correlations, cmap=sns.color_palette("coolwarm", 11), annot=True, fmt=".2f", vmin=-1, vmax=1)
    plt.savefig(os.path.join(directory, "pearson_between_measures.pdf"), format="pdf")

    # spearman correlation between measures
    correlations = correlations_between_measures(results, measures, fold_sizes, spearman=True)
    plt.figure(figsize=(15, 15))
    clustergrid = sns.clustermap(correlations, cmap=sns.color_palette("coolwarm", 11), annot=True, fmt=".2f", vmin=-1, vmax=1)
    plt.savefig(os.path.join(directory, "spearman_between_measures.pdf"), format="pdf")

    # pearson correlation between fold sizes
    correlations = correlations_between_folds(results, measures, fold_sizes, spearman=False)
    for corr, measure in zip(correlations, measures):
        plt.figure(figsize=(10, 10))
        clustergrid = sns.heatmap(corr, cmap=sns.color_palette("coolwarm", 11), annot=True, fmt=".2f", vmin=-1, vmax=1)
        plt.savefig(os.path.join(directory, "pearson_between_foldsizes_%s.pdf" % (measure[:-5],)), format="pdf")

    # spearman correlation between fold sizes
    correlations = correlations_between_folds(results, measures, fold_sizes, spearman=True)
    for corr, measure in zip(correlations, measures):
        plt.figure(figsize=(10, 10))
        clustergrid = sns.heatmap(corr, cmap=sns.color_palette("coolwarm", 11), annot=True, fmt=".2f", vmin=-1, vmax=1)
        plt.savefig(os.path.join(directory, "spearman_between_foldsizes_%s.pdf" % (measure[:-5],)), format="pdf")
