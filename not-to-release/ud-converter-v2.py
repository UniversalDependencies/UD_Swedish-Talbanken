import re, sys, pprint

def check_index(type, index, myindex):
    if index != myindex:
        print("# Index error (" + type + "): " + str(index) + " != " + str(myindex))

def print_header(header):
    for (doc, par, msm, sid, tid, cat, dum, tok, pos, syn, suc, fea, lem) in header:
        print("\t".join(["#", doc + "." + str(par), tok, pos, syn]))

def find_lemma(word):
    tmp = word[12]
    if "|" in tmp:
        if tmp == "befinnas|befinna":
            return "befinna"
        elif tmp == "behövas|behöva":
            return "behöva"
        elif tmp in ["dras|dra", "dras|dra|dra ner"]:
            return "dra"
        elif tmp == "enas|ena":
            return "ena"
        elif tmp == "fattas|fatta" and (word[0], word[3], word[4]) == ("P113", 42, 3):
            return "fatta"
        elif tmp == "fordra|fordras":
            return "fordra"
        elif tmp in ["hållas|hålla", "hållas|hålla|hålla tillbaka"]:
            return "hålla"
        elif tmp == "krävas|kräva":
            return "kräva"
        elif tmp == "ledas|leda":
            return "leda"
        elif tmp == "rivas|riva|riva sönder":
            return "riva"
        elif tmp in ["räknas|räkna", "räknas|räkna|räkna upp", "räknas|räkna|räkna ut"]:
            return "räkna"
        elif tmp == "saknas|sakna":
            return "sakna"
        elif tmp in ["samlas|samla", "samlas|samla|samla upp"]:
            return "samla"
        elif tmp == "skiljas|skilja":
            return "skilja"
        elif tmp in ["tas|ta", "tas|ta|ta ansvar", "tas|ta|ta hänsyn","tas|ta|ta in", "tas|ta|ta tillvara", "tas|ta|ta upp", "tas|ta|ta ut", "tas|ta|ta vid"]:
            return "ta"
        elif tmp == "trängas|tränga" and (word[0], word[3], word[4]) == ("P110", 71, 12):
            return "tränga"
        elif tmp == "tröttas|trötta|trötta ut":
            return "trötta"
        elif tmp == "täcka|täckas":
            return "täcka"
        elif tmp == "utvecklas|utveckla":
            return "utveckla"
        else:
            tmps = tmp.split("|")
            tmp = tmps[0]
    if " " in tmp and not " " in word[7]:
        if re.match("i vilket fall som helst", tmp):
            return "vilken"
        elif re.match("med berått mod", tmp):
            return "beråda"
#        elif re.match("Svenska Dagbladet", tmp) and word[7] == "Dagbladets":
#            return "dagblad"
        elif re.match("gifta sig", tmp):
            return "gifta"
        else:
            tmps = tmp.split(" ")
            if ":" in tmps[-1]:
                tmps = tmps[:-1] + [tmps[-1][:tmps[-1].index(":")]]
            for t in tmps:
                if t.lower() == word[7].lower():
                    return t.lower()
                elif t+"s" == word[7]:
                    return t.lower()
            return "_".join(tmps)
    else:
        return tmp

def fix_coordination(sentence):
    for word in sentence:
        if deprel[word[4]] == "cc" and head[word[4]] < word[4]:
            for hword in sentence:
                if deprel[hword[4]] == "conj" and head[hword[4]] == head[word[4]] and hword[4] > word[4] and not hword[5] in ["D", "X", "N"]:
                    head[word[4]] = hword[4]
                    break
    for word in sentence:
        if deprel[word[4]] == "punct" and head[word[4]] < word[4] and word[7] in [",", ";"]:
            for hword in sentence:
                if deprel[hword[4]] == "punct" and head[hword[4]] == head[word[4]] and hword[4] > word[4]:
                    break
                if deprel[hword[4]] == "conj" and head[hword[4]] == head[word[4]] and hword[4] > word[4] and not hword[5] in ["D", "X", "N"]:
                    head[word[4]] = hword[4]
                    break

def fix_orphan(sentence):
    for word in sentence:
        if deprel[word[4]] in ["nsubj", "nsubj:pass", "obj", "iobj", "obl", "csubj", "csubj:pass", "xcomp", "ccomp", "advcl"]:
            for hword in sentence:
                if head[word[4]] == hword[4] and hword[9][-2:] in ["SS", "OO", "IO"] and deprel[hword[4]] in ["conj", "parataxis", "root"]:
                    misc[word[4]].append("Enhanced=" + deprel[word[4]])
                    deprel[word[4]] = "orphan"
                    misc[hword[4]].append("Enhanced=" + dep_label(0, head[hword[4]], "", hword))

def fix_spacing(sentence):
    for word in sentence:
        misc[word[4]] = []
    for i in range(0, len(sentence)):
        word = sentence[i]
        if word[7] == "(":
            misc[word[4]].append("SpaceAfter=No")
        elif word[7] == "'":
            if head[word[4]] > word[4]:
                misc[word[4]].append("SpaceAfter=No")
            else:
                misc[sentence[i-1][4]].append("SpaceAfter=No")
        elif word[7] in [",", ";", ".", ":", "?", "!", ")"]:
            misc[sentence[i-1][4]].append("SpaceAfter=No")
 
def fix_det(sentence):
    for word in sentence:
        if deprel[word[4]] == "det" and word[10] in ["JJ", "RO", "PC"]:
#            for dword in sentence:
#                if head[dword[4]] == head[word[4]] and dword[4] < word[4] and deprel[dword[4]] == "det":
            deprel[word[4]] = "amod"
        if deprel[word[4]] == "det" and word[12] in ["kl.", "kl"] and word[10] == "AB":
            deprel[word[4]] = "nmod"
            postag[word[4]] = "NOUN"
        if deprel[word[4]] == "det" and word[12] in ["resp", "respektive"]:
            deprel[word[4]] = "amod"

def print_sentence(sentence):
    parse_sentence(sentence)
    map_labels(sentence)
    if remove_dummies(sentence):
        reattach(sentence)
        relabel(sentence) # All verbs are labeled aux
        retag(sentence) # Fix remaining attachment and labeling errors too! AUX -> aux, cop; VERB -> not aux, not cop
        fix_det(sentence)
        fix_apposition(sentence)
        fix_coordination(sentence)
        fix_spacing(sentence)
        fix_orphan(sentence)
        # Print only nonword; decrement both word[id] and head[id]
        # Check if nonword is correct; such = "_" for omitted words?
        for (doc, par, msm, sid, tid, cat, dum, tok, pos, syn, suc, fea, lem) in sentence:
            if not tid in nonword:
                lem = find_lemma((doc, par, msm, sid, tid, cat, dum, tok, pos, syn, suc, fea, lem))
                if fea != "_":
                    tag = "|".join([suc,fea])
                else:
                    tag = suc
                utag = postag[tid]
                ufea = features[tid]
                if misc[tid] == []:
                    mis = "_"
                else:
                    mis = "|".join(sorted(set(misc[tid])))
                if utag == "VERB" and lem[-1] == "s":
                    ufeats = ufea.split("|")
                    if "Voice=Pass" in ufeats:
                        ufeats.remove("Voice=Pass")
                    ufea = "|".join(ufeats)
                if tid in deprel:
                    dep = deprel[tid]
                else:
                    print("# No deprel")
                    dep = syn
                if tid in head:
                    hd = head[tid] - decrement[head[tid]]
                    tid = tid - decrement[tid]
                else:
                    hd = -1
                if re.search("ST$", syn):
                    print("\t".join(["#", doc + "." + str(par), "ST", "ST"]))
                print("\t".join([str(tid), tok, lem, utag, tag, ufea, str(hd), dep, "_", mis])) 
        print()
    else:
        print("# Sentence omitted")

def fix_apposition(sentence):
    for w1 in sentence:
        if not w1[5] in ["D", "X", "N"] and deprel[w1[4]] in ["appos", "conj", "nmod"]:
            appos_head = w1
            for w2 in sentence[:sentence.index(w1)]:
                if not w2[5] in ["D", "N", "X"] and head[w1[4]] == w2[4]:
                    appos_head = w2
                    break
            if appos_head != w1:
                appos_root = w2
                non_proj = 0
                for w3 in sentence[sentence.index(w2)+1:sentence.index(w1)]:
                    if not w3[5] in ["D", "N", "X"] and head[appos_root[4]] == w3[4]:
                        appos_root = w3
                    elif non_proj == 0 and not w3[5] in ["D", "N", "X"] and head[w3[4]] < appos_head[4]:
                        non_proj = sentence.index(w3)
                if appos_root != w2:
                    head[w1[4]] = appos_root[4]
                    deprel[w1[4]] = "parataxis"
                    for w4 in sentence[sentence.index(appos_root)+1:]:
                        if head[w4[4]] == appos_head[4] and not deprel[w4[4]] in ["case"]:
                            head[w4[4]] = appos_root[4]
                elif non_proj > 0 and deprel[w1[4]] == "appos":
                    for w3 in sentence[:sentence.index(w1)]:
                        if not w3[5] in ["D", "N", "X"] and head[appos_root[4]] == w3[4]:
                            appos_root = w3
                    if appos_root != w2:
                        head[w1[4]] = appos_root[4]
                        deprel[w1[4]] = "parataxis"
                        for w4 in sentence[non_proj:]:
                            if head[w4[4]] == appos_head[4] and not deprel[w4[4]] in ["acl:relcl"]:
                                head[w4[4]] = appos_root[4]
    if sentence[0][0] == "P218" and sentence[0][3] == 40:
        head[sentence[8][4]] = sentence[14][4]
        deprel[sentence[8][4]] = "advcl"
                        
    for w1 in sentence:
        if not w1[5] in ["D", "X", "N"] and deprel[w1[4]] in ["parataxis", "conj"]:
            para_head = w1
            for w2 in sentence[:sentence.index(w1)]:
                if not w2[5] in ["D", "N", "X"] and head[w1[4]] == w2[4]:
                    para_head = w2
