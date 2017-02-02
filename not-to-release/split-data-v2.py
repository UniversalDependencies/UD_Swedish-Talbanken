import re, sys

output = "train"
doc = 0

train_file = open("sv-ud-train-v2.conllu", "w")
dev_file = open("sv-ud-dev-v2.conllu", "w")
test_file = open("sv-ud-test-v2.conllu", "w")
space_file = open("tokens-with-spaces.txt", "w")

train_id = 1
dev_id = 1
test_id = 1

sentence = []
space_tokens = []
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
    return "\t".join(cols) + "\n"
              
def sent_id(filename, id):
    return "# sent_id = sv-ud-" + filename + "-" + str(id) + "\n"

def text(sentence):
    tokens = []
    for line in sentence:
        columns = line.split("\t")
        tokens.append(columns)
        if " " in columns[1]:
            space_tokens.append(columns[1])
    string = []
    for t in tokens:
        string.append(t[1])
        if not "SpaceAfter=No" in t[9].strip().split("|"):
            string.append(" ")
    return "# text = " + "".join(string).strip() + "\n"

def print_sentence(file, id, new_doc, new_par, sentence):
    if new_doc != "":
        file.write("# new_doc id = " + new_doc + "\n")
    if new_par != "":
        file.write("# new_par id = " + new_par + "\n")
    file.write(id)
    file.write(text(sentence))
    for line in sentence:
        file.write(line)
    file.write("\n")

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
        sentence.append(line)
        new_sen = False
    elif doc in [108, 110, 114, 122, 204, 210, 213, 214, 218, 301, 307, 311, 412, 415, 416]:
        print_sentence(test_file, sent_id("test", test_id), new_doc, new_par, sentence)
        test_id = test_id + 1
        sentence = []
        new_sen = True
        new_par = ""
        new_doc = ""
    elif doc in [408, 409, 410, 411, 413, 414, 417, 418]:
        print_sentence(dev_file, sent_id("dev", dev_id), new_doc, new_par, sentence)
        dev_id = dev_id + 1
        sentence = []
        new_sen = True
        new_par = ""
        new_doc = ""
    else:
        print_sentence(train_file, sent_id("train", train_id), new_doc, new_par, sentence)
        train_id = train_id + 1
        sentence = []
        new_sen = True
        new_par = ""
        new_doc = ""

for tok in sorted(set(space_tokens), key=str.lower):
    space_file.write(tok + "\n")

train_file.close()
test_file.close()
dev_file.close()
space_file.close()

