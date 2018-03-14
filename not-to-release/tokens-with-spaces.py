import re, sys

space_tokens = []

print("Writing to {}".format(sys.argv[2]))

savein = sys.stdin
fin = open(sys.argv[1])
sys.stdin = fin

saveout = sys.stdout
fout = open(sys.argv[2], 'w')
sys.stdout = fout

for line in sys.stdin:
    if line.strip() and not line.startswith("#"):
        columns = line.strip().split("\t")
        if " " in columns[1]:
            space_tokens.append(columns[1])

for tok in sorted(set(space_tokens), key=str.lower):
    print(tok)

sys.stdin = savein
fin.close()
sys.stdout = saveout
fout.close()

print("Wrote {} tokens".format(len(set(space_tokens))))
