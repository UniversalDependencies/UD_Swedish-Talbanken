import sys, re

def print_sentence(sent):
    for w in sent:
        print("\t".join(w))
    print()

def switch_features(f1, f2, feats):
    feat_list = feats.split("|")
    feat_list[feat_list.index(f1)] = f2
    return "|".join(feat_list)

def pron_type_dem(feats):
    old_feat_list = feats.split("|")
    new_feat_list = []
    found = False
    for feat in old_feat_list:
        (f, v) = feat.split("=")
        if f == "PronType":
            new_feat = "=".join([f, "Dem"])
            new_feat_list.append(new_feat)
            found = True
        else:
            new_feat_list.append(feat)
    if not found:
        new_feat_list.append("PronType=Dem")
        new_feat_list.sort(key=str.casefold)
    return "|".join(new_feat_list)

def get_pron_type(lem, pos):
    if pos == "PRON":
        if lem in ["jag", "du", "han", "hon", "man", "den", "det", "en", "sig", "vi", "ni", "de"]:
            return "Prs"
        elif lem in ["all", "alltihop", "alltsammans", "båda"]:
            return "Tot"
        elif lem in ["annan", "många", "någon"]:
            return "Ind"
        elif lem in ["denna"]:
            return "Dem"
        elif lem in ["ingen", "intet"]:
            return "Neg"
        elif lem in ["varandra"]:
            return "Rcp"
        else:
            return "Nil"
    if pos == "DET": 
        if lem in ["den", "en", "de"]:
            return "Art"
        elif lem in ["all", "båda", "varje"]:
            return "Tot"
        elif lem in ["någon"]:
            return "Ind"
        elif lem in ["denna"]:
            return "Dem"
        elif lem in ["ingen"]:
            return "Neg"
        else:
            return "Nil"
    return "None"

def pron_type(lem, pos, feats):
    feat_list = feats.split("|")
    val = get_pron_type(lem, pos)
    feat_list.append("PronType=" + val)
    feat_list.sort(key=str.casefold)
    return "|".join(feat_list)

def fix_pronouns(sent):
    for w in sent:
        if w[3] in ["DET", "PRON"]:
            if not re.search("PronType", w[5]):
            	w[5] = pron_type(w[2], w[3], w[5])
    print_sentence(sent)

print("Writing to {}".format(sys.argv[2]))

savein = sys.stdin
fin = open(sys.argv[1])
sys.stdin = fin

saveout = sys.stdout
fout = open(sys.argv[2], 'w')
sys.stdout = fout

sent_counter = 0
sent_id = ""
sent = []

for line in sys.stdin:
    newline = True
    if re.match("^#", line):
        if re.match("^# sent_id", line):
            list = line.strip().split()
            sent_id = list[3]
        print(line.strip())
    elif line.strip():
        cols = line.strip().split("\t")
        sent.append(cols)
    elif sent:
        fix_pronouns(sent)
        sent_counter = sent_counter + 1
        sent_id = ""
        sent = []

sys.stdin = savein
fin.close()
sys.stdout = saveout
fout.close()

print("Wrote {} sentences".format(sent_counter))
