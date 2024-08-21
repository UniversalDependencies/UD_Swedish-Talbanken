import udapi
import argparse

# function for converting udapi-node to conllu string.
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--infile', required=True)
    parser.add_argument('--ucxnfile', required=True)
    parser.add_argument('--outfile', required=True)

    args = parser.parse_args()

    infile = args.infile
    ucxnfile = args.ucxnfile
    outfile = args.outfile

    print(f"Reading {infile}")
    ud_doc = udapi.Document(infile)
    print(f"Reading {ucxnfile}")
    ucxn_doc = udapi.Document(ucxnfile)

    ud_nodes = list(ud_doc.nodes)
    id2node = {node.address(): i for i, node in enumerate(ud_nodes)}

    for node in ucxn_doc.nodes:
        assert node.address() in id2node
        cxn, cxnelt = node.misc.get('Cxn', None), node.misc.get('CxnElt', None)
        if cxn or cxnelt:
            if cxn: ud_nodes[id2node[node.address()]].misc['Cxn'] = cxn
            if cxnelt: ud_nodes[id2node[node.address()]].misc['CxnElt'] = cxnelt

    print('Writing to', outfile)
    ud_doc.store_conllu(filename=outfile)
