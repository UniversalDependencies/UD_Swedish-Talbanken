import udapi
import argparse
import pandas as pd
from copy import deepcopy

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

def get_fixed_phrase(node):
     nodes = sorted([node] + [child for child in node.children if child.deprel == 'fixed'], key=lambda n: n.ord)
     return ' '.join([node.form for node in nodes]).lower()

def get_trees(doc):
    for bundle in doc.bundles:
        for tree in bundle.trees:
            yield tree

def find_spans(expression, root):
    spans = []
    if expression in root.text.lower():
        nodes = root.descendants
        for i, node in enumerate(nodes):
            span = nodes[i:i+len(expression.split())]
            span_expression = ' '.join([node.form.lower() for node in span])
            if span_expression == expression:
                if not any(node.deprel == 'fixed' and node.parent == span[0] for node in span[1:]):
                    spans.append(span)
    return spans

def get_fixed_children(node):
    return [n for n in node.children if n.deprel == 'fixed']

def get_fixed_structure(node):
    nodes = sorted([node] + [child for child in node.children if child.deprel == 'fixed'], key=lambda n: n.ord)
    return [node.upos for node in nodes]

def get_fixed_heads(doc):
    return set([node.parent for node in doc.nodes if node.deprel == 'fixed'])

def get_fixed(doc):
    return [{'head': head, 
             'children': get_fixed_children(head), 
             'expression': get_fixed_phrase(head), 
             'structure': get_fixed_structure(head)} for head in get_fixed_heads(doc)]

def find_unfixed_spans():
    spans = []
    for tree in get_trees(doc):
        for exp in fixed_df['expression'].to_list():
            spans.extend(find_spans(exp, tree.root))
    return spans

def set_new_deps(node, parent, deprel):
    node.parent, node.deprel = parent, deprel
    node.deps = [{'parent': parent, 'deprel': deprel}]

def transfer_children(old_node, new_node):
    for child in old_node.children:
        set_new_deps(child, new_node, child.deprel)

def update_deprels(nodes:list):
    assert isinstance(nodes, list)
    for node in nodes:
        deps = []
        if node.deprel in {'acl', 'advcl'}:
            mark_nodes = [child for child in node.children if child.deprel == 'mark']
            for dep in node.deps:
                if dep['parent'] == node.parent and dep['deprel'] in {'acl', 'advcl'}:
                    deps.append({'parent': dep['parent'], 'deprel': f"{dep['deprel']}:{':'.join([n.lemma for n in mark_nodes])}"})  

        elif node.deprel in {'obl', 'nmod'}:
            case_nodes = [child for child in node.children if child.deprel == 'case']
            if not len(case_nodes) and node.upos == 'ADP' and [child for child in node.children if child.deprel == 'conj']:
                case_nodes = [node]
            for dep in node.deps:
                if dep['parent'] == node.parent and dep['deprel'] in {'obl', 'nmod'}:
                    deps.append({'parent': dep['parent'], 'deprel': f"{dep['deprel']}:{':'.join([n.lemma for n in case_nodes])}"})

        elif node.deprel in {'conj'}:
            deps = node.deps
            parent_dep = [dep for dep in node.parent.deps if dep['parent'] == node.parent.parent][0]
            deps.insert(0, parent_dep)
        
        node.deps = deps if deps else node.deps

