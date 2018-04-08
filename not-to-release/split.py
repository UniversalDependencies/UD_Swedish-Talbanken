import re, sys

output = "train"
sentence = []

train_file = open(sys.argv[2] + "-train.conllu", "w")
dev_file = open(sys.argv[2] + "-dev.conllu", "w")
test_file = open(sys.argv[2] + "-test.conllu", "w")

def print_sentence(file, sentence):
    for line in sentence:
        file.write(line)
    file.write("\n")

sent_counter = 0

print("Writing to {}-[train|dev|test].conllu".format(sys.argv[2]))

savein = sys.stdin
fin = open(sys.argv[1])
sys.stdin = fin

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
        sent_counter = sent_counter + 1

train_file.close()
test_file.close()
dev_file.close()

sys.stdin = savein
fin.close()

print("Wrote {} sentences".format(sent_counter))
