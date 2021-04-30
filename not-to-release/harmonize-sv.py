import re, sys

# Simple class to store non-comment lines of a Conll file
class ConllEntry:
    def __init__(self, id, form, lemma, cpos, pos, feats=None, parent_id=None, relation=None, deps=None, misc=None):
        self.id = id
        self.form = form
        self.cpos = cpos
        self.pos = pos
        self.parent_id = parent_id
        self.relation = relation

        self.lemma = lemma
        self.feats = feats
        self.deps = deps
        self.misc = misc

    # determines what output looks like when we print or call str() 
    # tab-separated in same format as original ConllU file
    def __str__(self):
        values = [str(self.id), self.form, self.lemma, self.cpos, 
            self.pos, self.feats, str(self.parent_id), self.relation, 
            self.deps, self.misc]
        return '\t'.join(['_' if v is None else v for v in values])

# read in a conll file and store a list of sentences
def read_conll(filename):
    with open(filename,'r') as fh: 
        print("Reading {}".format(filename))
        sent_counter = 0
        sents = [] # list of sentences
        tokens = [] # list of tokens (one of these per sentence)
        for line in fh:
            tok = line.strip().split('\t')
            if not tok or line.strip() == '' and len(tokens)>0: # at the end of a sentence - append current token list to sents
                sent_counter += 1
                sents.append(tokens)
                tokens = []
            else:
                if line[0] == '#' or '-' in tok[0] or '.' in tok[0]: # a comment line
                    tokens.append(line.strip())
                else: # a regular line tab-separated line - create a ConllEntry to hold the information
                    tokens.append(ConllEntry(int(tok[0]), tok[1], tok[2], tok[3], tok[4], tok[5], int(tok[6]) if tok[6] != '_' else -1, tok[7], tok[8], tok[9]))

    print("Read {} sentences".format(sent_counter))
    return sents

# write sentences to a conll file
def write_conll(filename, sents):
    print("Writing to {}".format(filename))
    sent_counter = 0
    with open(filename, 'w') as fh:
        for sent in sents:
            sent_counter += 1
            for entry in sent:
                fh.write(str(entry) + '\n')
            fh.write('\n')
        print("Wrote {} sentences".format(sent_counter))

if __name__ == "__main__":

    sents = read_conll(sys.argv[1])

    for sent in sents:

        conll_entries = [entry for entry in sent if isinstance(entry,ConllEntry)]
        for entry in conll_entries:
            # 1. Possessiva pronomen
            if entry.cpos == "DET" and "Poss=Yes" in entry.feats:
                entry.cpos = "PRON" 
            # 3. Negation
            if re.search(r'^(inte|icke|ej)$',entry.lemma) and entry.cpos == "ADV":
                entry.cpos = "PART"
            # 5. Konjunktionerna "än" och "som"
            if entry.lemma == "som" and entry.relation == "mark":
                if entry.cpos == "CCONJ":
                    entry.cpos = "SCONJ"
                if entry.cpos == "ADV":
                    entry.cpos = "SCONJ"
                    entry.feats = "_" # removes PronType=Int,Rel
            if entry.lemma == "än" and entry.cpos == "CCONJ":
                if re.search(r'^(mark|fixed)$',entry.relation):
                    entry.cpos = "SCONJ"
                if entry.relation == "advmod":
                    entry.cpos = "ADV"
            # New: Konjunktionerna "både", "varken", "vare sig", "antingen"
            if entry.lemma in ["både", "varken", "vare", "antingen"] and entry.cpos == "CCONJ" and entry.relation == "advmod":
                entry.relation = "cc"
        # X -advcl-> Y (NOUN) -mark-> "som|än" + !(Y <-cop|nsubj- Z) -->
        # X -obl-> Y (NOUN) -case-> "som|än" (ADP) 
        for entry in conll_entries:
            if re.search(r'^(som|än)$',entry.lemma) and entry.relation == "mark":
                som = entry
                parent = conll_entries[entry.parent_id - 1]
                if re.search(r'^(NOUN|PROPN|PRON)$',parent.cpos) and parent.relation == "advcl":
                    cop_dep = None # actually cop or nsubj
                    for entry in conll_entries:
                        if entry.parent_id == parent.id and re.search(r'^(cop|nsubj)$',entry.relation):
                            cop_dep = entry
                            break
                    if not cop_dep:
                        som.relation = "case"
                        som.cpos = "ADP"
                        parent.relation = "obl"

        # X <-expl- "vara" -dislocated-> Y -acl:relcl-> Z -->
        # X <-expl- Y -acl:cleft-> Z + "vara" <-cop- Y
        for entry in conll_entries:
            if entry.lemma == "vara":
                vara = entry
                # look for dependents of entry with relations expl and dislocated
                expl_dep = None 
                disloc_dep = None 
                for entry in conll_entries:
                    if entry.parent_id == vara.id: # a dependent of entry
                        if entry.relation == "expl":
                            expl_dep = entry
                        if entry.relation == "dislocated":
                            disloc_dep = entry
                if expl_dep and disloc_dep:
                    aclrelcl_dep = None # look for dependent of dislocated dependent with relation acl:relcl
                    for entry in conll_entries:
                        if entry.parent_id == disloc_dep.id and entry.relation == "acl:relcl":
                            aclrelcl_dep = entry
                if expl_dep and disloc_dep and aclrelcl_dep: # if we found everything make the changes
                    disloc_dep.parent_id = vara.parent_id 
                    disloc_dep.relation = vara.relation
                    vara.parent_id = disloc_dep.id
                    vara.relation = "cop"
                    vara.cpos = "AUX"
                    aclrelcl_dep.relation = "acl:cleft"
                    for entry in conll_entries:
                        if entry.parent_id == vara.id:
                            entry.parent_id = disloc_dep.id

        # "när|då" <-mark|advmod- X <-advcl- Y
        # Om DEPREL = advmod, ändra till mark.
        # Om POSTAG = ADV, ändra till SCONJ.
        for entry in conll_entries:
            if re.search(r'^(när|då)$',entry.lemma) and re.search(r'^(mark|advmod)$',entry.relation):
                parent = conll_entries[entry.parent_id - 1]
                if parent.relation == "advcl":
                    entry.relation = "mark"
                    if entry.cpos == "ADV":
                        entry.cpos = "SCONJ"

        # Hack for latin words
        for entry in conll_entries:
            if re.search(r'^(consensus|facit|nuptiam)$',entry.lemma):
                entry.misc = "Lang=la"
                
    write_conll(sys.argv[2],sents)
    
