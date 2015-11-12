import sys

for line in sys.stdin:
    if line.strip() and not line.strip()[0] == "#":
        columns = line.strip().split("\t")
        feats = columns[5].split("|")
        if columns[3] == "ADJ" and columns[4][:2] == "PC" and "VerbForm=Fin" in feats:
            feats.remove("VerbForm=Fin")
            feats.append("VerbForm=Part")
            if "Mood=Ind" in feats:
                feats.remove("Mood=Ind")
        elif columns[3] == "VERB" and columns[2][-1] == "s" and "Voice=Pass" in feats:
            feats.remove("Voice=Pass")
        columns = columns[0:5] + ["|".join(sorted(feats))] + columns[6:]
        print("\t".join(columns))
    else:
        print(line.strip())
