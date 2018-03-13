import re, sys

output = "train"
sentence = []

train_file = open("sv_talbanken-ud-train.conllu", "w")
dev_file = open("sv_talbanken-ud-dev.conllu", "w")
test_file = open("sv_talbanken-ud-test.conllu", "w")

def print_sentence(file, sentence):
    for line in sentence:
        file.write(line)
    file.write("\n")

for line in sys.stdin:
    if re.match("^# sent_id", line):
        if "test" in line:
            output = "test"
        elif "dev" in line:
            output = "dev"
        else:
            output = "train"
    if line.strip():
        sentence.append(line)
    else:
        if output == "test":
            print_sentence(test_file, sentence)
        elif output == "dev":
            print_sentence(dev_file, sentence)
        else:
            print_sentence(train_file, sentence)
        sentence = []

train_file.close()
test_file.close()
dev_file.close()

