#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename: lexicalrichness.py
# Author: #cf


"""
Function to sample texts and calculate lexical richness measures.
"""


# ===============
# Import
# ===============

import re
import os
import glob
import random
import pandas as pd
from os.path import join
import pygal
import numpy as np
from collections import Counter
from collections import defaultdict
from pygal import style


mystyle = pygal.style.Style(
    background='white',
    plot_background='white',
    font_family="FreeSans",
    title_font_size = 20,
    legend_font_size = 14,
    label_font_size = 12,
    major_label_font_size = 12,
    value_font_size = 12,
    major_value_font_size = 12,
    tooltip_font_size = 12)


# ===============
# Parameters
# ===============

wdir = "/home/christof/Dropbox/0-Analysen/2017/lexicalrichness/"
textpath = join(wdir, "texts", "*.txt")
sampling = [2500,50000,50] # min, max, steps
makeplots = ["samplesize", "vocabsize", "meanwordfreq", "typetokenratio", "GuiraudR", "HerdanC", "DugastK", "MaasA", "TuldavaLN", "HonoreH", "SichelS", "MicheaM"]#, "BrunetW"]


# ===============
# Functions
# ===============

def load_text(file):
    """
    Load the text file and turn it into a list of tokens.
    """
    with open(file, "r") as infile:
        text = infile.read()
        text = re.split("\W", text)
        text = [word for word in text if word]
        return text


def get_sample(text, samplesize):
    """
    Select a sample from the text with a given length.
    "start" can be fixed or random within a given range.
    If it is set to random, results will vary across runs.
    """
    start = 5
    #start = random.randint(100,5100)
    sample = text[start:start+samplesize]
    return sample


def get_vocabsize(sample):
    """
    For a given sample, calculate the number of types (different tokens)
    """
    vocabsize = len(set(sample))
    return vocabsize


def get_numhapaxleg(sample):
    """
    For a given sample, calculate the number of hapax legomena.
    """
    counts = dict(Counter(sample))
    counts = pd.DataFrame(counts, index=["freq"])
    counts = counts.T
    hapaxlegs = counts[(counts.freq==1)]
    numhapaxleg = len(hapaxlegs)
    dislegs = counts[(counts.freq==2)]
    numdisleg = len(dislegs)
    return numhapaxleg, numdisleg


def get_measures(results):
    """
    Based on the basic indicators, calculate measures of lexical richness.
    This part operates directly on the dataframe for better performance.
    """
    vsize = results.loc[:,"vocabsize"]
    ssize = results.loc[:,"samplesize"]
    hleg = results.loc[:,"numhapaxleg"]
    dleg = results.loc[:,"numdisleg"]
    results["meanwordfreq"] = ssize / vsize
    results["typetokenratio"] = vsize / ssize
    results["GuiraudR"] = vsize / np.sqrt(ssize)
    results["HerdanC"] = np.log(vsize) / np.log(ssize)
    results["DugastK"] = np.log(vsize) / np.log(np.log(ssize))
    results["MaasA"] = (np.log(ssize) - np.log(vsize)) / np.log(np.log2(ssize)) #check
    results["TuldavaLN"] = (1 - (vsize ^ 2)) / ((vsize ^ 2) * np.log(ssize))
    results["HonoreH"] = 100 * np.log(ssize) / (1-(hleg/vsize))
    results["SichelS"] = dleg / vsize
    results["MicheaM"] = vsize / dleg
    # results["BrunetW"] = ssize ^ (vsize ^ -0.172) #doesn't work
    return results


def save_dataframe(results, resultsfile):
    """
    Save the table with indicators and measures to file.
    There is one such results file per text analyzed.
    All results from the samples from this text are included.
    """
    with open(resultsfile, "w") as outfile:
        results.to_csv(resultsfile, sep="\t")


def plot_results(wdir, makeplots, filename, results, sampling):
    """
    For each measure and each text, make a lineplot.
    """
    for measure in makeplots:
        plotfolder = join(wdir, "plots", measure)
        if not os.path.exists(plotfolder):
            os.makedirs(plotfolder)
        plotfile = join(plotfolder, filename + "_" + measure + ".svg")
        data = list(results.loc[:,measure])
        lineplot = pygal.XY(show_legend=False,
                            style = mystyle,
                            show_y_guides=True,
                            stroke = True,
                            show_x_guides=True,
                            x_title="sample size",
                            y_title=measure,
                            title="Lexical Richness in " + filename + ": " + measure)
        counter = 0
        for point in data:
            counter +=1
            lineplot.add(str(sampling[0]+counter*sampling[2]), [{"value" : (sampling[0]+counter*sampling[2],point), "color":"darkblue"}], dots_size=1)
        lineplot.render_to_file(plotfile)


# ===============
# Main
# ===============

def main(wdir, textpath, sampling, makeplots):
    """
    Coordinating function for the calculation of measures of lexical richness.
    """
    for file in glob.glob(textpath):
        filename,ext = os.path.basename(file).split(".")
        resultsfile = join(wdir, "data", "lexicalrichness_" + filename + ".csv")
        print(filename)
        text = load_text(file)
        # Set up lists for the basic indicators
        samplesizes = []
        vocabsizes = []
        numhapaxlegs = []
        numdislegs = []
        # For increasing sample size, calculate indicators
        for samplesize in range(sampling[0],sampling[1],sampling[2]):
            sample = get_sample(text, samplesize)
            vocabsize = get_vocabsize(sample)
            numhapaxleg, numdisleg = get_numhapaxleg(sample)
            samplesizes.append(samplesize)
            vocabsizes.append(vocabsize)
            numhapaxlegs.append(numhapaxleg)
            numdislegs.append(numdisleg)
        results = pd.DataFrame(
        {"samplesize":samplesizes,
         "vocabsize":vocabsizes,
         "numhapaxleg":numhapaxlegs,
         "numdisleg":numdislegs})
        # Calculate a number of measures of lexical richness
        results = get_measures(results)
        # Save numeric results to file and plot them
        save_dataframe(results, resultsfile)
        plot_results(wdir, makeplots, filename, results, sampling)
        # TODO: join all dataframes into one big panel object.
        # Then you could get the value for any combination of
        # text analyzed, samplesize, and measure,
        # or the list of values for any of two criteria.

main(wdir, textpath, sampling, makeplots)