def DET_JJ(expression_dict):
    assert expression_dict['structure'] == ['DET', 'ADJ']
    assert expression_dict['head'].deprel in {'conj', 'det', 'obj'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 1
    det_node = expression_dict['head']
    adj_node = expression_dict['children'][0]
    parent_node = det_node.parent

    if det_node.deprel == 'det':
        set_new_deps(adj_node, parent_node, 'amod')
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in det_node.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()

    elif det_node.deprel == 'obj':
        set_new_deps(adj_node, parent_node, 'obj')
        set_new_deps(det_node, adj_node, 'det')
        transfer_children(det_node, adj_node)

        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in det_node.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()

    elif det_node.deprel == 'conj':
        cc_node = [child for child in det_node.children if child.deprel == 'cc']
        assert len(cc_node) == 1
        cc_node = cc_node[0]
        
        coordinated_node = parent_node
        
        head_noun_node = coordinated_node.parent

        assert head_noun_node.upos in {'NOUN', 'PRON', 'PROPN'}

        for child in head_noun_node.children:
            if child != coordinated_node:
                set_new_deps(child, coordinated_node, child.deprel)

        set_new_deps(det_node, head_noun_node, 'det')
        set_new_deps(adj_node, head_noun_node, 'amod')
        set_new_deps(cc_node, head_noun_node, 'cc')
        set_new_deps(coordinated_node, head_noun_node.parent, head_noun_node.deprel)
        set_new_deps(head_noun_node, coordinated_node, 'conj')
        
        update_deprels([coordinated_node, head_noun_node])

        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in det_node.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
        

    else:
        unhandled_expressions.append(expression_dict)

def DET_NN(expression_dict):
    assert expression_dict['structure'] == ['DET', 'NOUN'], expression_dict['structure']
    assert len(expression_dict['children']) == 1
    assert expression_dict['head'].deprel in {'nmod', 'obj', 'advmod'}, expression_dict['head'].deprel

    det_node = expression_dict['head']
    noun_node = expression_dict['children'][0]
    parent_node = det_node.parent

    if expression_dict['head'].deprel in {'nmod', 'obj', 'advmod'}:
        set_new_deps(noun_node, parent_node, det_node.deprel)
        set_new_deps(det_node, noun_node, 'det')
        transfer_children(det_node, noun_node)

        update_deprels([noun_node])

        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in det_node.root.descendants], sep='\n')
        # print()
    else:
        unhandled_expressions.append(expression_dict)
   
def P_NN_P(expression_dict):    
    assert expression_dict['structure'] == ['ADP', 'NOUN', 'ADP']
    assert expression_dict['head'].deprel in {'case', 'mark', 'conj'} and expression_dict['head'].upos == 'ADP', expression_dict['head'].deprel 
    assert len(expression_dict['children']) == 2
    
    parent_node = expression_dict['head'].parent
    parent_deprel = parent_node.deprel
    parent_head = parent_node.parent

    first_adp = expression_dict['head']
    head_noun = expression_dict['children'][0]
    second_adp = expression_dict['children'][1]
    assert first_adp.upos == 'ADP'
    assert head_noun.upos == 'NOUN'
    assert second_adp.upos == 'ADP'

    if expression_dict['head'].deprel == 'case':
        set_new_deps(head_noun, parent_head, parent_deprel)
        set_new_deps(parent_node, head_noun, 'nmod')
        set_new_deps(first_adp, head_noun, 'case')
        set_new_deps(second_adp, parent_node, 'case')

        transfer_children(first_adp, head_noun)

        update_deprels([parent_node, head_noun])

        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in sorted([parent_head, first_adp, head_noun, second_adp, parent_node], key=lambda n: n.ord)], sep='\n')

    elif expression_dict['head'].deprel == 'mark':
        assert parent_deprel == 'advcl', parent_deprel
        set_new_deps(head_noun, parent_head, 'advmod')
        set_new_deps(parent_node, head_noun, 'acl')
        set_new_deps(first_adp, head_noun, 'case')
        set_new_deps(second_adp, parent_node, 'mark')

        transfer_children(first_adp, head_noun)

        update_deprels([head_noun, parent_node])

        changes.append(expression_dict)

        # print(*[get_conllu(node) for node in sorted([parent_head, first_adp, head_noun, second_adp, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
        
    elif expression_dict['head'].deprel == 'conj':
        cc_node = [child for child in first_adp.children if child.deprel == 'cc']
        assert len(cc_node) == 1
        cc_node = cc_node[0]
        coordinated_adp_node = parent_node
        assert coordinated_adp_node.deprel == 'case'
        
        dependent_noun_node = coordinated_adp_node.parent

        assert dependent_noun_node.upos in {'NOUN', 'PRON', 'PROPN'}

        set_new_deps(coordinated_adp_node, dependent_noun_node.parent, dependent_noun_node.deprel)
        set_new_deps(head_noun, coordinated_adp_node, 'conj')
        set_new_deps(dependent_noun_node, head_noun, 'nmod')
        set_new_deps(first_adp, head_noun, 'case')
        set_new_deps(second_adp, dependent_noun_node, 'case')
        set_new_deps(cc_node, head_noun, 'cc')

        update_deprels([coordinated_adp_node, head_noun, dependent_noun_node])

        changes.append(expression_dict)

        # print(*[get_conllu(node) for node in head_noun.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([parent_head, first_adp, head_noun, second_adp, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()  
    else:
        unhandled_expressions.append(expression_dict)