#                    print("Found para: " + w2[7] + " : " + w1[7])
                    break
            if para_head != w1:
                for w3 in sentence[sentence.index(w2)+1:sentence.index(w1)]:
                    for w4 in sentence[sentence.index(w1)+1:]:
                        if not w3[5] in ["D", "N", "X"] and not w4[5] in ["D", "N", "X"] and head[w4[4]] == w3[4]:
#                            print("Found xy: " + w3[7] + " : " + w4[7]) 
                            for w5 in sentence[sentence.index(w3)+1:sentence.index(w4)]:
                                if w5[9][-2:] == "++":
                                    break
                                elif not w5[5] in ["D", "N", "X"] and head[w5[4]] == para_head[4] and head[w3[4]] != w5[4] and deprel[w5[4]] != "nmod":
#                                    print("Found z: " + w5[7])
                                    head[w5[4]] = w3[4]
                                    if deprel[w5[4]] == "conj":
                                        deprel[w5[4]] = "parataxis"
    if sentence[0][0] == "P218" and sentence[0][3] == 54:
        head[sentence[6][4]] = sentence[5][4]
        head[sentence[10][4]] = sentence[5][4]
        head[sentence[13][4]] = sentence[5][4]
    if sentence[0][0] == "P405" and sentence[0][3] == 18:
        head[sentence[13][4]] = sentence[12][4]
        head[sentence[18][4]] = sentence[12][4]
    if sentence[0][0] == "P405" and sentence[0][3] == 24:
        head[sentence[7][4]] = sentence[6][4]
        head[sentence[12][4]] = sentence[6][4]
    if sentence[0][0] == "P209" and sentence[0][3] == 78:
        deprel[sentence[12][4]] = "appos"
    if sentence[0][0] == "P409" and sentence[0][3] == 63:
        head[sentence[112][4]] = sentence[114][4]
        deprel[sentence[112][4]] = "obl"
        head[sentence[47][4]] = sentence[39][4]
        deprel[sentence[47][4]] = "conj"
        head[sentence[74][4]] = sentence[39][4]
        head[sentence[85][4]] = sentence[39][4]
        deprel[sentence[85][4]] = "conj"
        head[sentence[91][4]] = sentence[39][4]
        head[sentence[94][4]] = sentence[39][4]
        deprel[sentence[94][4]] = "conj"

def reattach(sentence):
    for w1 in sentence:
        for w2 in sentence:
            if w1[4] < w2[4] and head[w1[4]] == w2[4] and deprel[w1[4]] == "cc" and deprel[w2[4]] in ["conj", "parataxis"] and w2[4] in head:
#                print("Reattached cc: " + str(w1[4]))
                if head[w2[4]] < w2[4]:
                    head[w1[4]] = head[w2[4]]
                    if deprel[w2[4]] == "parataxis":
                        deprel[w2[4]] = "conj"
                else:
                    h = head[w2[4]]
                    candidates = sentence[:w1[4]-1]
                    candidates.reverse()
                    for w3 in candidates:
                        if not w3[4] in nonword and head[w3[4]] == head[w2[4]] and not deprel[w3[4]] in ["punct", "neg", "cc"]:
                            head[w2[4]] = w3[4]
                            head[w1[4]] = w3[4]
                            break
                    if head[w2[4]] != h:
                        puncts = sentence[head[w2[4]]:h-1]
                        for w4 in puncts:
                            if not w4 in nonword and head[w4[4]] == h and (deprel[w4[4]] in ["punct"] or (deprel[w4[4]] in ["neg"] and w4[4] < w1[4])):
                                head[w4[4]] = head[w2[4]]
    for w1 in sentence:
        if head[w1[4]] == 0 and w1[10] in ["MAD", "MID", "PAD"]:
            new_head = 0
            for w2 in sentence:
                if head[w2[4]] == w1[4] and w2[5] not in ["D", "N", "X"]:
                    head[w2[4]] = 0
                    head[w1[4]] = w2[4]
                    new_head = w2[4]
                    deprel[w1[4]] = "punct"
#                    print("Found new head: " + str(new_head))
                    break
            if head[w1[4]] == 0:
                for w2 in sentence:
                    if head[w2[4]] == 0 and w2[5] not in ["D", "N", "X"]:
                        head[w1[4]] = w2[4]
                        new_head = w2[4]
                        deprel[w1[4]] = "punct"
                        break
            for w2 in sentence:
                if head[w2[4]] == w1[4]:
                    head[w2[4]] = new_head
                if head[w2[4]] == 0 and w2[4] != new_head:
                    head[w2[4]] = new_head
                    if w2[10] in ["MAD", "MID", "PAD"]:
                        deprel[w2[4]] = "punct"
                    else:
                        deprel[w2[4]] = "conj" # Crude hack!
            if head[w1[4]] == 0:
                print("# Found no alternative root to punctuation.")
    for w1 in sentence:
        if head[w1[4]] == 0 and w1[9][-2:] == "YY":
            new_head = 0
            for w2 in sentence:
#                print("# Candidate head: " + str(w2) + " head: " + str(head[w2[4]]) + " deprel: " + deprel[w2[4]])
                if head[w2[4]] == w1[4] and w2[5] not in ["D", "N", "X"] and deprel[w2[4]] in ["conj", "parataxis"]:
                    head[w2[4]] = 0
                    head[w1[4]] = w2[4]
                    new_head = w2[4]
                    deprel[w1[4]] = "discourse"
