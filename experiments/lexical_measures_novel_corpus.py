#!/usr/bin/env python3

import itertools
import math
import multiprocessing
import os
import psutil
import statistics
import unicodedata

from complexity_measures import surface, utils

# window sizes: 100, 150, 250, 500, 1000, 2500, 5000, 7500, 10000
# +/- punctuation
# +/- case
# disjoint/moving window


def read_csv(filename, ignore_punct=False, lower_case=False):
    with open(filename, encoding="utf-8") as f:
        sentences = utils.get_sentences(f)
        tokens = (t[0] for t in itertools.chain.from_iterable(sentences))
        if ignore_punct:
            tokens = (t for t in tokens if not all((unicodedata.category(c)[0] == "P" for c in t)))
        if lower_case:
            tokens = (t.lower() for t in tokens)
        return list(tokens)


def average_moving_windows(measure, tokens, window_size, **kwargs):
    results = []
    for window in utils.moving_windows(tokens, window_size, step_size=1):
        results.append(measure(window, **kwargs))
    if len(results) == 1:
        return results[0], 0, results
    return statistics.mean(results), utils.confidence_interval(results), results


def analyze_text(args):
    filename, ignore_punct, lower_case, disjoint_windows, window_size = args
    if disjoint_windows:
        bootstrap = surface.bootstrap
    else:
        bootstrap = average_moving_windows
    tokens = read_csv(filename, ignore_punct, lower_case)
    n_windows = len(tokens) // window_size
    if n_windows == 0:
        return tuple(0, ["_"] * 58)
    result_ttr = bootstrap(surface.type_token_ratio, tokens, window_size)
    type_token_ratio = result_ttr[0]
    type_token_ratio_md = statistics.median(result_ttr[2])
    result_guiraud_r = bootstrap(surface.guiraud_r, tokens, window_size)
    guiraud_r = result_guiraud_r[0]
    guiraud_r_md = statistics.median(result_guiraud_r[2])
    result_herdan_c = bootstrap(surface.herdan_c, tokens, window_size)
    herdan_c = result_herdan_c[0]
    herdan_c_md = statistics.median(result_herdan_c[2])
    result_dugast_k = bootstrap(surface.dugast_k, tokens, window_size)
    dugast_k = result_dugast_k[0]
    dugast_k_md = statistics.median(result_dugast_k[2])
    result_maas_a2 = bootstrap(surface.maas_a2, tokens, window_size)
    maas_a2 = result_maas_a2[0]
    maas_a2_md = statistics.median(result_maas_a2[2])
    result_dugast_u = bootstrap(surface.dugast_u, tokens, window_size)
    dugast_u = result_dugast_u[0]
    dugast_u_nan = len([v for v in result_dugast_u[2] if v is math.nan])
    dugast_u_wo_nan = statistics.mean([v for v in result_dugast_u[2] if v is not math.nan])
    dugast_u_md = statistics.median([v for v in result_dugast_u[2] if v is not math.nan])
    result_tuldava_ln = bootstrap(surface.tuldava_ln, tokens, window_size)
    tuldava_ln = result_tuldava_ln[0]
    tuldava_ln_md = statistics.median(result_tuldava_ln[2])
    result_brunet_w = bootstrap(surface.brunet_w, tokens, window_size)
    brunet_w = result_brunet_w[0]
    brunet_w_md = statistics.median(result_brunet_w[2])
    result_cttr = bootstrap(surface.cttr, tokens, window_size)
    cttr = result_cttr[0]
    cttr_md = statistics.median(result_cttr[2])
    result_summer_s = bootstrap(surface.summer_s, tokens, window_size)
    summer_s = result_summer_s[0]
    summer_s_md = statistics.median(result_summer_s[2])
    result_sichel_s = bootstrap(surface.sichel_s, tokens, window_size)
    sichel_s = result_sichel_s[0]
    sichel_s_md = statistics.median(result_sichel_s[2])
    result_michea_m = bootstrap(surface.michea_m, tokens, window_size)
    michea_m = result_michea_m[0]
    michea_m_nan = len([v for v in result_michea_m[2] if v is math.nan])
    michea_m_wo_nan = statistics.mean([v for v in result_michea_m[2] if v is not math.nan])
    michea_m_md = statistics.median([v for v in result_michea_m[2] if v is not math.nan])
    result_honore_h = bootstrap(surface.honore_h, tokens, window_size)
    honore_h = result_honore_h[0]
    honore_h_nan = len([v for v in result_honore_h[2] if v is math.nan])
    honore_h_wo_nan = statistics.mean([v for v in result_honore_h[2] if v is not math.nan])
    honore_h_md = statistics.median([v for v in result_honore_h[2] if v is not math.nan])
    result_entropy = bootstrap(surface.entropy, tokens, window_size)
    entropy = result_entropy[0]
    entropy_md = statistics.median(result_entropy[2])
    result_evenness = bootstrap(surface.evenness, tokens, window_size)
    evenness = result_evenness[0]
    evenness_md = statistics.median(result_evenness[2])
    result_yule_k = bootstrap(surface.yule_k, tokens, window_size)
    yule_k = result_yule_k[0]
    yule_k_md = statistics.median(result_yule_k[2])
    result_simpson_d = bootstrap(surface.simpson_d, tokens, window_size)
    simpson_d = result_simpson_d[0]
    simpson_d_md = statistics.median(result_simpson_d[2])
    result_herdan_vm = bootstrap(surface.herdan_vm, tokens, window_size)
    herdan_vm = result_herdan_vm[0]
    herdan_vm_md = statistics.median(result_herdan_vm[2])
    result_hdd = bootstrap(surface.hdd, tokens, window_size)
    hdd = result_hdd[0]
    hdd_md = statistics.median(result_hdd[2])
    result_mtld = bootstrap(surface.mtld, tokens, window_size)
    mtld = result_mtld[0]
    mtld_md = statistics.median(result_mtld[2])
    result_average_token_length = bootstrap(surface.average_token_length, tokens, window_size)
    average_token_length = result_average_token_length[0]
    average_token_length_md = statistics.median(result_average_token_length[2])
    result_gries_dp = bootstrap(surface.gries_dp, tokens, window_size, n_parts=5)
    gries_dp = result_gries_dp[0]
    gries_dp_md = statistics.median(result_gries_dp[2])
    result_gries_dp_norm = bootstrap(surface.gries_dp_norm, tokens, window_size, n_parts=5)
    gries_dp_norm = result_gries_dp_norm[0]
    gries_dp_norm_md = statistics.median(result_gries_dp_norm[2])
    result_kl_divergence = bootstrap(surface.kl_divergence, tokens, window_size, n_parts=5)
    kl_divergence = result_kl_divergence[0]
    kl_divergence_md = statistics.median(result_kl_divergence[2])
    result_orlov_z = bootstrap(surface.orlov_z, tokens, window_size)
    orlov_z = result_orlov_z[0]
    orlov_z_nan = len([v for v in result_orlov_z[2] if v is math.nan])
    orlov_z_wo_nan = statistics.mean([v for v in result_orlov_z[2] if v is not math.nan])
    orlov_z_md = statistics.median([v for v in result_orlov_z[2] if v is not math.nan])
    return n_windows, type_token_ratio, type_token_ratio_md, guiraud_r, guiraud_r_md, herdan_c, herdan_c_md, dugast_k, dugast_k_md, maas_a2, maas_a2_md, dugast_u, dugast_u_nan, dugast_u_wo_nan, dugast_u_md, tuldava_ln, tuldava_ln_md, brunet_w, brunet_w_md, cttr, cttr_md, summer_s, summer_s_md, sichel_s, sichel_s_md, michea_m, michea_m_nan, michea_m_wo_nan, michea_m_md, honore_h, honore_h_nan, honore_h_wo_nan, honore_h_md, entropy, entropy_md, evenness, evenness_md, yule_k, yule_k_md, simpson_d, simpson_d_md, herdan_vm, herdan_vm_md, hdd, hdd_md, mtld, mtld_md, average_token_length, average_token_length_md, gries_dp, gries_dp_md, gries_dp_norm, gries_dp_norm_md, kl_divergence, kl_divergence_md, orlov_z, orlov_z_nan, orlov_z_wo_nan, orlov_z_md

