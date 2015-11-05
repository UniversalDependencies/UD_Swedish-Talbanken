import re, sys

output = "train"
doc = 0

train_file = open("sv-ud-train.conllu", "w")
dev_file = open("sv-ud-dev.conllu", "w")
test_file = open("sv-ud-test.conllu", "w")

for line in sys.stdin:
    if re.match("^#", line):
        m = re.match("#\tP(\d{3})", line)
        if m and int(m.group(1)) != doc:
            doc = int(m.group(1))
    elif doc in [108, 110, 114, 122, 204, 210, 213, 214, 218, 301, 307, 311, 412, 415, 416]:
        test_file.write(line)
    elif doc in [408, 409, 410, 411, 413, 414, 417, 418]:
        dev_file.write(line)
    else:
        train_file.write(line)