#                    print("Found new head: " + str(new_head))
                    break
            if new_head != 0:
                for w2 in sentence:
                    if head[w2[4]] == w1[4]:
                        head[w2[4]] = new_head
            if head[w1[4]] == 0:
                print("# Found no alternative root to discourse.")
    if sentence[0][0] == "P103" and sentence[0][3] == 27:
        head[sentence[11][4]] = sentence[2][4]
    if sentence[0][0] == "P404" and sentence[0][3] == 31:
        head[sentence[29][4]] = sentence[8][4]
        head[sentence[38][4]] = sentence[8][4]
        head[sentence[49][4]] = sentence[8][4]
        deprel[sentence[29][4]] = "conj"    
    if sentence[0][0] == "P110" and sentence[0][3] == 48:
        head[sentence[13][4]] = sentence[12][4]
        head[sentence[15][4]] = sentence[12][4]
        head[sentence[24][4]] = sentence[12][4]
        head[sentence[25][4]] = sentence[12][4]
    if sentence[0][0] == "P118" and sentence[0][3] == 61:
        head[sentence[8][4]] = 0 # ROOT -> regler
        deprel[sentence[8][4]] = "root"
        head[sentence[4][4]] = sentence[8][4] # regler -> trafikmiljö
        deprel[sentence[4][4]] = "advcl"
        head[sentence[5][4]] = sentence[8][4] # regler -> ,
        head[sentence[9][4]] = sentence[8][4] # regler -> .
    if sentence[0][0] == "P118" and sentence[0][3] == 62:
        head[sentence[8][4]] = 0 # ROOT -> krav
        deprel[sentence[8][4]] = "root"
        head[sentence[4][4]] = sentence[8][4] # krav -> trafikregler
        deprel[sentence[4][4]] = "advcl"
        head[sentence[5][4]] = sentence[8][4] # krav -> ,
        head[sentence[12][4]] = sentence[8][4] # krav -> och
        deprel[sentence[12][4]] = "cc"
        head[sentence[15][4]] = sentence[8][4] # krav -> regelbrott
        head[sentence[16][4]] = sentence[8][4] # krav -> .
    if sentence[0][0] == "P120" and sentence[0][3] == 58:
        head[sentence[5][4]] = sentence[4][4]
        head[sentence[7][4]] = sentence[4][4]
        head[sentence[9][4]] = sentence[4][4]
        head[sentence[10][4]] = sentence[4][4]
    if sentence[0][0] == "P122" and sentence[0][3] == 6:
        head[sentence[17][4]] = sentence[15][4]
        head[sentence[20][4]] = sentence[15][4]
        head[sentence[18][4]] = sentence[20][4]
        head[sentence[19][4]] = sentence[20][4]
        deprel[sentence[20][4]] = "conj"
        deprel[sentence[18][4]] = "advmod"
    if sentence[0][0] == "P122" and sentence[0][3] == 94:
        head[sentence[10][4]] = sentence[1][4]
    if sentence[0][0] == "P201" and sentence[0][3] == 3:
        head[sentence[10][4]] = sentence[7][4] # hända -> sa
        deprel[sentence[10][4]] = "parataxis"
        head[sentence[7][4]] = 0 # root -> hända
        deprel[sentence[7][4]] = "root"
        head[sentence[9][4]] = sentence[7][4] # hända -> ,
        head[sentence[21][4]] = sentence[7][4] # hända -> ,
    if sentence[0][0] == "P201" and sentence[0][3] == 10:
        head[sentence[7][4]] = sentence[5][4]
        head[sentence[8][4]] = sentence[5][4]
        head[sentence[9][4]] = sentence[5][4]
        deprel[sentence[5][4]] = "dislocated" # "dislocated:root"
        deprel[sentence[7][4]] = "conj"
        deprel[sentence[9][4]] = "conj"
    if sentence[0][0] == "P201" and sentence[0][3] == 64:
        head[sentence[10][4]] = sentence[6][4] # Krister -> Ingemund
        deprel[sentence[10][4]] = "conj"
        head[sentence[14][4]] = sentence[6][4] # Krister -> Torsten
        deprel[sentence[14][4]] = "conj"
        head[sentence[17][4]] = sentence[6][4] # Krister -> etc.
        deprel[sentence[17][4]] = "conj"
    if sentence[0][0] == "P201" and sentence[0][3] == 39:
        head[sentence[15][4]] = sentence[8][4] # ser -> ,
        head[sentence[17][4]] = sentence[8][4] # ser -> löser
        head[sentence[21][4]] = sentence[8][4] # ser -> ,
        head[sentence[25][4]] = sentence[8][4] # ser -> uttolkare
        head[sentence[32][4]] = sentence[8][4] # ser -> etc.
    if sentence[0][0] == "P203" and sentence[0][3] == 7:
        head[sentence[10][4]] = sentence[3][4] 
    if sentence[0][0] == "P203" and sentence[0][3] == 27:
        head[sentence[10][4]] = sentence[4][4] # klarar -> gå
        deprel[sentence[10][4]] = "parataxis"
    if sentence[0][0] == "P203" and sentence[0][3] == 29:
        head[sentence[11][4]] = sentence[6][4] # göra -> men
        deprel[sentence[11][4]] = "cc"
        head[sentence[25][4]] = sentence[6][4] # göra -> jobb
        deprel[sentence[25][4]] = "conj"
    if sentence[0][0] == "P203" and sentence[0][3] == 39:
        head[sentence[27][4]] = sentence[25][4]
        head[sentence[30][4]] = sentence[25][4]
        head[sentence[35][4]] = sentence[25][4]
        head[sentence[38][4]] = sentence[25][4]
        head[sentence[42][4]] = sentence[25][4]
        deprel[sentence[30][4]] = "conj"
        deprel[sentence[38][4]] = "conj"
    if sentence[0][0] == "P203" and sentence[0][3] == 74:
        head[sentence[6][4]] = sentence[5][4]
        head[sentence[8][4]] = sentence[5][4]
        head[sentence[11][4]] = sentence[5][4]
        head[sentence[13][4]] = sentence[5][4]
        head[sentence[19][4]] = sentence[5][4]
        head[sentence[21][4]] = sentence[5][4]
        deprel[sentence[13][4]] = "conj"
    if sentence[0][0] == "P207" and sentence[0][3] == 16:
        head[sentence[23][4]] = sentence[18][4]
        deprel[sentence[23][4]] = "conj"
        head[sentence[24][4]] = sentence[18][4]
        head[sentence[30][4]] = sentence[18][4]
        deprel[sentence[30][4]] = "conj"
    if sentence[0][0] == "P207" and sentence[0][3] == 41:
        head[sentence[5][4]] = 0 # ROOT -> är
        deprel[sentence[5][4]] = "root"
        head[sentence[1][4]] = sentence[5][4] # är -> Huvudpunkterna
        deprel[sentence[1][4]] = "nsubj"
        head[sentence[8][4]] = sentence[5][4] # är -> Horn
        deprel[sentence[8][4]] = "obl"
        head[sentence[9][4]] = sentence[5][4] # är -> .
    if sentence[0][0] == "P209" and sentence[0][3] == 72:
        head[sentence[13][4]] = sentence[12][4]
        head[sentence[19][4]] = sentence[12][4]
        deprel[sentence[19][4]] = "conj"
    if sentence[0][0] == "P220" and sentence[0][3] == 7:
        head[sentence[32][4]] = sentence[24][4]
        head[sentence[33][4]] = sentence[24][4]
        deprel[sentence[32][4]] = "conj"
        head[sentence[34][4]] = sentence[24][4]
        head[sentence[39][4]] = sentence[24][4]
        deprel[sentence[39][4]] = "conj"
    if sentence[0][0] == "P226" and sentence[0][3] == 26:
        deprel[sentence[17][4]] = "conj"
    if sentence[0][0] == "P227" and sentence[0][3] == 62:
        head[sentence[11][4]] = sentence[15][4]
        head[sentence[12][4]] = sentence[15][4]
        deprel[sentence[11][4]] = "discourse"
    if sentence[0][0] == "P228" and sentence[0][3] == 21:
        head[sentence[5][4]] = 0 # ROOT -> sällskapshunden
        deprel[sentence[5][4]] = "root"
        head[sentence[1][4]] = sentence[5][4] # sällskapshunden -> Och
        deprel[sentence[1][4]] = "cc"
        head[sentence[3][4]] = sentence[5][4] # sällskapshunden -> inte
        deprel[sentence[3][4]] = "advmod"
        features[sentence[3][4]] = "Polarity=Neg"
        head[sentence[4][4]] = sentence[5][4] # sällskapshunden -> minst
        deprel[sentence[4][4]] = "advmod"
        head[sentence[6][4]] = sentence[5][4] # sällskapshunden -> .
    if sentence[0][0] == "P304" and sentence[0][3] == 197:
        head[sentence[18][4]] = sentence[21][4]
        head[sentence[51][4]] = sentence[54][4]
    if sentence[0][0] == "P306" and sentence[0][3] == 77:
        head[sentence[20][4]] = sentence[16][4]
    if sentence[0][0] == "P308" and sentence[0][3] == 2:
        head[sentence[22][4]] = sentence[20][4]
        head[sentence[23][4]] = sentence[20][4]
        head[sentence[24][4]] = sentence[20][4]
        head[sentence[32][4]] = sentence[7][4] 
        head[sentence[34][4]] = sentence[7][4] 
        head[sentence[44][4]] = sentence[7][4] 
        deprel[sentence[22][4]] = "conj"
    if sentence[0][0] == "P309" and sentence[0][3] == 33:
        head[sentence[7][4]] = sentence[10][4] # fördelas -> säger
        deprel[sentence[7][4]] = "parataxis"
        head[sentence[10][4]] = 0 # root -> säger
        deprel[sentence[10][4]] = "root"
        head[sentence[6][4]] = sentence[10][4] # säger -> ,
        head[sentence[9][4]] = sentence[10][4] # säger -> ,
    if sentence[0][0] == "P401" and sentence[0][3] == 6:
        head[sentence[16][4]] = sentence[12][4] # kan -> grad
        head[sentence[18][4]] = sentence[12][4] # kan -> och
        head[sentence[19][4]] = sentence[12][4] # kan -> bord
    if sentence[0][0] == "P401" and sentence[0][3] == 10:
        head[sentence[51][4]] = sentence[50][4] # känslomässig -> och
        head[sentence[52][4]] = sentence[50][4] # känslomässig -> andra
        deprel[sentence[52][4]] = "conj"
        head[sentence[53][4]] = sentence[50][4] # känslomässig -> befriande
        deprel[sentence[53][4]] = "conj"
    if sentence[0][0] == "P403" and sentence[0][3] == 9:
        deprel[sentence[16][4]] = "conj"
    if sentence[0][0] == "P406" and sentence[0][3] == 38:
        head[sentence[5][4]] = sentence[3][4] 
        head[sentence[7][4]] = sentence[3][4] 
        head[sentence[10][4]] = sentence[3][4] 
    if sentence[0][0] == "P408" and sentence[0][3] == 7:
        head[sentence[35][4]] = sentence[31][4] 
        head[sentence[37][4]] = sentence[31][4] 
        head[sentence[45][4]] = sentence[31][4] 
    if sentence[0][0] == "P408" and sentence[0][3] == 27:
        head[sentence[23][4]] = sentence[17][4] 
        head[sentence[25][4]] = sentence[17][4] 
    if sentence[0][0] == "P409" and sentence[0][3] == 56:
        head[sentence[31][4]] = sentence[20][4] 
    if sentence[0][0] == "P410" and sentence[0][3] == 21:
        head[sentence[23][4]] = sentence[28][4] 
        head[sentence[24][4]] = sentence[28][4] 
    if sentence[0][0] == "P413" and sentence[0][3] == 91:
        head[sentence[10][4]] = sentence[15][4] # arbeta -> t.ex.
        deprel[sentence[10][4]] = "advmod"
        head[sentence[12][4]] = sentence[15][4] # arbeta -> mellan
        head[sentence[14][4]] = sentence[15][4] # arbeta -> att
        head[sentence[15][4]] = sentence[9][4] # välja -> arbeta
        head[sentence[16][4]] = sentence[15][4] # arbeta -> borta
        head[sentence[17][4]] = sentence[15][4] # arbeta -> och
        head[sentence[19][4]] = sentence[15][4] # arbeta -> arbeta
        head[sentence[21][4]] = sentence[15][4] # arbeta -> ,
        head[sentence[22][4]] = sentence[27][4] # ha -> t.ex.
        deprel[sentence[22][4]] = "advmod"
        head[sentence[24][4]] = sentence[27][4] # ha -> mellan
        head[sentence[26][4]] = sentence[27][4] # ha -> att
        head[sentence[27][4]] = sentence[15][4] # arbeta -> ha
        head[sentence[28][4]] = sentence[27][4] # ha -> barn
        head[sentence[29][4]] = sentence[27][4] # ha -> och
        head[sentence[31][4]] = sentence[27][4] # ha -> ta
    if sentence[0][0] == "P416" and sentence[0][3] == 74:
        head[sentence[12][4]] = sentence[4][4] 
        head[sentence[18][4]] = sentence[4][4] 
        head[sentence[20][4]] = sentence[4][4] 
    if sentence[0][0] == "P110" and sentence[0][3] == 55:
        head[sentence[14][4]] = sentence[10][4] # bekämpas -> ,
        head[sentence[22][4]] = sentence[10][4] # bekämpas -> förbättrats
        deprel[sentence[22][4]] = "conj"
        head[sentence[23][4]] = sentence[10][4] # bekämpas -> och
        head[sentence[32][4]] = sentence[10][4] # bekämpas -> ökat
        deprel[sentence[32][4]] = "conj"
    if sentence[0][0] == "P308" and sentence[0][3] == 32:
        deprel[sentence[13][4]] = "acl"
        deprel[sentence[30][4]] = "conj"
    if sentence[0][0] == "P102" and sentence[0][3] == 87:
        deprel[sentence[3][4]] = "obj"

def passive(word):
    if word[12] == "fattas|fatta" and word[0] != "P113":
        return False
    if word[12] == "trängas|tränga" and word[0] != "P110":
        return False
    if word[12] in ["andas", "brottas", "finnas|finna", "handskas", "hoppas|hoppa", "kräkas", "kännas|känna", 
                    "låtsas|låtsa", "mattas|matta", "minnas|minna", "mötas|möta", "rymmas|rymma", "samsas|samsa",
                    "synas", "trivas", "tyckas|tycka", "tyckas|tycka|tycka om", "töras", "utspelas", "vistas"]: # Add ambiguous cases
        return False
    else:
        return True

def relabel_ellipsis(fun):
    if fun == "SS":
        return "nsubj"
    elif fun == "OO":
        return "obj"
    elif fun == "AG":
        return "obl:agent"
    elif fun == "ANSP":
        return "appos"
    elif fun == "SP":
        return "xcomp"
    elif fun in ["AT", "ET", "EU"]:
        return "nmod"
    else:
        return "obl"

