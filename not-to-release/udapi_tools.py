import udapi

class FilterList(list):
    def filter(self, **kwargs):
        matched_tokens = []
        for tb, node in self:
            found = True
            for k, v in kwargs.items():
                if isinstance(v, str):
                    if k in node.feats.keys():
                        if node.feats[k] != v:
                            found = False
                            break
                    elif hasattr(node, k):
                        if getattr(node, k) != v:
                            found = False
                            break
                    else:
                        if v is not None:
                            found = False
                            break
                elif callable(v):
                    if not v(node):
                        found = False
                        break
                else:
                    found = False    
            if found:
                matched_tokens.append((tb, node))
        return matched_tokens
    
    def content(self, address=False, form=True, lemma=False, upos=False, deprel=False, feats=False, text=False, treebank=False, sorting_fn=lambda node: node[1].form.lower(), **kwargs):
        output = list()
        for tb, node in sorted(self, key=sorting_fn):
            line = ''
            line += f"id='{node.address()}'" + '\t' if address else ''
            line += f"treebank='{tb}'" + '\t' if treebank else ''
            line += f"form='{node.form}'" + '\t' if form else ''
            line += f"lemma='{node.lemma}'" + '\t' if lemma else ''
            line += f"upos='{node.upos}'" + '\t' if upos else ''
            line += f"deprel='{node.deprel}'" + '\t' if deprel else ''
            line += f"feats='{node.feats.__str__()}'" + '\t' if feats else ''
            line += f"text='{node.root.compute_text()}'" + '\t' if text else ''

            for key, fn in kwargs.items():
                line += f"{key}='{fn(node)}'" + '\t' if feats else ''
            
            if line not in output:
                output.append(line)
        
        return output
        

class Treebanks:
    def __init__(self, treebanks) -> None:
        self.treebanks = treebanks
        for key, tb in self.treebanks.items():
            setattr(self, key, tb)

    @property
    def nodes(self):
        for key, tb in self.treebanks.items():
            for node in tb.nodes:
                yield key, node

    def filter(self, **kwargs):
        matched_tokens = FilterList()
        for tb, node in self.nodes:
            found = True
            for k, v in kwargs.items():
                if isinstance(v, str):
                    if k in node.feats.keys():
                        if node.feats[k] != v:
                            found = False
                            break
                    elif hasattr(node, k):
                        if getattr(node, k) != v:
                            found = False
                            break
                    else:
                        if v is not None:
                            found = False
                            break
                elif callable(v):
                    if not v(node):
                        found = False
                        break
                else:
                    found = False    
            if found:
                matched_tokens.append((tb, node))
        return matched_tokens
    
    
def get_conllu(node):
    if node._parent is None:
        head = '_' # Empty nodes
    else:
        try:
            head = str(node._parent._ord)
        except AttributeError:
            head = '0'

    conllu_str = '\t'.join('_' if v is None else v for v in
                    (str(node._ord), node.form, node.lemma, node.upos, node.xpos,
                    '_' if node._feats is None else str(node.feats), head, node.deprel,
                    node.raw_deps, '_' if node._misc is None else str(node.misc)))
    return conllu_str