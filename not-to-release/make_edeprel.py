import sys

edeprel = []

print("Writing to {}".format(sys.argv[2]))

savein = sys.stdin
fin = open(sys.argv[1])
sys.stdin = fin

saveout = sys.stdout
fout = open(sys.argv[2], 'w')
sys.stdout = fout

for line in sys.stdin:
    if line.strip() and not line.startswith("#"):
        cols = line.strip().split("\t")
        for edep in cols[8].split("|"):
            parts = edep.split(":")
            if len(parts) > 2:
                edeprel.append(":".join(parts[1:]))

for rel in sorted(set(edeprel)):
    print(rel)

sys.stdin = savein
fin.close()
sys.stdout = saveout
fout.close()

print("Wrote {} tokens".format(len(set(edeprel))))