def relabel(sentence):
    for w1 in sentence:
        if deprel[w1[4]] in ["det", "amod"]:
            for w2 in sentence:
                if head[w1[4]] == w2[4] and w1[9][-2:] in ["AT", "DT", "DU", "DV"] and ((len(w1[9]) > len(w2[9]) and w1[9][:-2] != w2[9]) or (len(w1[9]) == len(w2[9]) and w1[9][-4:-2] != w2[9][-4:-2])):
                    if len(w1[9]) > 4 and w1[9][-6:-2] == "ANSP":
                        fun = "ANSP"
                    else:
                        fun = w1[9][-4:-2]
                    deprel[w1[4]] = relabel_ellipsis(fun)
    for w1 in sentence:
        for w2 in sentence:
            if head[w1[4]] == w2[4] and deprel[w1[4]] == "aux":
                if w1[2] != w2[2] or w1[9][-6:] == "ANSPIV":
                    deprel[w1[4]] = "parataxis"
                elif (w2[9][-2:] in ["SP", "FV", "IV", "IX"] or w2[9][-4:] in ["SPAA", "SPAT", "SPDB", "SPDT", "SPDU", "SPDV"]) and re.search("AV", w1[8]):
                    deprel[w1[4]] = "cop"
                elif w1[9][-4:] in ["OOIV", "OAIV", "EOIV", "VSIV", "VOIV"] and not ((w2[9][-4:] == w1[9][-4:-2] + "IX" or w2[9][-2:] == "SP") and len(w1[9]) == len(w2[9])):
                    deprel[w1[4]] = "xcomp"
                elif w1[9][-4:] in ["SSIV", "ESIV"] and not ((w2[9][-4:] == w1[9][-4:-2] + "IX" or w2[9][-2:] == "SP") and len(w1[9]) == len(w2[9])):
                    deprel[w1[4]] = "csubj"
            if w1[4] > w2[4] and head[w1[4]] == w2[4] and w1[9] == w2[9] and deprel[w1[4]] != "fixed" and deprel[w1[4]] != "parataxis":
                deprel[w1[4]] = "conj"
            if head[w1[4]] == w2[4] and deprel[w1[4]] == "nsubj" and re.search("SFO", w2[11]) and passive(w2):
                deprel[w1[4]] = "nsubj:pass"
            if head[w1[4]] == w2[4] and deprel[w1[4]] == "csubj" and re.search("SFO", w2[11]) and passive(w2):
                deprel[w1[4]] = "csubj:pass"
            if head[w1[4]] == w2[4] and w1[8] == "ID" and re.match("PN", w2[8]):
                deprel[w1[4]] = "flat:name"
            if head[w1[4]] == w2[4] and deprel[w1[4]] == "dep" and re.match("AV", w2[8]):
                deprel[w1[4]] = "dislocated"
                for w3 in sentence:
                    if head[w3[4]] == w2[4] and deprel[w3[4]] == "nsubj" and w3[7] in ["det", "Det", "DET"]:
                        deprel[w3[4]] = "expl"
        if deprel[w1[4]] == "det" and (w1[10] in ["PS", "HS"] or (w1[10] in ["NN", "PM"] and (re.search("GG", w1[8]) or re.search("GEN", w1[11])))):
            deprel[w1[4]] = "nmod:poss"
        elif deprel[w1[4]] == "det" and w1[10] in ["NN", "PM"]:
            new_label = "nmod"
            for w2 in sentence[w1[4]:]:
#                print(str(w2[4]) + ":" + w2[7] + ":" + str(head[w2[4]]) + ":" + deprel[w2[4]])
                if head[w2[4]] == w1[4] and deprel[w2[4]] == "fixed" and re.search("GEN", w2[11]):
                    new_label = "nmod:poss"
            deprel[w1[4]] = new_label
        if w1[10] == "RG":
            if deprel[w1[4]] in ["det", "amod", "dep"]:
                deprel[w1[4]] = "nummod"
            else:
                nummod = True
                for w2 in sentence:
                    if head[w2[4]] == w1[4]:
                        nummod = False
                if nummod:
                    deprel[w1[4]] = "nummod"
        if w1[9][-2:] == "TT" and deprel[w1[4]] == "parataxis":
            deprel[w1[4]] = "vocative"
        if head[w1[4]] == 0:
            deprel[w1[4]] = "root"
        if head[w1[4]] == 0 and re.match("säga|kommentera|framhålla|påpeka|upplysa|anse|konstatera|undra|fastslå", w1[12]):
            new_head = 0
            for w2 in sentence:
#                if w1[12] == "kommentera":
#                    print("Flip parataxis: " + w2[7] + ":" + str(head[w2[4]]) + ":" + deprel[w2[4]])
                if w2[4] < w1[4] and head[w2[4]] == w1[4] and deprel[w2[4]] == "parataxis":
                    head[w2[4]] = new_head
                    if new_head == 0:
                        deprel[w2[4]] = "root"
                        new_head = w2[4]
                        head[w1[4]] = w2[4]
                        deprel[w1[4]] = "parataxis"
                        head[sentence[-1][4]] = w2[4] # Final punctuation
                    for w3 in sentence:
                        if w3[4] < w2[4] and head[w3[4]] == w1[4] and deprel[w3[4]] == "punct":
                            head[w3[4]] = new_head
    for w1 in sentence:
        if w1[7] == "som" and w1[8] == "XX" and w1[9][-2:] == "XX":
            for w2 in sentence:
                if head[w1[4]] == w2[4]:
                    for w3 in sentence:
                        if head[w3[4]] == w2[4] and w3[4] < w1[4] and not deprel[w3[4]] in ["case", "mark", "punct"]:
                            if ":" in deprel[w3[4]]:
                                real_dep = deprel[w3[4]][:deprel[w3[4]].index(":")]
                            else:
                                real_dep = deprel[w3[4]]
                            deprel[w1[4]] = real_dep
                            deprel[w3[4]] = "dislocated" # "dislocated:" + real_dep [add real_dep to misc?]
    for w1 in sentence:
        if deprel[w1[4]] == "dep":
            deprel[w1[4]] = "parataxis"
    disloc = False
    dishead = False
    for w1 in sentence:
        if not disloc and deprel[w1[4]] == "dislocated" and w1[9][-2:] == "DB":
            disloc = True
            for w2 in sentence:
                if not dishead and head[w1[4]] == w2[4]:
                    dishead = True
                    for w3 in sentence:
                        if head[w2[4]] == w3[4]:
                            head[w1[4]] = w3[4]
                            # if (w1[7] in ["så", "det"] or w1[10] in ["HP", "HD", "HS", "PN", "DT"]) and not w2[7] in ["Det", "det"]:
                            if deprel[w2[4]] == "nmod:poss":
                                real_dep = "nmod"
                            else:
                                real_dep = deprel[w2[4]]
                            if not w2[7] in ["Det", "det", "Vems"]:
                                deprel[w1[4]] = real_dep
                                deprel[w2[4]] = "dislocated" # "dislocated:" + real_dep
                                for w4 in sentence:
                                    if head[w4[4]] == w2[4] and deprel[w4[4]] == "case" and w2[4] < w4[4] and w4[4] < w1[4]:
                                        head[w4[4]] = w1[4]
                                    if head[w4[4]] == w2[4] and w4[4] > w1[4]:
                                        head[w4[4]] = w1[4]
                            else:
                                deprel[w1[4]] = "dislocated" # "dislocated:" + real_dep
    if sentence[0][0] == "P208" and sentence[0][3] == 49:
        deprel[sentence[4][4]] = "dislocated" # "dislocated:csubj"
        deprel[sentence[22][4]] = "csubj"
    if sentence[0][0] == "P210" and sentence[0][3] == 59:
        head[sentence[2][4]] = sentence[6][4]
        head[sentence[7][4]] = sentence[6][4]
        head[sentence[8][4]] = sentence[6][4]
        head[sentence[29][4]] = sentence[6][4]
        deprel[sentence[2][4]] = "dislocated"
        head[sentence[6][4]] = 0
        deprel[sentence[6][4]] = "root"
    if sentence[0][0] == "P304" and sentence[0][3] == 99:
        deprel[sentence[5][4]] = "parataxis"

