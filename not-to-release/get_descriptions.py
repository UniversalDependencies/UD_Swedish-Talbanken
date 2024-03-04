from collections import defaultdict, Counter
import sys, re

# 0: ID, 1: FORM, 2: LEMMA, 3: UPOS, 4: XPOS, 5: FEATS, 6: HEAD, 7: DEPREL, 8: ENHANCED-DEPS, 9: MISC

def get_descriptions (path, tokenlist):
    ''' returns a dictionary of alternative feature descriptions for a list of tokens '''
    result = defaultdict()
    udfile = path
    with open(udfile, "r") as u:
        for line in u:    
            if re.match(r'\d', line):
                info = line.split('\t')
                # compute the result as lemma_upos_feats
                entry = info[1].lower()
                if entry in tokenlist:
                    descr = info[1] + ', Lemma=' + info[2] + ', UPOS=' + info[3] + ', FEATS=' + info[5]
                    try:
                        result[entry][descr] += 1
                    except:
                        try:
                            result[entry][descr] = 1
                        except:
                            result[entry] = Counter()
                            result[entry][descr] = 1
    return result

if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[-1].endswith('.txt'):
            with open(sys.argv[-1], 'r') as f:
                tokens = [token.strip() for line in f.readlines() for token in line.split()]
        else:
            tokens = [token.strip() for token in sys.argv[1:]]
    else:
        tokens = [token.strip() for token in sys.argv[1:]]

    udfile = sys.argv[1]

    descrs = get_descriptions(udfile, tokens)

    descrs
    for wrd in descrs:
        print()
        for desc in descrs[wrd].most_common():
            print(desc[0], desc[1])