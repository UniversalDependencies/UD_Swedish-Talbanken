import re
from collections import defaultdict

class Token():
    def __init__(self, info, sent_id=None, sent=None) -> None:
        self.sent_id = sent_id
        self.sent = sent
        self.convert_info_to_attr(info)
                
    def convert_info_to_attr(self, info):
        # 0: ID, 1: FORM, 2: LEMMA, 3: UPOS, 4: XPOS, 5: FEATS, 6: HEAD, 7: DEPREL, 8: ENHANCED-DEPS, 9: MISC
        self.sent_pos = info[0]

        self.form = info[1] if info[1] != '_' else None
        self.lemma = info[2] if info[2] != '_' else None
        self.upos = info[3] if info[3] != '_' else None
        self.xpos = info[4] if info[4] != '_' else None

        self.feats = {}
        if info[5] != '_':
            feats = [tuple(feat.split('=')) for feat in info[5].split('|')]
            self.feats = {key: value for key, value in feats} 

        self.head = info[6] if info[6] != '_' else None

        self.deprel = info[7] if info[7] != '_' else None 
        self.deps = info[8] if info[8] != '_' else None
        self.misc = info[9] if info[9] != '_' else None

    def reconstruct_feats(self):
        if len(self.feats.keys()):
            feats = list(self.feats.items())
            feats = sorted(feats, key=lambda a: a[0].lower())
            feats = [f'{feat[0]}={feat[1]}' for feat in feats if feat[1] is not None]
            feats = '|'.join(feats)
            return feats
        return '_'
    
    def get_head(self):
        head = None
        if self.head == '0':
            return 'ROOT'
        for token in self.sent:
            if token.sent_pos == self.head:
                head = token
        if head is None:
            print('ERROR:', token.head, token.sent_id, [tok.sent_pos for tok in self.sent], type(self.head), type(token.sent_pos))
        return head

    def to_conllu(self):
        sent_pos = self.sent_pos if self.sent_pos is not None else '_'
        form = self.form if self.form is not None else '_'
        lemma = self.lemma if self.lemma is not None else '_'
        upos = self.upos if self.upos is not None else '_'
        xpos = self.xpos if self.xpos is not None else '_'
        rfeats = self.reconstruct_feats()
        head = self.head if self.head is not None else '_'
        deprel = self.deprel if self.deprel is not None else '_'
        deps = self.deps if self.deps is not None else '_'
        misc = self.misc if self.misc is not None else '_'
        line = f'{sent_pos}\t{form}\t{lemma}\t{upos}\t{xpos}\t{rfeats}\t{head}\t{deprel}\t{deps}\t{misc}'
        return line
    


class Sentence():
    def __init__(self, sent_id, text, tok_lines, comments=[]) -> None:
        self.id = sent_id
        self.text = text
        self.comments = comments
        self.tokens = [Token(line, sent_id=self.id, sent=self) for line in tok_lines]

    def __getitem__(self, idx):
        return self.tokens[idx] if idx < len(self.tokens) else None
    
    def __len__(self):
        return len(self.tokens)
    
    def __iter__(self):
        return iter(self.tokens)
      
class ConlluTreebank():
    def __init__(self) -> None:
        self.sentences = {}
        self.document_structure = []

    def add_sentence(self, sentence_obj):
        self.sentences[sentence_obj.id] = sentence_obj

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return list(self.sentences.values())[idx]
        return self.sentences[idx]
    
    def __iter__(self):
        return iter(self.sentences.values())
    
    def __len__(self):
        return len(self.sentences.values())
    
    def iter_tokens(self):
        for sentence in self:
            for token in sentence:
                yield token
    
    def iter_sentences(self):
        for sentence in self:
            yield sentence

    def get_token_matches(self, **kwargs):
        matched_tokens = []
        for token in self.iter_tokens():
            found = True
            for k, v in kwargs.items():
                if isinstance(v, str):
                    if k in token.feats.keys():
                        if token.feats[k] != v:
                            found = False
                            break
                    elif hasattr(token, k):
                        if getattr(token, k) != v:
                            found = False
                            break
                    else:
                        if v is not None:
                            found = False
                            break
                elif callable(v):
                    if not v(token):
                        found = False
                        break
                else:
                    found = False    
            if found:
                matched_tokens.append(token)
        return matched_tokens
    
    # def get_deprel(self, deprel):
    #     found_subtrees = defaultdict(dict)
    #     for sentence in self.iter_sentences():
    #         for token in sentence:
    #             if token.deprel == deprel:
    #                 head = token.get_head()
    #                 found_subtrees[]
                
            

            

    def write_to_file(self, file_name):
        with open(file_name, 'w') as f:
            for line in self.document_structure:
                f.write(line+'\n')
                if re.match(r'# sent_id', line):
                    sent_id = line.split('=', maxsplit=1)[-1].strip()
                    sent = self.sentences[sent_id]
                    for comment in sent.comments:
                        f.write(comment+'\n')
                    for token in sent.tokens:
                        f.write(token.to_conllu()+'\n')

    @classmethod
    def load_conllu_from_file(cls, file):
        with open(file, 'r') as f:
            data = ConlluTreebank()
            sent_id = None
            comments = []
            for line in f:
                line = line.rstrip()
                
                if re.match(r'# sent_id', line):
                    sent_id = line.split('=', maxsplit=1)[-1].strip()
                    tok_lines = list()
                    data.document_structure.append(line)
                elif re.match(r'#', line) and sent_id:
                    comments.append(line)
                    if re.match(r'# text =', line):
                        text = line.split('=', maxsplit=1)[-1].strip()
                elif re.match(r'\d', line) and sent_id:
                    tok_lines.append(line.split('\t'))
                elif len(line) == 0 and sent_id:
                    sent = Sentence(sent_id, text, tok_lines, comments)
                    data.add_sentence(sent)
                    data.document_structure.append(line)
                    sent_id = None
                    comments = []
                else: 
                    data.document_structure.append(line)

        return data            

if __name__ == '__main__':
    file = '/home/norrman/GitHub/UD_Swedish-Talbanken/not-to-release/output/temp/sv6.conllu'

    data = ConlluTreebank.load_conllu_from_file(file)

    # found_tokens = data.get_token_matches(upos='ADJ',
    #                                       func1= lambda tok: tok.lemma[-1] in ['f', 'g', 'l', 'm', 'n', 'p', 'r', 's', 'v'],
    #                                       func2= lambda tok: tok.form == tok.lemma+'t')


    

    