def retag(sentence):
    if sentence[0][0] == "P105" and sentence[0][3] == 13:
        postag[sentence[6][4]] = "NOUN"
        postag[sentence[7][4]] = "ADJ"
    if sentence[0][0] == "P115" and sentence[0][3] == 34:
        postag[sentence[22][4]] = "NOUN"
        postag[sentence[23][4]] = "NOUN"
        head[sentence[22][4]] = 24
        head[sentence[23][4]] = 18
        deprel[sentence[22][4]] = "compound"
        deprel[sentence[23][4]] = "conj"
        for w in sentence:
            if head[w[4]] == 23:
                head[w[4]] = 24
    if sentence[0][0] == "P201" and sentence[0][3] == 109:
        postag[sentence[3][4]] = "ADJ"
        postag[sentence[4][4]] = "ADJ"
        postag[sentence[5][4]] = "NOUN"
    if sentence[0][0] == "P205" and sentence[0][3] == 2:
        postag[sentence[6][4]] = "NOUN"
        postag[sentence[7][4]] = "NOUN"
        head[sentence[6][4]] = 8
        head[sentence[7][4]] = 0
        deprel[sentence[6][4]] = "compound"
        deprel[sentence[7][4]] = "root"
        for w in sentence:
            if head[w[4]] == 7:
                head[w[4]] = 8
    if sentence[0][0] == "P207" and sentence[0][3] == 21:
        deprel[sentence[24][4]] = "conj"
    if sentence[0][0] == "P217" and sentence[0][3] == 43:
        postag[sentence[13][4]] = "NOUN"
        postag[sentence[14][4]] = "NOUN"
        head[sentence[13][4]] = 15
        head[sentence[14][4]] = 9
        deprel[sentence[13][4]] = "compound"
        deprel[sentence[14][4]] = "obj"
        for w in sentence:
            if head[w[4]] == 14:
                head[w[4]] = 15
    if sentence[0][0] == "P226" and sentence[0][3] == 21:
        postag[sentence[11][4]] = "ADJ"
        postag[sentence[12][4]] = "NOUN"
        postag[sentence[13][4]] = "ADP"
        postag[sentence[14][4]] = "NOUN"
        postag[sentence[15][4]] = "NOUN"
        deprel[sentence[12][4]] = "flat:name"
        deprel[sentence[13][4]] = "flat:name"
        deprel[sentence[14][4]] = "flat:name"
        deprel[sentence[15][4]] = "flat:name"
    if sentence[0][0] == "P301" and sentence[0][3] == 24:
        postag[sentence[22][4]] = "NOUN"
        postag[sentence[23][4]] = "NOUN"
    if sentence[0][0] == "P303" and sentence[0][3] == 81:
        postag[sentence[25][4]] = "NOUN"
        postag[sentence[26][4]] = "CCONJ"
        postag[sentence[27][4]] = "NOUN"
        postag[sentence[28][4]] = "NOUN"
        postag[sentence[29][4]] = "ADP"
        postag[sentence[30][4]] = "DET"
        postag[sentence[31][4]] = "ADJ"
        postag[sentence[32][4]] = "NOUN"
    if sentence[0][0] == "P305" and sentence[0][3] == 66:
        postag[sentence[18][4]] = "NOUN"
    if sentence[0][0] == "P305" and sentence[0][3] == 67:
        postag[sentence[2][4]] = "NOUN"
    if sentence[0][0] == "P305" and sentence[0][3] == 102:
        postag[sentence[19][4]] = "NOUN"
        features[sentence[19][4]] = "Case=Nom|Definite=Ind|Gender=Com|Number=Plur"
    if sentence[0][0] == "P309" and sentence[0][3] == 32:
        postag[sentence[18][4]] = "NOUN"
        postag[sentence[19][4]] = "NOUN"
        head[sentence[18][4]] = 20
        head[sentence[19][4]] = 17
        deprel[sentence[18][4]] = "compound"
        deprel[sentence[19][4]] = "appos"
        for w in sentence:
            if head[w[4]] == 19:
                head[w[4]] = 20
    if sentence[0][0] == "P309" and sentence[0][3] == 66:
        postag[sentence[13][4]] = "NOUN"
        postag[sentence[14][4]] = "NOUN"
        head[sentence[13][4]] = 15
        head[sentence[14][4]] = 8
        deprel[sentence[13][4]] = "compound"
        deprel[sentence[14][4]] = "obl"
        for w in sentence:
            if head[w[4]] == 14:
                head[w[4]] = 15
    if sentence[0][0] == "P313" and sentence[0][3] == 2:
        postag[sentence[5][4]] = "NOUN"
    if sentence[0][0] == "P402" and sentence[0][3] == 7:
        postag[sentence[5][4]] = "NOUN"
        postag[sentence[6][4]] = "VERB"
        postag[sentence[7][4]] = "NOUN"
        features[sentence[5][4]] = "Case=Nom|Gender=Masc|Number=Sing"
        features[sentence[6][4]] = "Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Act"
        features[sentence[7][4]] = "Case=Acc|Gender=Fem|Number=Sing"
        head[sentence[1][4]] = 5
        head[sentence[4][4]] = 9
        head[sentence[5][4]] = 7
        head[sentence[6][4]] = 5
        head[sentence[7][4]] = 7
        deprel[sentence[4][4]] = "advmod"
        deprel[sentence[5][4]] = "nsubj"
        deprel[sentence[6][4]] = "acl"
        deprel[sentence[7][4]] = "obj"
    if sentence[0][0] == "P402" and sentence[0][3] == 49:
        postag[sentence[6][4]] = "NOUN"
        postag[sentence[7][4]] = "NOUN"
        head[sentence[6][4]] = 8
        head[sentence[7][4]] = 5
        deprel[sentence[6][4]] = "compound"
        deprel[sentence[7][4]] = "nmod"
        for w in sentence:
            if head[w[4]] == 7:
                head[w[4]] = 8
    if sentence[0][0] == "P403" and sentence[0][3] == 27:
        deprel[sentence[82][4]] = "conj"
    if sentence[0][0] == "P403" and sentence[0][3] == 40:
        postag[sentence[49][4]] = "NOUN"
        postag[sentence[50][4]] = "NOUN"
    if sentence[0][0] == "P405" and sentence[0][3] == 42:
        postag[sentence[15][4]] = "ADV"
    if sentence[0][0] == "P407" and sentence[0][3] == 27:
        postag[sentence[26][4]] = "ADP"
        postag[sentence[27][4]] = "ADJ"
    for w in sentence:
        if w[10] != "_" and w[10] in ["MID", "MAD", "PAD"] and deprel[w[4]] in ["case", "cc"]:
            postag[w[4]] = "SYM"
    for w1 in sentence:
        if w1[10] != "_" and postag[w1[4]] == "VERB":
            for w2 in sentence:
                if w2[4] > w1[4] and head[w1[4]] == w2[4] and w2[9][-2:] in ["IV", "IX", "SP"] and deprel[w1[4]] == "aux" and w1[9][:-2] == w2[9][:-2]:
#                    print(w1[9] + " = " + w2[9])
                    postag[w1[4]] = "AUX"
                if head[w1[4]] == w2[4] and deprel[w1[4]] == "aux" and ((w2[9][-2:] == "SP" and w1[9][:-2] == w2[9][:-2]) or (w2[9][-4:] == "SPDT" and w1[9][:-2] == w2[9][:-4])):
                    postag[w1[4]] = "AUX"
                if head[w1[4]] == w2[4] and deprel[w1[4]] == "cop":
                    postag[w1[4]] = "AUX"
                if head[w1[4]] == w2[4] and postag[w2[4]] == "ADJ" and w2[8][-2:] == "PA" and re.match("BV", w1[8]):
                    postag[w1[4]] = "AUX"
                    postag[w2[4]] = "VERB"
                    deprel[w1[4]] = "aux:pass"
                    for w3 in sentence:
                        if head[w3[4]] == w2[4] and deprel[w3[4]] == "nsubj":
                            deprel[w3[4]] = "nsubj:pass"
                        if head[w3[4]] == w2[4] and deprel[w3[4]] == "aux":
                            postag[w3[4]] = "AUX"
    for w1 in sentence:
        if w1[10] != "_" and postag[w1[4]] == "PUNCT" and deprel[w1[4]] != "punct":
            if deprel[w1[4]] == "cc":
                postag[w1[4]] = "CCONJ"
            elif deprel[w1[4]] == "case":
                postag[w1[4]] = "ADP"
            else:
                deprel[w1[4]] = "punct"
    for w1 in sentence:
        if deprel[w1[4]] == "appos":
            for w2 in sentence[w1[4]:]:
                if head[w2[4]] == w1[4] and deprel[w2[4]] == "cc":
                    for w3 in sentence[w2[4]:]:
                        if head[w3[4]] == w1[4] and deprel[w3[4]] == "appos":
                            deprel[w3[4]] = "conj"
    for w1 in sentence:
        if deprel[w1[4]] == "mark" and postag[w1[4]] == "PRON" and w1[7] == "som":
            postag[w1[4]] = "SCONJ"
            features[w1[4]] = "_"
    for w1 in sentence:
        if deprel[w1[4]] == "case":
            for w2 in sentence[w1[4]:]:
                if head[w1[4]] == w2[4] and deprel[w2[4]] in ["csubj", "csubj:pass", "ccomp", "xcomp", "advcl", "acl", "acl:relcl"]:
                    deprel[w1[4]] = "mark"
                    for w3 in sentence[:w1[4]-1]:
                        if w3[10] != "_" and head[w3[4]] == w2[4] and not deprel[w3[4]] in ["advmod", "punct"]:
                            deprel[w1[4]] = "case"
                            break
                elif head[w1[4]] == w2[4] and deprel[w2[4]] in ["conj"]:
                    for w3 in sentence[w1[4]:w2[4]-1]:
                        if deprel[w3[4]] == "mark":
                            deprel[w1[4]] = "mark"
    for w1 in sentence:
        if deprel[w1[4]] in ["xcomp", "ccomp", "csubj", "csubj:pass", "advcl", "acl", "acl:relcl"]:
            for w2 in sentence[w1[4]:]:
                if deprel[w2[4]] == "cc" and head[w2[4]] == w1[4]:
                    for w3 in sentence[w2[4]:]:
                        if head[w3[4]] == w1[4] and deprel[w3[4]] == deprel[w1[4]]:
                            deprel[w3[4]] = "conj"

def pron_type(mamtag, lem):
    if mamtag == "XX":
        return "PronType=Rel"
    elif mamtag == "ID":
        if lem in ["annan", "någon", "samma", "två"]:
            return "PronType=Ind"
        elif lem in ["all", "allt", "varje"]:
            return "PronType=Tot"
        elif lem in ["denna"]:
            return "PronType=Dem"
        elif lem in ["som"]:
            return "PronType=Rel"
        elif lem in["vad"]:
            return "PronType=Int"
        else:
            return "PronType=Prs"
    elif mamtag[:2] == "EN":
        return "PronType=Prs"
    elif mamtag[:2] == "AB":
        return "PronType=Ind"
    elif mamtag[2:4] in ["PP", "DP", "OP", "XP"]:
        return "PronType=Prs"
    elif mamtag[2:4] == "CP":
        return "PronType=Rcp"
    elif mamtag[2:4] == "FP":
        return "PronType=Int"
    elif mamtag[2:4] == "RP":
        return "PronType=Rel"
    elif mamtag[2:4] == "TP":
        return "PronType=Tot"
    elif mamtag[2:4] == "NP":
        return "PronType=Neg"
    elif mamtag[2:4] in ["KP", "SU", "ZP"]:
        return "PronType=Ind"
    elif lem[:3] == "vad":
        return "PronType=Int"
    elif lem[:3] in ["den", "jag"] or lem[:2] in ["de", "du"]:
        return "PronType=Prs"
    else:
        return "PronType=?"

def map_features(lem, utag, mamtag, suctag, feats):
    if "_" in feats:
        feats.remove("_")
    ufeats = []
    for f in feats:
        if "/" in f:
            uf = ""
        else:
            uf = suc2ufeat[f]
        if uf != "":
            ufeats = ufeats + suc2ufeat[f]
    if "VerbForm=Fin" in ufeats and not "Mood=Imp" in ufeats and not "Mood=Sub" in ufeats:
        ufeats = ufeats + ["Mood=Ind"]
