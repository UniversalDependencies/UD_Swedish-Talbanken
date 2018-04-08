import re, sys

output = "train"
doc = 0

train_id = 1
dev_id = 1
test_id = 1

sentence = []
new_sen = True
new_doc = ""
new_par = ""
new_par_sen = False

def insert_new_par(line):
    cols = line.strip().split("\t")
    if cols[9] == "_":
        cols[9] = "NewPar=Yes"
    else:
        col9 = cols[9].split("|")
        col9.append("NewPar=Yes")
        cols[9] = "|".join(sorted(col9))
    return "\t".join(cols)
              
def sent_id(filename, id):
    return "# sent_id = sv-ud-" + filename + "-" + str(id)

def text(sentence):
    tokens = []
    for line in sentence:
        columns = line.split("\t")
        tokens.append(columns)
    string = []
    for t in tokens:
        string.append(t[1])
        if not "SpaceAfter=No" in t[9].strip().split("|"):
            string.append(" ")
    return "# text = " + "".join(string).strip()

def print_sentence(id, new_doc, new_par, sentence):
    if new_doc != "":
        print("# newdoc id = " + new_doc)
    if new_par != "":
        print("# newpar id = " + new_par)
    print(id)
    print(text(sentence))
    for line in sentence:
        print(line)
    print()

sent_counter = 0

print("Writing to {}".format(sys.argv[2]))

savein = sys.stdin
fin = open(sys.argv[1])
sys.stdin = fin

saveout = sys.stdout
fout = open(sys.argv[2], 'w')
sys.stdout = fout

for line in sys.stdin:
    if re.match("^#", line):
        m = re.match("#\tP(\d{3})\.(\d+)", line)
        if m:
            if int(m.group(1)) != doc:
                doc = int(m.group(1))
                new_doc = "P" + m.group(1)
            if int(m.group(2)) > 0:
                if new_sen:
                    new_par = "P" + m.group(1) + "." + m.group(2)
                else:
                    new_par_sen = True
    elif line.strip():
        if new_par_sen:
            line = insert_new_par(line)
            new_par_sen = False
        sentence.append(line.strip())
        new_sen = False
    elif doc in [108, 110, 114, 122, 204, 210, 213, 214, 218, 301, 307, 311, 412, 415, 416]:
        print_sentence(sent_id("test", test_id), new_doc, new_par, sentence)
        sent_counter = sent_counter + 1
        test_id = test_id + 1
        sentence = []
        new_sen = True
        new_par = ""
        new_doc = ""
    elif doc in [408, 409, 410, 411, 413, 414, 417, 418]:
        print_sentence(sent_id("dev", dev_id), new_doc, new_par, sentence)
        sent_counter = sent_counter + 1
        dev_id = dev_id + 1
        sentence = []
        new_sen = True
        new_par = ""
        new_doc = ""
    else:
        print_sentence(sent_id("train", train_id), new_doc, new_par, sentence)
        sent_counter = sent_counter + 1
        train_id = train_id + 1
        sentence = []
        new_sen = True
        new_par = ""
        new_doc = ""

sys.stdin = savein
fin.close()
sys.stdout = saveout
fout.close()

print("Wrote {} sentences".format(sent_counter))