def P_NN(expression_dict):
    assert (expression_dict['structure'] == ['ADP', 'NOUN'] or 
            expression_dict['structure'] == ['ADP', 'PRON']), expression_dict
    assert expression_dict['head'].deprel in {'root', 'compound:prt', 'advmod', 'xcomp',  'nmod', 'acl:relcl', 'case', 'advcl'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 1
    
    adp_node = expression_dict['head']
    noun_node = expression_dict['children'][0]
    parent_node = adp_node.parent

    if adp_node.deprel in {'root', 'xcomp', 'acl:relcl', 'advcl'}:
        set_new_deps(noun_node, parent_node, adp_node.deprel)
        set_new_deps(adp_node, noun_node, 'case')
        transfer_children(adp_node, noun_node)

        update_deprels([noun_node])

        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # print()
    elif adp_node.deprel in {'compound:prt', 'advmod'}:
        set_new_deps(noun_node, parent_node, 'obl')
        set_new_deps(adp_node, noun_node, 'case')
        transfer_children(adp_node, noun_node)

        update_deprels([noun_node])
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # print()
    elif adp_node.deprel in {'case'}:
        set_new_deps(noun_node, parent_node.parent, parent_node.deprel if parent_node.parent.upos != 'VERB' else 'obl')
        set_new_deps(parent_node, noun_node, parent_node.deprel)
        set_new_deps(adp_node, noun_node, 'case')
        transfer_children(adp_node, noun_node)
        transfer_children(parent_node, noun_node)

        update_deprels([noun_node])
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # print()
    else:
        unhandled_expressions.append(expression_dict)
 
def P_JJ(expression_dict):
    assert expression_dict['structure'] == ['ADP', 'ADJ'], expression_dict
    assert expression_dict['head'].deprel in {'advmod'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 1
    adp_node = expression_dict['head']
    adj_node = expression_dict['children'][0]
    parent_node = adp_node.parent

    assert parent_node.upos in {'NOUN', 'VERB', 'ADJ'}, parent_node.upos

    if adp_node.deprel == 'advmod':
        set_new_deps(adj_node, parent_node, 'amod' if parent_node.upos in {'NOUN', 'PRON', 'PROPN'} else 'advmod')
        set_new_deps(adp_node, adj_node, 'case')

        transfer_children(adp_node, adj_node)

        update_deprels([adj_node])
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
    else:
        unhandled_expressions.append(expression_dict)

def P_JJ_NN(expression_dict):
    assert expression_dict['structure'] == ['ADP', 'ADJ', 'NOUN'], expression_dict
    assert expression_dict['head'].deprel in {'nmod', 'advmod'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 2
    adp_node = expression_dict['head']
    adj_node = expression_dict['children'][0]
    noun_node = expression_dict['children'][1]
    parent_node = adp_node.parent

    if expression_dict['head'].deprel in {'nmod'}:
        set_new_deps(noun_node, parent_node, adp_node.deprel)
        set_new_deps(adj_node, noun_node, 'amod')
        set_new_deps(adp_node, noun_node, 'case')

        transfer_children(adp_node, noun_node)

        update_deprels([noun_node])
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
    elif expression_dict['head'].deprel in {'advmod'}:
        set_new_deps(noun_node, parent_node, 'obl' if parent_node not in {'NOUN', 'PRON', 'PROPN'} else 'nmod')
        set_new_deps(adj_node, noun_node, 'amod')
        set_new_deps(adp_node, noun_node, 'case')

        transfer_children(adp_node, noun_node)

        update_deprels([noun_node])
        
        changes.append(expression_dict)

        # # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # print(*[get_conllu(node) for node in sorted([adp_node, noun_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
        
    else:
        unhandled_expressions.append(expression_dict)

def P_DET_JJ(expression_dict):
    assert expression_dict['structure'] == ['ADP', 'DET', 'ADJ'], expression_dict
    assert expression_dict['head'].deprel in {'conj', 'root', 'advmod'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 2
    adp_node = expression_dict['head']
    det_node = expression_dict['children'][0]
    adj_node = expression_dict['children'][1]
    parent_node = adp_node.parent

    if expression_dict['head'].deprel in {'root', 'advmod', 'conj'}:
        set_new_deps(adj_node, adp_node.parent, adp_node.deprel)
        set_new_deps(adp_node, adj_node, 'case')
        set_new_deps(det_node, adj_node, 'det')

        transfer_children(adp_node, adj_node)

        update_deprels([adj_node])
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # # print(*[get_conllu(node) for node in sorted([adp_node, noun_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
    else:
        unhandled_expressions.append(expression_dict)

def P_ADV(expression_dict):
    assert expression_dict['structure'] == ['ADP', 'ADV'], expression_dict
    assert expression_dict['head'].deprel in {'advmod', 'nmod', 'compound:prt', 'conj'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 1
    adp_node = expression_dict['head']
    adv_node = expression_dict['children'][0]
    parent_node = adp_node.parent


    if expression_dict['head'].deprel in {'advmod'}:
        set_new_deps(adv_node, parent_node, adp_node.deprel)
        set_new_deps(adp_node, adv_node, 'case')
        
        changes.append(expression_dict)
        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()

    else:
        unhandled_expressions.append(expression_dict)

def P_ADV_NN(expression_dict):
    assert expression_dict['structure'] == ['ADP', 'ADV', 'NOUN'], expression_dict
    assert expression_dict['head'].deprel in {'advmod', 'conj', 'root'}, expression_dict['head'].deprel
    assert len(expression_dict['children']) == 2
    adp_node = expression_dict['head']
    adv_node = expression_dict['children'][0]
    noun_node = expression_dict['children'][1]
    parent_node = adp_node.parent

    if expression_dict['head'].deprel in {'advmod', 'root', 'conj'}:
        set_new_deps(noun_node, parent_node, 'nmod' if parent_node.upos in {'NOUN', 'PROPN', 'PRON'} else 'obl' if adp_node.deprel in {'advmod'} else adp_node.deprel)
        set_new_deps(adp_node, noun_node, 'case')
        set_new_deps(adv_node, noun_node, 'amod')

        transfer_children(adp_node, noun_node)

        update_deprels([noun_node])

        changes.append(expression_dict)

        # print(*[get_conllu(node) for node in adp_node.root.descendants], sep='\n')
        # # print(*[get_conllu(node) for node in sorted([det_node, adj_node, parent_node], key=lambda n: n.ord)], sep='\n')
        # print()
    else:
        unhandled_expressions.append(expression_dict)


def apply_rules(expression_dict, rule):
    if rule in globals():
        globals()[rule](expression_dict)
    else:
        print(f'RULE DOES NOT EXIST: {rule}')
        
def apply_conversion(doc, fixed_df):
    nodes = list(doc.nodes)
    id2node = {node.address(): i for i, node in enumerate(nodes)}
    fixed_expressions = get_fixed(doc)

    # assert all(exp['expression'] in fixed_df['expression'].to_list() for exp in fixed_expressions)

    for exp in fixed_expressions:
        if exp['expression'] in fixed_df['expression'].to_list():
            rule = fixed_df.loc[fixed_df['expression']==exp['expression']]['rule'].values[0]
            if rule:
                apply_rules(exp, rule)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--infile', required=True)
    parser.add_argument('--outfile', required=True)
    parser.add_argument('--fixedfile', required=True)

    args = parser.parse_args()

    infile = args.infile
    fixedfile = args.fixedfile
    outfile = args.outfile
    
    changes = []
    unhandled_expressions = []

    print(f"Reading {infile}")
    doc = udapi.Document(infile)

    print(f"Reading {fixedfile}")
    fixed_df = pd.read_csv(fixedfile)

    apply_conversion(doc, fixed_df)

    for exp_dict in changes:
        print('EXPRESSION:', exp_dict['expression'])
        print('ID:', exp_dict['head'].ord)
        print('RULE:', fixed_df.loc[fixed_df['expression']==exp_dict['expression']]['rule'].values[0])
        print(*[get_conllu(node) for node in exp_dict['head'].root.descendants], sep='\n')
        print()
    
    print('Writing to', outfile)
    doc.store_conllu(filename=outfile)