#    if suctag in ["HA", "HD", "HP", "HS"]:
#        ufeats = ufeats + ["PronType=Int,Rel"]
    if suctag in ["HS", "PS"]:
        ufeats = ufeats + ["Poss=Yes"] # Test this!
    if utag == "ADJ" and suctag == "PC" and "VerbForm=Fin" in ufeats:
        ufeats.remove("VerbForm=Fin")
        ufeats.append("VerbForm=Part")
        if "Mood=Ind" in ufeats:
            ufeats.remove("Mood=Ind")
    if utag == "VERB" and lem == "jfr":
        ufeats = ufeats + ["Mood=Imp", "VerbForm=Fin", "Voice=Act"]
    if utag == "VERB" and lem == "läsa" and ufeats == []:
        ufeats = ["VerbForm=Stem"]
    if utag in ["DET", "PRON"] and not "PronType=Int,Rel" in ufeats:
        if utag == "DET" and (lem[:2] == "en" or mamtag[:2] == "EN"):
            ufeats.append("PronType=Art")
        elif utag == "DET" and mamtag[:2] == "RO":
            ufeats.append("PronType=Tot")
        elif lem in ["denna"]:
            ufeats.append("PronType=Dem")
        else:
            ufeats.append(pron_type(mamtag, lem))
    if utag == "NUM":
        ufeats.append("NumType=Card")
    if mamtag == "ABNA":
        ufeats.append("Polarity=Neg")
    if suctag == "UO":
        ufeats.append("Foreign=Yes")
    return ufeats

def map_labels(sentence):
    for w in sentence:
        if w[10] != "_":
            if w[10] == "PL":
                postag[w[4]] = mamba2utag[w[8][:2]]
            else:
                postag[w[4]] = suc2utag[w[10]]
            if w[11] != "_" or w[8] == "ABNA" or w[10] == "UO":
                feats = w[11].split("|")
                ufeats = map_features(w[12], postag[w[4]], w[8], w[10], feats)
                ufeat_string = "|".join(sorted(ufeats, key=str.lower))
                if ufeat_string != "":
                    features[w[4]] = ufeat_string
                else:
                    features[w[4]] = "_"
            else:
                features[w[4]] = "_"
    return

def remove_dummies(sentence):  # Continue here: transfer deprel when shifting head!
    dep = {}
    for w in sentence:
        if w[10] == "_":
            nonword[w[4]] = []
            dep[w[4]] = w[9][-2:]
        if not w[4] in head:
            print("# No head for " + str(w[4]) + ":" + w[7])
            #return False
            head[w[4]] = 0
            deprel[w[4]] = "dep"
    for w in sentence:
        if head[w[4]] in nonword:
            nonword[head[w[4]]].append(w)
    # First reattach conjuncts and ++ at dummy level, then lower all other dummy dependents to clause head
    for i in sorted(nonword):
        if len(nonword[i]) > 1:
            ch = []
            found = False
            for w in nonword[i]:
                if w[4] > i and w[9][-2:] in ["FV", "IV", "IX", "SP"]:
                    ch = w
                    found = True
                    break
            if not found:   # If not found, look for first content word phrase
                for w in nonword[i]:
                    if not w[9][-2:] in ["++", "+A", "I?", "IC", "IG", "IK", "IM", "IP", "IQ", "IS", "IT", "IU", "JC", "JD", "JG", "JR", "JT", "NA", "PL", "PR", "UK", "VA", "XA", "XT"]:
                        ch = w
                        found = True
                        break
            if found and ch[9][-2:] == "DT":   # If head is DT, prefer following AT, DV or DU
                for w in nonword[i]:
                    if w[9][-2:] == "AT":
                        ch = w
                        break
                for w in nonword[i]:
                    if w[9][-2:] == "DV":
                        ch = w
                        break
                for w in nonword[i]:
                    if w[9][-2:] == "DU":
                        ch = w
                        break
            if not found:
                for w in nonword[i]:
                    if w[9][-2:] in ["+A", "VA", "XA"]:   # Hack for sentence 1726
                        ch = w
                        found = True
                        break
            if not found:
                for w in sentence[i:]:   # Crude hack!!!
                    if w[4] in head and head[w[4]] < i:
                        ch = w
                        found = True
                        break
            if found:
                for w in nonword[i]:
                    if w != ch and w[4] < i: # Reattach pre-dependents of dummy
                        head[w[4]] = ch[4]
                    elif w != ch: # and w[9][-2:] != dep[i]: # Reattach post-dependents (omit conjuncts?)
#                        print("Reattached post-dependents: " + str(w[4]))
                        head[w[4]] = ch[4]
            else:
                print("# Multiple dependents of " + str(i))
                #print(nonword[i])
    for w in sentence:
        if not w[4] in nonword:
            while head[w[4]] != 0 and head[w[4]] in nonword:
#                print(w[7] + ":" + str(head[w[4]]))
                if head[w[4]] != 0:
                    deprel[w[4]] = deprel[head[w[4]]]
                else:
                    deprel[w[4]] = "root"
                head[w[4]] = head[head[w[4]]]
    decr = 0
    decrement[0] = 0
    for w in sentence:
        if w[4] in nonword:
            decr += 1
        else:
            decrement[w[4]] = decr
    return True

def dep_label(offset, root, label, word):
    if offset == 0 and root == 0:
        return "root"
    elif label != "":
        return label
    elif word[9][-2:] in ["++", "+H"]: 
        return "cc"
    elif word[9][-2:] in ["+F", "MS"]:   # To do: Detect phrase coordination
        return "conj"
    elif word[9][-2:] in ["+A", "+B", "AA", "AB", "AC", "CA", "CB", "KA", "KB", "MA", "MB", "NA", "OA", "OB", "RA", "RB", "RC", "TA", "TB", "TC", "VA", "XA"]:   # To do: Check subtypes
        if word[5] == "D":
            return "advcl"
        elif word[10] in ["NN", "PM", "PN", "RG", "HP"] or (re.match("PO", word[8]) and not re.match("JJ|AB", word[10])):
            return "obl"
        else:
            return "advmod" 
    elif word[9][-2:] == "AG":
        if word[5] == "D":
            return "advcl"
        else:
            return "obl:agent"
    elif word[9][-2:] in ["AN", "AO"] or word[9][-4:] in ["ANSP", "ANSQ"]:
        return "appos"
    elif word[9][-2:] in ["AT", "AU", "AV", "XT", "FP"]:   # To do: Check part of speech # Add FP
        return "amod"
    elif word[9][-2:] in ["DB", "XF"]:   # Wild guess
        return "dislocated"
    elif word[9][-2:] in ["DT", "DU", "DV"]:   
        return "det"
    elif word[9][-2:] == "EF":   # Investigate cleft sentences   
        return "acl:relcl"
    elif word[9][-2:] in ["EO", "OO"]:   # Investigate logical object + ccomp vs. xcomp
        if word[5] == "D":
            if word[8] == "IF":
                return "xcomp"
            else:
                return "ccomp"
        else:
            return "obj"
    elif word[9][-2:] in ["ES", "SS"]:   # Investigate logical subject
        if word[5] == "D":
            return "csubj"
        else:
            return "nsubj"
    elif word[9][-2:] in ["ET", "EU", "EV"]:   # Investigate ET mapping
        if word[5] == "D" and word[8] == "RC":
            return "acl:relcl"
        elif word[5] == "D":
            return "acl"
        else:
            return "nmod"
    elif word[9][-2:] in ["FO", "FS"]:
        return "expl"
    elif word[9][-2:] in ["FP", "PT"]:   # Check FP -> acl [advcl?]
        return "acl"
    elif word[9][-2:] in ["FV", "IV", "IX"]:   # Note main verbs later overridden by "root", "conj", etc.
        return "aux"
    elif word[9][-2:] in ["I?", "IC", "IG", "IK", "IP", "IQ", "IR", "IS", "IT", "IU", "JC", "JD", "JG", "JR", "JT"]:
        return "punct"
    elif word[9][-2:] in ["IM", "UK"]:
        return "mark"
    elif word[9][-2:] == "IO":
        return "iobj"
#    elif word[9][-2:] == "NA":  # Changed to advmod in v2
#        return "neg" 
#    elif word[9][-2:] == "OA":
#        if word[5] == "D":
#            if word[8] == "IF":
#                return "xcomp"
#            else:
#                return "advcl" # Maybe ccomp?
#        elif word[10] in ["NN", "PN", "PM"]:
#            return "nmod"
#        else:
#            return "advmod"
    elif word[9][-2:] in ["OP", "OQ", "VO", "VS"]:
        return "xcomp"
    elif word[9][-2:] in ["SP", "SQ"]:
        if word[5] == "D":
            return "ccomp"
        else:
            return "xcomp"
    elif word[9][-2:] == "PL":
        return "compound:prt"
    elif word[9][-2:] == "PR":
        return "case"
    elif word[9][-2:] == "TT":
        return "vocative"
    elif word[9][-2:] in ["XX", "XY"]:
        return "dep"
    elif word[9][-2:] == "YY":
        return "discourse"
    elif word[8] == "PU":
        return "punct"
    elif word[9][-2:] == "GM":
        return "root"
    elif word[9][-2:] == "ST":
        return "root"
    else:
        print("# No UD mapping for " + str(word))
        return "dep"

def lex_head(words):
    mwe = True
    dep = words[0][9]
    for w in words[1:]:
        if w[9] != dep:
            mwe = False
    return mwe

def parse_sentence(sentence):
    msms = find_msms(sentence)
    build_tree(0, 0, "root", msms[0])
    h = find_head(0, msms[0])
#    print("Head: " + str(h))
#    print("Main: " + str(msms[0]))
    for m in msms[1:]:
#        print("Dep MSM: " + str(m))
        build_tree(0, h[4], "parataxis", m)

def find_msms(sentence):
    msm = {}
    msm[0] = []
    root_msm = 0
    for w in sentence:
        if w[2] != 0 and root_msm == 0:
            root_msm = int(w[2])
        if w[2] == 0 or w[2] == root_msm:
            msm[0].append(w)
        else:
            if not int(w[2]) in msm:
                msm[int(w[2])] = []
            msm[int(w[2])].append(w)
    msms = []
    for m in sorted(msm):
        msms.append(msm[m])
    return msms

