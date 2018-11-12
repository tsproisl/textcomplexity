#!/usr/bin/env python3

from nltk.tree import ParentedTree
import nltk_tgrep

# Average number of CONSTITUENTs per sentence (NP, VP, PP, SBAR)

# Average length of CONSTITUENT (NP, VP, PP)

# Average number of constituents per sentence

# NUR = FRAG?

# Lu 2010

# clauses = S
# 


examples = ["(TOP(CS(S(KON Und)(ADV dann)(VVFIN kam)(ADJD unvermittelt)(NP(ART der)(NN Moment)))($, ,)(S(S(KOUS da)(PPER sie)(VP(PIS beide)(VVINF auflegen))(VMFIN mussten))($, ,)(PP(APPR aus)(PIAT irgendeinem)(NN Grund)))($, ,)(KON und)(S(NP(ART die)(NN Frau))(VVFIN begann)(NP(PPOSAT ihr)(NN Gepäck)(PP(APPRART im)(NN Abteil)))(VZ(PTKZU zu)(VVINF verstauen)))($. .)))",
            "(TOP(S(NP(ART Die)(NN Leute))(VMFIN mussten)(PPER ihm)(VP(VVINF ausweichen)($, ,)(PP(APPR mit)(CNP(NP(PPOSAT ihren)(CNP(NN Koffern)(KON und)(NN Kindern)))(KON und)(PIS allem)))($, ,)(S(PRELS was)(PIS man)(ADV sonst)(ADV noch)(VP(PP(APPRART im)(NN Leben))(PP(APPR hinter)(PRF sich))(VVINF herziehen))(VMFIN musste)))($. .)))",
            "(TOP(S(NP(PPOSAT Sein)(NN Koffer))(VVFIN lehnte)(PRF sich)(PP(APPR an)(PPOSAT sein)(ADJA linkes)(NN Bein))($. .)))"]
for example in examples:
    tree = ParentedTree.fromstring(example)
    print(tree)
    # t-units: TOP-S, TOP-CS-S
    result = nltk_tgrep.tgrep_nodes(tree, "S > (CS > TOP) | > TOP")
    print(len(result))
    for res in result:
        print(res)
