import re, sys

output = "train"
doc = 0
new_doc = False

train_file = open("sv-ud-train-v2.conllu", "w")
dev_file = open("sv-ud-dev-v2.conllu", "w")
test_file = open("sv-ud-test-v2.conllu", "w")
space_file = open("tokens-with-spaces.txt", "w")

train_id = 1
dev_id = 1
test_id = 1

sentence = []
space_tokens = []

def sent_id(filename, id):
    return "# sent_id = " + filename + "-s" + str(id) + "/sv\n"

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
        if t[9].strip() == "_":
            string.append(" ")
    return "# text = " + "".join(string).strip() + "\n"

def print_sentence(file, id, sentence):
    file.write(id)
    file.write(text(sentence))
    for line in sentence:
        file.write(line)
    file.write("\n")

for line in sys.stdin:
    if re.match("^#", line):
        m = re.match("#\tP(\d{3})", line)
        if m and int(m.group(1)) != doc:
            doc = int(m.group(1))
    elif line.strip():
        sentence.append(line)
    elif doc in [108, 110, 114, 122, 204, 210, 213, 214, 218, 301, 307, 311, 412, 415, 416]:
        print_sentence(test_file, sent_id("test", test_id), sentence)
        test_id = test_id + 1
        sentence = []
    elif doc in [408, 409, 410, 411, 413, 414, 417, 418]:
        print_sentence(dev_file, sent_id("dev", dev_id), sentence)
        dev_id = dev_id + 1
        sentence = []
    else:
        print_sentence(train_file, sent_id("train", train_id), sentence)
        train_id = train_id + 1
        sentence = []

for tok in sorted(set(space_tokens), key=str.lower):
    space_file.write(tok + "\n")

train_file.close()
test_file.close()
dev_file.close()
space_file.close()

