import sys, re

def split_enhanced(deps):
    pairs = deps.split("|")
    
def process_sentence(sent_id, sent):
    for word in sent:
        cols = word.split("\t")
        basic = [cols[6] + ":" + cols[7]]
        enhanced = cols[8].split("|")
        if basic != enhanced:
            print(sent_id + "\t" + cols[0] + "\t" + "|".join(enhanced))

sent_counter = 0

print("Writing to {}".format(sys.argv[3]))

savein = sys.stdin
fin = open(sys.argv[1])
sys.stdin = fin

enhanced = {}
null = {}

for line in sys.stdin:
#    (sent, word, deps) = line.strip().split("\t")
    cols = line.strip().split("\t")
    if len(cols) > 3:
        id = cols[1].split(".")
        if not (cols[0], id[0]) in null.keys():
            null[cols[0], id[0]] = []
        token = "\t".join(cols[2:])
        null[cols[0], id[0]].append(token)
    else:
        enhanced[cols[0], cols[1]] = cols[2]

sys.stdin = savein
fin.close()

savein = sys.stdin
fin = open(sys.argv[2])
sys.stdin = fin

saveout = sys.stdout
fout = open(sys.argv[3], 'w')
sys.stdout = fout

sent_id = ""

for line in sys.stdin:
    if re.match("^# sent_id", line):
        list = line.strip().split()
        sent_id = list[3]
        print(line.strip())
    elif line.strip():
        if re.match("^#", line):
            print(line.strip())
        else:
            cols = line.strip().split("\t")
            if (sent_id, cols[0]) in enhanced.keys():
                cols[8] = enhanced[sent_id, cols[0]]
            else:
                cols[8] = cols[6] + ":" + cols[7]
            print("\t".join(cols))
            if (sent_id, cols[0]) in null.keys():
                for tok in null[sent_id, cols[0]]:
                    print(tok)
    else:
        print(line.strip())
        sent_counter = sent_counter + 1
        sent_id = ""

sys.stdin = savein
fin.close()
sys.stdout = saveout
fout.close()

print("Wrote {} sentences".format(sent_counter))