def build_tree(offset, root, label, words):
#    print("Input phrase: " + str(offset) + " : " + str(root) + " : " + str(words))
    if lex_head(words):   # Lexical head [possibly MWE]
#        print("Lexical head: " + str(words))
        head[words[0][4]] = root
        deprel[words[0][4]] = dep_label(offset, root, label, words[0])
        for w in words[1:]:
            head[w[4]] = words[0][4]
            deprel[w[4]] = "fixed"
    elif words[0][9][offset:offset+2] in ["+F", "MS"]:   # Coordination; removed "GX, GM"
#        print("Main clause: " + str(words))
        head[words[0][4]] = root
        deprel[words[0][4]] = dep_label(offset, root, label, words[0])
        build_tree(offset, words[0][4], "", words[1:])
    else:   # Regular phrase [possibly subordinate clause]
        phrases = find_phrases(offset, words)
#        print("Split into phrases: " + str(phrases))
        if len(phrases) == 1:
#            print("Single phrase: " + str(phrases))
            build_tree(offset + 2, root, "", phrases[0])
        else: 
            hp = find_head_child(offset, phrases)
            build_tree(offset, root, "", hp)                 # dl -> ""
#            print("Found head child: " + str(hp))
#            print("Phrases: " + str(phrases))
            hw = find_head(root, hp)   
#            print("Found head word: " + str(hw))
            if hw[9][offset:offset+2] == "" and not hw[5] == "D":   # Ordinary headed phrase, not subclause
                hcoord = False
                pcoord = False
                pch = hw
                dch = []
#                hch = []
                dcd = ""
                deps = []
                cdeps = []
                ccs = []
                pus = []
                before_head = True
                for p in phrases:
                    if p == hp:
                        before_head = False
                        deps = []
                        dch = []
                    elif p[0][9][offset:offset+2] == "+H":
#                        print("Attached in head coordination: " + str(p))
#                        build_tree(offset + 2, pch[4], "", p)
                        hcoord = True
                        ccs.append(p)
                    elif p[0][9][offset:offset+2] == "++" or p[0][8] in ["IK++", "IS++", "IT++"]:
                        hcoord = False
#                        print("Appended cc: " + str(p))
                        ccs.append(p)
                        before_head = True
                    elif p[0][9][offset:offset+2] in ["IK", "IS", "IT"]:
                        pus.append(p)
                        before_head = True # Nice try! And it worked!
                    elif p[0][9][offset:offset+2] == hw[9][offset:offset+2]:
                        dch = [] # Reset dch for sentence 1617
                        if not hcoord:
#                            print("Attached conj to main head: " + str(p) + " " + str(hw[4]))
#                            print(ccs)
                            build_tree(offset, hw[4], "conj", p)
                            for c in ccs:
                                build_tree(offset + 2, hw[4], "", c)
#                                print("Attached cc under main head: " + str(c) + " " + str(hw[4]))
                            for c in pus:
                                build_tree(offset + 2, hw[4], "punct", c)
#                                print("Attached pu under main head: " + str(c) + " " + str(hw[4]))
                            pch = find_head(hw[4], p)
                            pcoord = True
                            for d in cdeps:
#                                print("Attached cdep under main head: " + str(p))
                                build_tree(find_offset(offset, p), pch[4], "", d) 
#                            ccs = [] # 3344
#                            cdeps = []
#                            deps = []
#                            pus = []
                        else:
#                            print("Attached conj pch: " + str(p))
                            build_tree(offset, pch[4], "conj", p)
                            for c in ccs:
#                                print("Attached cc in head coord: " + str(c) + " " + str(hw[4]))
                                build_tree(offset + 2, pch[4], "", c)
                            for c in pus:
                                if c[0][4] > pch[4]:
                                    build_tree(offset + 2, pch[4], "", c)
                            hch = find_head(hw[4], p)
                            for d in cdeps:
#                                print("Attached cdep under main head: " + str(p))
                                build_tree(find_offset(offset, p), hch[4], "", d) 
                        before_head = False
                        deps = []
                        ccs = []
                        pus = [] 
                        cdeps = []
                    elif ccs != [] and ((deps != [] and p[0][9][offset:offset+2] == deps[-1][0][9][offset:offset+2]) or dch != []):
#                        print("Attached sibling head to pch: " + str(p))
                        if dch == []:
                            build_tree(offset + 2, pch[4], "", deps[-1])
                            dch = find_head(pch[4], deps[-1])
                        tmp = []
                        for c in ccs:
                            if c[0][4] > dch[4]:
#                                print("Attach cc to sibling head: " + str(c))
                                build_tree(offset + 2, dch[4], "", c)
                                tmp.append(c)
                        for c in tmp:
                            ccs.remove(c)
#                        print("Attach conj to sibling head: " + str(p))
                        tmp = []
                        for c in pus:
                            if c[0][4] > dch[4]:
                                build_tree(offset + 2, dch[4], "punct", c)
                                tmp.append(c)
                        for c in tmp:
                            pus.remove(c)
                        build_tree(offset, dch[4], "conj", p)
                        deps = []
                        before_head = False
                    else:
                        if not p[0][9][offset:offset+2] in ["IK", "IS", "IT"]:
                            deps.append(p)
                        if pcoord or (before_head and ccs != []):
#                        if before_head and ccs != []:
                            if before_head:
                                cdeps.append(p)
                            else:
#                                print("Attached post-head dependent to pch: " + str(p))
                                build_tree(find_offset(offset, p), pch[4], "", p)
                        else:
#                            print("Attached dependent to main head: " + str(p))
                            build_tree(find_offset(offset, p), hw[4], "", p)
                for c in ccs:   # Crude hack; fix remnants
#                    print("Attached cc in hack: " + str(p))
                    build_tree(offset + 2, hw[4], "", c)
                for c in pus: 
                    build_tree(offset + 2, hw[4], "punct", c)
                for d in cdeps:
#                    print("Attached cdep in hack: " + str(p))
                    build_tree(offset + 2, hw[4], "", d)
            elif hw[9][offset:offset+2] == "" and hw[5] == "D":   # Subclause
                coord = False
                ch = hw
                before_head = True
                phrase = []
                for p in phrases:
#                    print(p)
#                    print("hw: " + str(hw))
                    if p == hp:
                        before_head = False
                    elif before_head:
                        build_tree(find_offset(offset, p), ch[4], "", p)
                    else:
                        phrase = phrase + p
#                        print("Extended phrase: " + str(phrase))
                if phrase != []:
                    build_tree(offset, ch[4], "", phrase)
            else:  # Clause
                dch = []
                dcd = ""
                deps = []
                ccs = []
                hcp = []
                hch = []
                pus = []
                for p in phrases:
                    if p == hp:
                        deps = []
                        dch = []
                    elif p[0][9][offset:offset+2] == "++" or p[0][8] in ["IK++", "IS++", "IT++"]:
#                        print("Append cc: " + str(p))
                        ccs.append(p)
                    elif p[0][9][offset:offset+2] in ["IK", "IS", "IT"]:
                        pus.append(p)
                    elif (hcp != [] or (ccs != [] and ccs[-1][0][4] > hw[4] and p[0][4] > ccs[-1][0][4])) and head_eq(p[0], hw):
                        dch = [] # Reset for sentence 1617?
                        if hcp == []:
                            hcp = find_head_child(offset, phrases[phrases.index(p):])
#                            print("Attach conj to main head: " + str(hcp))
                            build_tree(offset + 2, hw[4], "conj", hcp)
                            hch = find_head(hw[4], hcp)
                            if hcp != p and p[0][9][offset:offset+2] in ["FV", "IV", "IX"]:
#                                print("Attach auxiliary verb to current head: " + str(p))
                                build_tree(offset + 2, hch[4], "", p)
                        elif hcp != p and p[0][9][offset:offset+2] in ["FV", "IV", "IX"] and ccs == []:
#                            print("Attach auxiliary verb to current head: " + str(p))
                            build_tree(offset + 2, hch[4], "", p)
                        else:
#                            print("Attach conj to main head: " + str(p))
                            build_tree(offset + 2, hw[4], "conj", p)
                        for c in ccs:
#                            print("Attach cc to main head: " + str(c))
                            build_tree(offset + 2, hw[4], "", c)
                        for c in pus:
                            build_tree(offset + 2, hw[4], "punct", c)
                            ccs = []
                            pus = []
                    elif p[0][9][offset:offset+2] in ["+F", "MS"]:
#                        print("Attach msm as conj to main head: " + str(p))
                        build_tree(offset, hw[4], "conj", p)
                        deps = []
                    elif ccs != [] and deps != [] and (p[0][9][offset:offset+2] == deps[-1][0][9][offset:offset+2] or (head_eq(p[0], deps[-1][0]) and ccs[-1][0][4] > deps[-1][0][4])):
#                        print("Attach sibling head to main head: " + str(deps[-1]))
                        build_tree(offset + 2, hw[4], "", deps[-1])
                        dch = find_head(hw[4], deps[-1])
                        tmp = []
                        for c in ccs:
                            if c[0][4] > dch[4]:
#                                print("Attach cc to sibling head: " + str(c))
                                build_tree(offset + 2, dch[4], "", c)
                                tmp.append(c)
                        for c in tmp:
                            ccs.remove(c)
#                        print("Attach conj to sibling head: " + str(p))
                        tmp = []
                        for c in pus:
                            if c[0][4] > dch[4]:
                                build_tree(offset + 2, dch[4], "punct", c)
                                tmp.append(c)
                        for c in tmp:
                            pus.remove(c)
                        build_tree(offset, dch[4], "conj", p)
                        deps.append(p)
                    else:
                        if not p[0][9][offset:offset+2] in ["IK", "IS", "IT"]:
                            deps.append(p)
#                        print("Attach dep to main head: " + str(p))
                        build_tree(find_offset(offset, p), hw[4], "", p)
                for c in ccs:   # Crude hack; fix remnants
#                    print("Attach orphan ccs to main head: " + str(c))
                    build_tree(offset + 2, hw[4], "", c)
                for c in pus:
                    build_tree(offset + 2, hw[4], "punct", c)