def main():
    fields = "filename n_windows type_token_ratio type_token_ratio_md guiraud_r guiraud_r_md herdan_c herdan_c_md dugast_k dugast_k_md maas_a2 maas_a2_md dugast_u dugast_u_nan dugast_u_wo_nan dugast_u_md tuldava_ln tuldava_ln_md brunet_w brunet_w_md cttr cttr_md summer_s summer_s_md sichel_s sichel_s_md michea_m michea_m_nan michea_m_wo_nan michea_m_md honore_h honore_h_nan honore_h_wo_nan honore_h_md entropy entropy_md evenness evenness_md yule_k yule_k_md simpson_d simpson_d_md herdan_vm herdan_vm_md hdd hdd_md mtld mtld_md average_token_length average_token_length_md gries_dp gries_dp_md gries_dp_norm gries_dp_norm_md kl_divergence kl_divergence_md orlov_z orlov_z_nan orlov_z_wo_nan orlov_z_md".split()
    directory = "../../complexity-corpus/Romankorpus/tagged"
    # n_proc = psutil.cpu_count(logical=False) - 2
    n_proc = 10
    print("Use %d processes" % n_proc)
    with multiprocessing.Pool(processes=n_proc) as pool:
        for disjoint_windows in (True, False):
            for lower_case in (False, True):
                for ignore_punct in (False, True):
                    for window_size in (100, 150, 250, 500, 1000, 2500, 5000, 7500, 10000):
                        with open(os.path.join("lexical_measures_novel_corpus", "lexical_measures_%s_%d%s%s.tsv" % ("disjoint" if disjoint_windows else "moving", window_size, "-punct" if ignore_punct else "+punct", "-case" if lower_case else "+case")), mode="w", encoding="utf-8") as out:
                            out.write("\t".join(fields) + "\n")
                            filenames = [fn for fn in sorted(os.listdir(directory)) if fn.endswith(".csv")]
                            args = zip([os.path.join(directory, fn) for fn in filenames], itertools.repeat(ignore_punct), itertools.repeat(lower_case), itertools.repeat(disjoint_windows), itertools.repeat(window_size))
                            outputs = pool.imap(analyze_text, args)
                            for filename, output in zip(filenames, outputs):
                                out.write(filename + "\t" + "\t".join([repr(o) for o in output]) + "\n")


if __name__ == "__main__":
    main()