def head_eq(w1, w2):
    if w1[9] == w2[9] and w1[9][-2:]:
        return True
    elif w1[9][-2:] in ["FV", "IV", "IX"] and w2[9][-2:] in ["FV", "IV", "IX"]:
        return True
    elif w1[9][-4:] in ["RAPR"] and w2[9][-2:] in ["TA"]: # Hack for sentence 642
        return True
    elif w1[9][-4:] in ["RAPR"] and w2[9][-2:] in ["TA"]: # Hack for sentence 642
        return True
    else:
        return False

def find_phrases(offset, words):
    phrases = []
    p = []
    frag_id = 0
    frag_len = 0
    for w in words:
        if p == []:
            p.append(w)
        elif frag_id > 0:
            if w[6] == "_" or int(w[6][:frag_len]) != frag_id:  # Does this work for all +F?
                frag_id = 0
                frag_len = 0
                phrases.append(p)
                p = []
            p.append(w)
        else:
            if w[9][offset:offset+2] != p[-1][9][offset:offset+2] or w[4] > p[-1][4] + 1:
                phrases.append(p)
                p = []
            p.append(w)
        if w[9][offset:offset+2] == "+F":
            frag_len = 1
#            print("+F dummy: " + w[7][frag_len] + ":" + w[7])
            while frag_len < 4 and w[7][frag_len] != "0":
                frag_len += 1
            frag_id = int(w[7][:frag_len])
    if p != []:
        phrases.append(p)
    phrases = find_discontiguous(offset, phrases) # ADDED
    return phrases

def find_discontiguous(offset, phrases): # ADDED
    deps = []
    ps = []
    cc = -1
    for p in phrases:
        d = p[0][9][offset:offset+2]
        if d in ["++", "+H", "IP", "IQ"] or p[0][8][:4] in ["IK++", "IS++", "IT++"]: # IP = hack for sentence 401
            cc = len(deps)
            deps.append(d)
            ps.append(p)
        elif d in deps and not d in ["", "ST", "+F", "I?", "IC", "IG", "IK", "IP", "IQ", "IR", "IS", "IT", "IU", "JC", "JD", "JG", "JR", "JT"] and p[0][2] == ps[deps.index(d)][0][2] and (p[0][6] == ps[deps.index(d)][0][6] or p[0][6][:4] == ps[deps.index(d)][0][7]) and not ps[deps.index(d)][0][9] in ["SSMS", "OOMS"]: 
            if cc > deps.index(d):
                deps.append("++")
                ps.append(p)
            else:
                i = deps.index(d)
                pp = ps[i] + p
                ps.remove(ps[i])
                ps.insert(i, pp)
        else:
            deps.append(d)
            ps.append(p)
    return ps
        
def find_head_child(offset, phrases):
    ch = phrases[0]
    verb = False
    found = False
    for p in phrases:
        if p[0][9][offset:] == "":  # If headed phrase, return first head [may contain conjuncts]
            return p
    for dep in ["FV", "IV", "IX"]:   # Else try to find main verb (but don't go beyond cc)
        for p in phrases:
            if p[0][9][offset:offset+2] == dep:
                #print("Found verb: " + str(p))
                ch = p
                verb = True
            elif verb and p[0][4] > ch[0][4] and (p[0][9][offset:offset+2] in ["++", "+H"] or p[0][8] in ["IK++", "IS++", "IT++"]):
                #print("Breaks for " + str(p))
                break
    if verb:   # If found main verb, look for complement of copula "vara" (still don't go beyond cc)
        for p in phrases:
            if p[0][9][offset:offset+2] == "SP" and p[0][5] != "D": 
                if re.match("AV", ch[0][8]):
                    ch = p
                elif re.match("BV", ch[0][8]):
                    ps = find_phrases(offset+2, p)
                    hch = find_head_child(offset+2, ps)
                    if hch[0][8][-2:] == "PA":
                        ch = p
            elif p[0][4] > ch[0][4] and p[0][9][offset:offset+2] in ["++", "+H"]:
                break
        return ch
    else:   # Else look for predicative complement
        for p in phrases:
            if p[0][9][offset:offset+2] == "SP":
                return p
        for p in phrases:
            if p[0][9][offset:offset+2] == "XX":
                return p
        for p in phrases:
            if not p[0][9][offset:offset+2] in ["++", "+H", "+A", "CA", "MA", "I?", "IC", "IG", "IK", "IM", "IP", "IQ", "IS", "IT", "IU", "JC", "JD", "JG", "JR", "JT", "NA", "PL", "PR", "UK", "VA", "XA", "XT", "GM", "GX", "MS", "+F"]:
                found = True
                ch = p
                break
        if ch[0][9][offset:offset+2] == "DT":   # If head is DT, prefer following AT
            for p in phrases:
                if p[0][9][offset:offset+2] == "AT":
                    ch = p
                    return ch
            for p in phrases:
                if p[0][9][offset:offset+2] == "DV":
                    ch = p
                    return ch
            for p in phrases:
                if p[0][9][offset:offset+2] == "DU":
                    ch = p
                    return ch
        if not found:
            for p in phrases:
                if p[0][9][offset:offset+2] in ["+A", "VA", "XA"]:
                    ch = p
                    break
    return ch

def find_head(root, p):
    for w in p:
        if w[4] in head and head[w[4]] == root:
            return w
    return p[0]

def find_offset(o, hc):
    if hc[0][9][o:o+2] in ["+F", "MS"] or hc[0][5] == "D":
        return o
    else:
        return o + 2

header = []
sentence = []
dummy = []
current_sid = 0
mydoc = ""
mypar = 0
mysid = 0
mytid = 0
head = {}
deprel = {}
postag = {}
features = {}
nonword = {}
decrement = {}
misc = {}
discontiguous = False
parbreak = False

suc2utag = {
    "AB": "ADV",
    "DT": "DET",
    "HA": "ADV",
    "HD": "DET",
    "HP": "PRON",
    "HS": "DET",
    "IE": "PART",
    "IN": "INTJ",
    "JJ": "ADJ",
    "KN": "CCONJ",
    "NN": "NOUN",
    "PC": "ADJ",
    "PL": "ADP", # Fix!
    "PM": "PROPN",
    "PN": "PRON",
    "PP": "ADP",
    "PS": "DET",
    "RG": "NUM",
    "RO": "ADJ",
    "SN": "SCONJ",
    "VB": "VERB", # Fix!
    "UO": "X",
    "MAD": "PUNCT",
    "MID": "PUNCT",
    "PAD": "PUNCT"
}

mamba2utag = {
    "AB": "ADV",
    "ID": "ADV",
    "NN": "NOUN",
    "PR": "ADP"
}
suc2ufeat = {
    "AKT": ["Voice=Act"],
    "DEF": ["Definite=Def"],
    "GEN": ["Case=Gen"],
    "IND": ["Definite=Ind"],
    "INF": ["VerbForm=Inf"],
    "IMP": ["VerbForm=Fin", "Mood=Imp"],
    "KOM": ["Degree=Cmp"],
    "KON": ["Mood=Sub"],
    "NEU": ["Gender=Neut"],
    "NOM": ["Case=Nom"],
    "MAS": ["Gender=Masc"],
    "OBJ": ["Case=Acc"],
    "PLU": ["Number=Plur"],
    "POS": ["Degree=Pos"],
    "PRF": ["VerbForm=Part", "Tense=Past"],
    "PRT": ["VerbForm=Fin", "Tense=Past"],
    "PRS": ["VerbForm=Fin", "Tense=Pres"],
    "SFO": ["Voice=Pass"],
    "SIN": ["Number=Sing"],
    "SMS": [],
    "SUB": ["Case=Nom"],
    "SUP": ["VerbForm=Sup"],
    "SUV": ["Degree=Sup"],
    "UTR": ["Gender=Com"],
    "AN": ["Abbr=Yes"],
    "-": []
}

for line in sys.stdin:
    (idx, dum, tok, pos, syn, sid, cat, suc, fea, lem) = line.strip().split("\t")
    doc = idx[0:4]
    par = int(idx[4:6])
    msm = int(idx[6:9])
    sid = int(sid)
    tid = int(idx[9:12])
    # v2: remove underscore
    if "_" in tok:
        tok = tok.replace("_", " ")
        lem = lem.replace("_", " ")
    # v2: remove underscore
    if sid == 0:
        if sentence != []:
            print_sentence(sentence)
            sentence = []
            dummy = []
        header.append((doc, par, msm, sid, tid, cat, dum, tok, pos, syn, suc, fea, lem))
        if syn == "TX":
            mydoc = doc
            mypar = 0
            mysid = 0
        elif re.search("ST$", syn) or pos == "ST": # Annotation error?
            mypar += 1
        check_index("doc", doc, mydoc)
        check_index("par", par, mypar)
        check_index("sid", sid, 0)
        check_index("tid", tid, 0)
    else:
        if sid != current_sid:
            if header != []:
                print_header(header)
                header = []
            if sentence != []:
                print_sentence(sentence)
                sentence = []
                dummy = []
            mytid = 0
            current_sid = sid
            head = {}
            deprel = {}
            postag = {}
            features = {}
            nonword = {}
            decrement = {}
            misc = {}
        mytid += 1
        if re.search("GM$", syn) and tok == "0000":
            syn = "GM"   # Single change
            mysid += 1
        elif re.search("GX$", syn):
            mysid += 1
        elif re.search("ST$", syn) or pos == "ST": # Annotation error?
            mypar += 1
        check_index("doc", doc, mydoc)
        check_index("par", par, mypar)
        check_index("sid", sid, mysid)
        check_index("tid", tid, mytid)
        if dum != "_":
            for d in dummy:
                if dum[0:4] == d[0] and msm == d[2]:
                    if len(dum) == 4:
                        i = 0
                    else:
                        i = 2 * int(dum[4])
                    syn = d[1][0:i] + syn
        if re.match("\d{4}", tok) and pos != "RO":  # Hack! 
            dummy.append((tok, syn, msm))
        if syn[-4:] == "  ++":
            syn = syn[:-4] + "+H"
        syn = syn.replace("  ", "")
        sentence.append((doc, par, msm, sid, tid, cat, dum, tok, pos, syn, suc, fea, lem))

if sentence != []:
    print_sentence(sentence)
