import udapi
import sys
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

def set_new_pos(node, upos, xpos, feats):
    node.upos, node.xpos, node.feats = upos, xpos, feats

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
                    deps.append({'parent': dep['parent'], 'deprel': f"{dep['deprel']}{':' if mark_nodes else ''}{'_'.join([n.lemma for n in mark_nodes])}"})  

        elif node.deprel in {'obl', 'nmod'}:
            case_nodes = [child for child in node.children if child.deprel == 'case']
            if not len(case_nodes) and node.upos == 'ADP' and [child for child in node.children if child.deprel == 'conj']:
                case_nodes = [node]
            for dep in node.deps:
                if dep['parent'] == node.parent and dep['deprel'] in {'obl', 'nmod'}:
                    deps.append({'parent': dep['parent'], 'deprel': f"{dep['deprel']}{':' if case_nodes else ''}{'_'.join([n.lemma for n in case_nodes])}"})

        elif node.deprel in {'conj'}:
            cc_nodes = [child for child in node.children if child.deprel == 'cc']
            deps.append({'parent': node.parent, 'deprel': f"conj{':' if cc_nodes else ''}{'_'.join([n.lemma for n in cc_nodes])}"}) 
            parent_dep = [dep for dep in node.parent.deps if dep['parent'] == node.parent.parent]
            if parent_dep:
                deps.insert(0, parent_dep[0])
        
        deps = sorted(deps, key=lambda a: a['parent'])
        node.deps = deps if deps else node.deps

def ABBR(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    abr_node = exp['children'][0]

    if head_node.upos != "ADJ":        
        set_new_pos(head_node, "ADJ", "JJ|AN", {'Abbr': 'Yes'})

    set_new_deps(abr_node, parent_node, 'nmod')
    set_new_deps(head_node, abr_node, 'amod')

    transfer_children(head_node, abr_node)

    changes.append(exp)

def ABBR_s_ff(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    abr_node = exp['children'][0]

    set_new_pos(abr_node, "NOUN", "NN|AN", {"Abbr": "Yes"})


    set_new_deps(head_node, parent_node, 'nmod')
    set_new_deps(abr_node, head_node, 'conj')

    update_deprels([head_node, abr_node])

    changes.append(exp)

def AD_CALENDAS_GRAECA(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    calendas_node = exp['children'][0]
    graecas_node = exp['children'][1]

    set_new_deps(calendas_node, parent_node, head_node.deprel)
    set_new_deps(head_node, calendas_node, 'case')
    set_new_deps(graecas_node, calendas_node, 'amod')

    transfer_children(head_node, calendas_node)

    update_deprels([calendas_node, head_node, graecas_node])

    changes.append(exp)

def ADV_ADV_1(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    if adv_node.upos != "ADV":       
        set_new_pos(adv_node, "ADV", "AB", "_")

    set_new_deps(adv_node, head_node, 'advmod')

    update_deprels([head_node, adv_node])

    changes.append(exp)

def ADV_ADV_2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    set_new_deps(adv_node, parent_node, head_node.deprel)
    set_new_deps(head_node, adv_node, 'advmod')

    transfer_children(head_node, adv_node)

    update_deprels([head_node, adv_node])

    changes.append(exp)

def ADV_ADV_ADV_1(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    adv2_node = exp['children'][0]
    adv3_node = exp['children'][1]

    set_new_deps(adv3_node, parent_node, 'advmod')
    set_new_deps(head_node, adv3_node, 'advmod')
    set_new_deps(adv2_node, adv3_node, 'advmod')

    transfer_children(head_node, adv3_node)

    update_deprels([adv3_node, head_node, adv2_node])

    changes.append(exp)

def ADV_P(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(p_node, parent_node, 'case')

    update_deprels([parent_node, head_node, p_node])

    changes.append(exp)

def ADV_P_ADV(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    adv2_node = exp['children'][1]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(p_node, adv2_node, 'case')
    set_new_deps(adv2_node, head_node, 'obl')

    update_deprels([head_node, p_node, adv2_node, parent_node])

    changes.append(exp)

def ADV_P_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    nn_node = exp['children'][1]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(p_node, nn_node, 'case')
    set_new_deps(nn_node, head_node, 'obl')

    update_deprels([head_node, p_node, nn_node, parent_node])

    changes.append(exp)

def ADV_P_att(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    att_node = exp['children'][1]

    set_new_deps(head_node, parent_node.parent, 'advcl')
    set_new_deps(parent_node, head_node, 'advcl')
    set_new_deps(p_node, parent_node, 'mark')
    set_new_deps(att_node, parent_node, 'mark')

    update_deprels([head_node, p_node, att_node, parent_node])

    changes.append(exp)

def ADV_PR(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    pr_node = exp['children'][0]

    set_new_deps(pr_node, parent_node, head_node.deprel)
    set_new_deps(head_node, pr_node, 'advmod')

    update_deprels([pr_node, head_node, parent_node])

    changes.append(exp)

def ADV_JJ_än(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    jj_node = exp['children'][0]
    än_node = exp['children'][1]
    
    set_new_deps(jj_node, parent_node, 'nmod' if parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'amod')
    set_new_deps(än_node, parent_node, 'case')
    set_new_deps(head_node, jj_node, 'advmod')
    
    update_deprels([head_node, än_node, jj_node, parent_node])

    changes.append(exp)

def ADV_SC(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    sc_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(sc_node, parent_node, 'mark')

    update_deprels([head_node, sc_node, parent_node])

    changes.append(exp)

def ADV_SC_ADV(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    än_node = exp['children'][0]
    adv2_node = exp['children'][1]

    set_new_deps(head_node, parent_node.parent, parent_node.deprel)    
    set_new_deps(parent_node, head_node, 'obl')
    set_new_deps(än_node, parent_node, 'case')
    set_new_deps(adv2_node, parent_node, 'advmod')

    update_deprels([head_node, än_node, adv2_node, parent_node, parent_node.parent])

    changes.append(exp)

def ADV_VB(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    vb_node = exp['children'][0]

    set_new_deps(vb_node, parent_node, 'advcl')
    set_new_deps(head_node, vb_node, 'advmod')

    update_deprels([head_node, vb_node])

    changes.append(exp)

def ALLTEFTER(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    efter_node = exp['children'][0]

    set_new_deps(efter_node, parent_node, 'case')
    set_new_deps(head_node, efter_node, 'advmod')

    update_deprels([head_node, efter_node])

    changes.append(exp)

def ALLTEFTER(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    efter_node = exp['children'][0]

    set_new_deps(efter_node, parent_node, 'case')
    set_new_deps(head_node, efter_node, 'advmod')

    update_deprels([head_node, efter_node])

    changes.append(exp)

def ALLTEFTERSOM_1(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    efter_node = exp['children'][0]
    som_node = exp['children'][1]

    set_new_deps(efter_node, parent_node, 'mark')
    set_new_deps(som_node, efter_node, 'goeswith')
    set_new_deps(head_node, efter_node, 'advmod')

    update_deprels([head_node, efter_node, som_node])

    changes.append(exp)

def ALLTEFTERSOM_2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    eftersom_node = exp['children'][0]

    set_new_deps(eftersom_node, parent_node, 'mark')
    set_new_deps(head_node, eftersom_node, 'advmod')

    update_deprels([head_node, eftersom_node])

    changes.append(exp)

def ALLTEFTERSOM_3(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    som_node = exp['children'][0]

    set_new_deps(som_node, parent_node, 'mark')
    set_new_deps(head_node, som_node, 'advmod')

    update_deprels([head_node, som_node])

    changes.append(exp)

def ÄNNU_EN_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    en_node = exp['children'][0]
    nn_node = exp['children'][1]

    set_new_deps(nn_node, parent_node, 'obl')
    set_new_deps(head_node, nn_node, 'advmod')
    set_new_deps(en_node, nn_node, 'det')

    update_deprels([head_node, nn_node, en_node])

    changes.append(exp)

def CASE(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    second_node = exp['children'][0] 

    if second_node.upos == 'ADV' and second_node.form == 'sist':   
        set_new_pos(second_node, 'ADJ', 'JJ|SUV|SIN|IND|NOM', 'Case=Nom|Definite=Ind|Degree=Sup|Number=Sing')

    elif second_node.upos == 'ADV' and second_node.form == 'dess':
        set_new_pos(second_node, 'PRON', 'PS|UTR/NEU|SIN/PLU|DEF', 'Definite=Def|Poss=Yes|PronType=Prs')

    elif second_node.upos == 'ADV' and second_node.form == 'nytt':
        set_new_pos(second_node, 'ADJ', 'JJ|POS|SIN|IND|NOM', 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing')

    elif second_node.upos == 'ADV' and second_node.form == 'vidare':
        set_new_pos(second_node, 'ADJ', 'JJ|KOM|SIN/PLU|IND/DEF|NOM', 'Case=Nom|Degree=Cmp')

    elif second_node.upos == 'ADV' and second_node.form == 'stort':
        set_new_pos(second_node, 'ADJ', 'JJ|POS|SIN|IND|NOM', 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing')

    elif second_node.upos == 'ADV' and second_node.form == 'fatt':
        set_new_pos(second_node, 'NOUN', 'NN|-|-|-|-', '_')

    elif second_node.upos == 'ADV' and second_node.form == 'mera':
        set_new_pos(second_node, 'PRON', 'PN|UTR/NEU|SIN/PLU|IND|SUB/OBJ', 'Definite=Ind|PronType=Ind')

    elif second_node.upos == 'ADV' and second_node.form == 'kort':             
        set_new_pos(second_node, 'ADJ', 'JJ|SUV|SIN|IND|NOM', 'Case=Nom|Definite=Ind|Degree=Sup|Number=Sing')

    if head_node.deprel in {'advmod', 'compound:prt'}:
        set_new_deps(second_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(second_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, second_node, 'case')

    update_deprels([head_node, second_node])

    changes.append(exp) 

def CASE_DET(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    det_node = exp['children'][0] 
    noun_node = exp['children'][1]

    if head_node.deprel in {'advmod'}:
        set_new_deps(noun_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(noun_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, noun_node, 'case')
    set_new_deps(det_node, noun_node, 'det')
    
    transfer_children(head_node, noun_node)

    update_deprels([head_node, noun_node, det_node])

    changes.append(exp)

def CC(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    cc_node = exp['children'][0] 
    coord_node = exp['children'][1]

    set_new_deps(coord_node, head_node, 'conj')
    set_new_deps(cc_node, coord_node, 'cc')

    update_deprels([cc_node, coord_node])

    changes.append(exp)

def CC_X(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    cc_node = exp['children'][0]
    coord_node = cc_node.next_node

    set_new_deps(coord_node, head_node, 'conj')
    set_new_deps(cc_node, coord_node, 'cc')

    update_deprels([cc_node, head_node, coord_node])

    changes.append(exp)

def CC_X_X(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    cc_node = exp['children'][0]
    coord_node = exp['children'][1]
    igen_node = exp['children'][2]

    set_new_deps(coord_node, head_node, 'conj')
    set_new_deps(cc_node, coord_node, 'cc')
    set_new_deps(igen_node, parent_node, 'advmod')

    update_deprels([cc_node, head_node, coord_node])

    changes.append(exp)

def CC_DET(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    cc_node = exp['children'][0]
    det_node = exp['children'][1]
    coord_node = exp['children'][2]

    set_new_deps(coord_node, head_node, 'conj')
    set_new_deps(cc_node, coord_node, 'cc')
    set_new_deps(det_node, coord_node, 'det')

    update_deprels([cc_node, head_node, coord_node])

    changes.append(exp)

def CC_SÅ_ADV(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    så_node = exp['children'][0]
    coord_node = exp['children'][1]

    set_new_deps(coord_node, parent_node, 'conj')
    set_new_deps(head_node, coord_node, 'cc')
    set_new_deps(så_node, coord_node, 'advmod')

    update_deprels([head_node, parent_node, coord_node])

    changes.append(exp)

def CCONJ_NN(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]

    set_new_deps(nn_node, parent_node, 'obl')
    set_new_deps(head_node, nn_node, 'case')

    update_deprels([parent_node, head_node, nn_node])

    changes.append(exp)

def DET_HÄR(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    här_node = exp['children'][0]

    if head_node.deprel not in {'det'}:
        set_new_deps(här_node, head_node, 'advmod')
    else:
        set_new_deps(head_node, parent_node, 'det')
        set_new_deps(här_node, parent_node, 'advmod')

    if head_node.deprel == 'det':
        if head_node.upos != 'DET':
            head_node.upos = 'DET'
            head_node.xpos = 'DT'
            head_node.feats['PronType'] = 'Art'
    else:
        if head_node.upos != 'PRON':
            head_node.upos = 'PRON'
            head_node.xpos = 'PN'
            head_node.feats['PronType'] = 'Prs'

    update_deprels([parent_node, head_node, här_node])

    changes.append(exp)

def DET_JJ(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    jj_node = exp['children'][0]

    if parent_node.upos in {'NOUN', 'PRON', 'PROPN'} or head_node.deprel in {'det'}:
        set_new_deps(head_node, parent_node, 'det')
        set_new_deps(jj_node, parent_node, 'amod')
    else:
        set_new_deps(jj_node, parent_node, head_node.deprel)
        set_new_deps(head_node, jj_node, 'det')
        transfer_children(head_node, jj_node)

    changes.append(exp)

def DET_NN(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]

    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
        set_new_deps(head_node, nn_node, 'det')
        transfer_children(head_node, nn_node)
    else:
        set_new_deps(nn_node, parent_node, head_node.deprel)
        set_new_deps(head_node, nn_node, 'det')
        transfer_children(head_node, nn_node)

    update_deprels([head_node, nn_node])

    changes.append(exp)

def DET_PS(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    ps_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'det')
    set_new_deps(ps_node, parent_node, 'nmod:poss')

    changes.append(exp)

def DET_JJ_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    jj_node = exp['children'][0]
    nn_node = exp['children'][1]

    if parent_node.upos in {'NOUN', 'PRON', 'PROPN'} or head_node.deprel in {'det'}:
        set_new_deps(nn_node, parent_node, 'nmod')
        set_new_deps(head_node, nn_node, 'det')
        set_new_deps(jj_node, nn_node, 'amod')
        
        transfer_children(head_node, nn_node)
    else:
        set_new_deps(nn_node, parent_node, head_node.deprel)
        set_new_deps(head_node, nn_node, 'det')
        set_new_deps(jj_node, nn_node, 'amod')
        
        transfer_children(head_node, nn_node)

    update_deprels([head_node, nn_node])

    changes.append(exp)

def IJ_IJ(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    ij_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'discourse' if head_node.deprel != 'root' else 'root')
    set_new_deps(ij_node, head_node, 'flat')

    changes.append(exp)

def IJ_SÅ_ADV(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    ij_node = exp['children'][0]
    adv_node = exp['children'][1]

    set_new_deps(head_node, parent_node, 'discourse')
    set_new_deps(ij_node, adv_node, 'advmod')
    set_new_deps(adv_node, head_node, 'advmod')

    changes.append(exp)

def IJ_X(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'discourse')
    set_new_deps(adv_node, parent_node, 'advmod')

    changes.append(exp)

def INTE1(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    set_new_deps(adv_node, parent_node, 'advmod')
    set_new_deps(head_node, adv_node, 'advmod')

    changes.append(exp)

def INTE2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(adv_node, head_node, 'advmod')

    changes.append(exp)

def JJ_CC_ADV_JJ(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    cc_node = exp['children'][0]
    adv2_node = exp['children'][1]
    adv3_node = exp['children'][2]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(adv2_node, adv3_node, 'advmod')
    set_new_deps(adv3_node, head_node, 'conj')
    set_new_deps(cc_node, adv3_node, 'cc')

    update_deprels([adv3_node])

    changes.append(exp)

def JJ_CC_JJ(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    cc_node = exp['children'][0]
    adv_node = exp['children'][1]

    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(adv_node, head_node, 'conj')
    set_new_deps(cc_node, adv_node, 'cc')

    update_deprels([adv_node])

    changes.append(exp)

def JJ_HÄR(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    här_node = exp['children'][0]

    set_new_deps(här_node, head_node, 'advmod')

    changes.append(exp)

def JJ_NN(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]
    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn_node, parent_node, head_node.deprel)
    set_new_deps(head_node, nn_node, 'amod')

    changes.append(exp)

def JJ_P(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]

    

    if parent_node.upos in {'NOUN', 'PROPN', 'PRON'}:
        if parent_node.deprel != 'obl':
            set_new_deps(head_node, parent_node.parent, parent_node.deprel)
        else:
            set_new_deps(head_node, parent_node.parent, 'advcl')
        set_new_deps(parent_node, head_node, 'obl')
        set_new_deps(p_node, parent_node, 'case')
    else:
        if parent_node.deprel != 'obl':
            set_new_deps(head_node, parent_node.parent, parent_node.deprel)
        else:
            set_new_deps(head_node, parent_node.parent, 'advcl')
        set_new_deps(parent_node, head_node, 'advcl')
        set_new_deps(p_node, parent_node, 'mark')
    
    update_deprels([parent_node])

    changes.append(exp)

def NN_P_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    nn_node = exp['children'][1]

    if head_node.deprel == 'compound:prt':  
        set_new_deps(head_node, parent_node, 'obl')
    set_new_deps(nn_node, head_node, 'nmod')
    set_new_deps(p_node, nn_node, 'case')


    update_deprels([nn_node])
    
    changes.append(exp)

def P_ADV_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    adj_node = exp['children'][0]
    nn_node = exp['children'][1]

    adj_node.upos = 'ADJ'
    adj_node.feats = {'Case': 'Nom',
                      'Degree': 'Pos'}
    
    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                     'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:    
        set_new_deps(nn_node, parent_node, head_node.deprel)
    set_new_deps(head_node, nn_node, 'case')
    set_new_deps(adj_node, nn_node, 'amod')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node])

    changes.append(exp)

def P_ADV_TAG(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    om_node = exp['children'][0]

    head_node.upos = 'ADV'
    head_node.feats = {'Degree': 'Pos'}
    
    set_new_deps(om_node, head_node, 'advmod')

    changes.append(exp)

def P_ADV_VB(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    adj_node = exp['children'][0]
    vb_node = exp['children'][1]

    adj_node.upos = 'ADJ'
    adj_node.feats = {'Case': 'Nom',
                      'Degree': 'Pos'}
    
    set_new_deps(vb_node, parent_node, 'advcl')
    set_new_deps(adj_node, vb_node, 'obl')
    set_new_deps(head_node, adj_node, 'case')

    transfer_children(head_node, vb_node)

    update_deprels([vb_node, adj_node])

    changes.append(exp)

def P_DET_ADV(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    det_node = exp['children'][0]
    adv_node = exp['children'][1]

    set_new_deps(adv_node, parent_node, 'obl')
    set_new_deps(det_node, adv_node, 'det')
    set_new_deps(head_node, adv_node, 'case')

    transfer_children(head_node, adv_node)

    update_deprels([adv_node])

    changes.append(exp)

def P_DET_NN_som(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    det_node = exp['children'][0]
    nn_node = exp['children'][1]
    som_node = exp['children'][2]

    set_new_deps(nn_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, nn_node, 'acl')
    set_new_deps(som_node, parent_node, 'mark')
    set_new_deps(det_node, nn_node, 'det')
    set_new_deps(head_node, nn_node, 'case')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node, parent_node])
    
    changes.append(exp)

def P_JJ_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    jj_node = exp['children'][0]
    nn_node = exp['children'][1]

    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, nn_node, 'case')
    set_new_deps(jj_node, nn_node, 'amod')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node])

    changes.append(exp)

def P_NN_att(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]
    att_node = exp['children'][1]

    set_new_deps(nn_node, parent_node.parent, 'obl')
    set_new_deps(head_node, nn_node, 'case')
    set_new_deps(parent_node, nn_node, 'acl')
    set_new_deps(att_node, parent_node, 'mark')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node, parent_node])

    changes.append(exp)

def P_NN_CC_NN(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    jj1_node = exp['children'][0]
    cc_node = exp['children'][1]
    jj2_node = exp['children'][2]

    if head_node.deprel in {'advmod'}:
        set_new_deps(jj1_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(jj1_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, jj1_node, 'case')
    set_new_deps(jj2_node, jj1_node, 'conj')
    set_new_deps(cc_node, jj2_node, 'cc')

    transfer_children(head_node, jj1_node)

    update_deprels([jj1_node, jj2_node])

    changes.append(exp)

def P_NN_P(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]
    p_node = exp['children'][1]

    set_new_deps(nn_node, parent_node.parent, parent_node.deprel)
    set_new_deps(head_node, nn_node, 'case')
    set_new_deps(parent_node, nn_node, 'nmod')
    set_new_deps(p_node, parent_node, 'case')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node, parent_node])

    changes.append(exp)

def P_NN_P_NN(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    nn1_node = exp['children'][0]
    p_node = exp['children'][1]
    nn2_node = exp['children'][2]

    if head_node.deprel in {'advmod'}:
        set_new_deps(nn1_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn1_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, nn1_node, 'case')
    set_new_deps(nn2_node, nn1_node, 'conj')
    set_new_deps(p_node, nn2_node, 'case')

    transfer_children(head_node, nn1_node)

    update_deprels([nn1_node, nn2_node])

    changes.append(exp)

def P_NN_som(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]
    som_node = exp['children'][1]

    set_new_deps(nn_node, parent_node.parent, 'obl')
    set_new_deps(head_node, nn_node, 'case')
    set_new_deps(parent_node, nn_node, 'acl')
    set_new_deps(som_node, parent_node, 'mark')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node, parent_node])

    changes.append(exp)

def P_NN_TAG(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]

    nn_node.upos = 'NOUN'
    nn_node.feats = '_'
    nn_node.xpos = 'NN|-|-|-|-'
    
    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, nn_node, 'case')

    transfer_children(head_node, nn_node)
    
    update_deprels([nn_node])

    changes.append(exp)

def P_NN_VB(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]
    vb_node = exp['children'][1]    

    set_new_deps(nn_node, vb_node, 'obl')
    set_new_deps(vb_node, parent_node, 'advcl')
    set_new_deps(head_node, nn_node, 'case')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node, parent_node, vb_node])

    changes.append(exp)
    
def P_PR_att_VB(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    pr_node = exp['children'][0]
    att_node = exp['children'][1]
    vb_node = exp['children'][2]

    set_new_deps(pr_node, parent_node, 'obl')
    set_new_deps(vb_node, pr_node, 'acl')
    set_new_deps(att_node, vb_node, 'mark')
    set_new_deps(head_node, pr_node, 'case')

    transfer_children(head_node, pr_node)

    update_deprels([pr_node, vb_node])

    changes.append(exp)

def P_PS_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    ps_node = exp['children'][0]
    nn_node = exp['children'][1]

    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn_node, parent_node, 
                    head_node.deprel)
    set_new_deps(ps_node, nn_node, 'nmod:poss')
    set_new_deps(head_node, nn_node, 'case')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node, ps_node])

    changes.append(exp)

def P_TID_TAG(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]

    nn_node.upos = 'NOUN'
    nn_node.feats = {'Case': 'Nom',
                     'Definite': 'Ind'}
    
    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, nn_node, 'case')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node])

    changes.append(exp)

def P_TID_TID(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    nn1_node = exp['children'][0]
    nn2_node = exp['children'][1]
        
    set_new_deps(nn1_node, parent_node, head_node.deprel)
    set_new_deps(nn2_node, nn1_node, 'nmod')
    set_new_deps(head_node, nn1_node, 'case')

    transfer_children(head_node, nn1_node)

    update_deprels([nn1_node, nn2_node])

    changes.append(exp)

def P_TID_TID_TAG(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    nn1_node = exp['children'][0]
    nn2_node = exp['children'][1]

    if nn1_node.upos != 'NOUN':
        nn1_node.upos = 'NOUN'
        nn1_node.feats = {'Case': 'Nom',
                        'Definite': 'Ind'}
    if nn2_node.upos != 'NOUN':
        nn2_node.upos = 'NOUN'
        nn2_node.feats = {'Case': 'Nom',
                        'Definite': 'Ind'}
        
    set_new_deps(nn1_node, parent_node, head_node.deprel)
    set_new_deps(nn2_node, nn1_node, 'nmod')
    set_new_deps(head_node, nn1_node, 'case')

    transfer_children(head_node, nn1_node)

    update_deprels([nn1_node, nn2_node])

    changes.append(exp)

def PART_att(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    att_node = exp['children'][0]
   
        
    set_new_deps(head_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, head_node, 'ccomp')
    set_new_deps(att_node, parent_node, 'mark')

    update_deprels([head_node, parent_node])

    changes.append(exp)

def PR_ADV_VB(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]
    vb_node = exp['children'][1]

    if head_node.form in {'vad'}:
        set_new_pos(head_node, 'PRON', 'HP|NEU|SIN|IND', 'Definite=Ind|Gender=Neut|Number=Sing|PronType=Int')
    if vb_node.upos == 'VERB':
        set_new_pos(vb_node, 'AUX', 'VB|PRS|AKT', 'Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Act')

    set_new_deps(adv_node, parent_node, 'parataxis')
    set_new_deps(head_node, adv_node, 'nsubj')
    set_new_deps(vb_node, adv_node, 'cop')

    transfer_children(head_node, adv_node)

    changes.append(exp)

def PR_än(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    än_node = exp['children'][0]

    if parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'}:
        set_new_deps(head_node, parent_node.parent, parent_node.deprel)
        set_new_deps(parent_node, head_node, 'nmod')
        set_new_deps(än_node, parent_node, 'case')
    else:
        set_new_deps(head_node, parent_node.parent, parent_node.deprel)
        set_new_deps(parent_node, head_node, 'acl')
        set_new_deps(än_node, parent_node, 'mark')
    
    update_deprels([head_node, parent_node])

    changes.append(exp)

def PR_P_NN1(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    nn_node = exp['children'][1]

    set_new_deps(head_node, parent_node, 'obl')
    set_new_deps(nn_node, head_node, 'nmod')
    set_new_deps(p_node, nn_node, 'case')

    update_deprels([head_node, nn_node])

    changes.append(exp)

def PR_P_NN2(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    nn_node = exp['children'][1]

    set_new_deps(nn_node, head_node, 'nmod')
    set_new_deps(p_node, nn_node, 'case')

    update_deprels([head_node, nn_node])

    changes.append(exp)

def PR_P_NN3(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    nn_node = exp['children'][1]

    set_new_deps(head_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, head_node, 'nmod')
    set_new_deps(nn_node, head_node, 'nmod')
    set_new_deps(p_node, parent_node, 'case')
    set_new_deps(nn_node, parent_node, 'nmod:poss')

    update_deprels([head_node, nn_node, parent_node])

    changes.append(exp)

def PR_P_PR1(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    pr_node = exp['children'][1]

    set_new_deps(pr_node, head_node, 'nmod')
    set_new_deps(p_node, pr_node, 'case')

    update_deprels([head_node, pr_node])

    changes.append(exp) 

def PR_P_PR2(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    pr_node = exp['children'][1]

    set_new_deps(head_node, parent_node, 'obl')
    set_new_deps(pr_node, head_node, 'nmod')
    set_new_deps(p_node, pr_node, 'case')

    update_deprels([head_node, pr_node])

    changes.append(exp)  
 
def PR_P2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]

    set_new_deps(head_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, head_node, 'nmod')
    set_new_deps(p_node, parent_node, 'case')

    update_deprels([head_node, parent_node])

    changes.append(exp)

def PR_PR_än(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    jj_node = exp['children'][0]
    än_node = exp['children'][1]

    if parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'}:
        set_new_deps(jj_node, parent_node.parent, parent_node.deprel)
        set_new_deps(parent_node, jj_node, 'nmod')
        set_new_deps(head_node, jj_node, 'det')
        set_new_deps(än_node, parent_node, 'case')
    else:
        set_new_deps(jj_node, parent_node.parent, parent_node.deprel)
        set_new_deps(parent_node, jj_node, 'acl')
        set_new_deps(head_node, jj_node, 'det')
        set_new_deps(än_node, parent_node, 'mark')

    update_deprels([head_node, parent_node])

    changes.append(exp)

def PS_NN(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    nn_node = exp['children'][0]

    if head_node.deprel in {'advmod'}:
        set_new_deps(nn_node, parent_node, 
                    'nmod' if not parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'} else 'obl')
    else:
        set_new_deps(nn_node, parent_node, 
                    head_node.deprel)
    set_new_deps(head_node, nn_node, 'nmod:poss')

    transfer_children(head_node, nn_node)

    update_deprels([nn_node])

    changes.append(exp)

def SÅ_ADV_1(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]


    if adv_node.upos == 'ADJ':
        set_new_deps(adv_node, parent_node, 'amod')
    else:
        set_new_deps(adv_node, parent_node, head_node.deprel)
    set_new_deps(head_node, adv_node, 'advmod')

    transfer_children(head_node, adv_node)

    update_deprels([adv_node])

    changes.append(exp)

def SÅ_ADV_2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]


    set_new_deps(adv_node, parent_node.parent, 'advmod')
    set_new_deps(parent_node, adv_node, 'advcl')
    set_new_deps(head_node, adv_node, 'advmod')

    transfer_children(head_node, adv_node)

    update_deprels([adv_node, parent_node])

    changes.append(exp)

def SÅ_ADV_NN(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]
    nn_node = exp['children'][1]


    set_new_deps(nn_node, parent_node, 'nmod')
    set_new_deps(adv_node, nn_node, 'advmod')
    set_new_deps(head_node, adv_node, 'advmod')

    transfer_children(head_node, nn_node)

    update_deprels([adv_node, nn_node])

    changes.append(exp)

def SÅ_DÄR(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    där_node = exp['children'][0]


    set_new_deps(head_node, parent_node, 'advmod')
    set_new_deps(där_node, head_node, 'advmod')

    changes.append(exp)

def SÅ_SOM_1(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]
    som_node = exp['children'][1]

    if parent_node.upos in {'NOUN', 'PRON', 'PROPN', 'NUM'}:
        set_new_deps(adv_node, parent_node.parent, parent_node.deprel)
        set_new_deps(parent_node, adv_node, 'obl')
        set_new_deps(som_node, parent_node, 'case')
        set_new_deps(head_node, adv_node, 'advmod')
    else:
        set_new_deps(adv_node, parent_node.parent, parent_node.deprel)
        set_new_deps(parent_node, adv_node, 'advcl')
        set_new_deps(som_node, parent_node, 'mark')
        set_new_deps(head_node, adv_node, 'advmod')

    transfer_children(head_node, adv_node)

    update_deprels([adv_node, parent_node])

    changes.append(exp)

def SÅ_SOM_2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    som_node = exp['children'][0]

    set_new_deps(head_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, head_node, 'advcl')
    set_new_deps(som_node, parent_node, 'mark')

    update_deprels([parent_node])

    changes.append(exp)

def SÅ_VB(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adj_node = exp['children'][0]

    set_new_deps(adj_node, parent_node, 'amod')
    set_new_deps(head_node, adj_node, 'advmod')

    transfer_children(head_node, adj_node)

    update_deprels([parent_node])

    changes.append(exp)

def SÅ_X2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    x2_node = exp['children'][0]

    x2_node.upos = 'ADV'
    x2_node.xpos = 'AB'
    x2_node.feats = '_'

    set_new_deps(x2_node, parent_node, head_node.deprel)
    set_new_deps(head_node, x2_node, 'advmod')

    transfer_children(head_node, x2_node)

    update_deprels([parent_node])

    changes.append(exp)

def SC_ADV(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    set_new_deps(adv_node, parent_node, 'advcl')
    set_new_deps(head_node, adv_node, 'mark')

    transfer_children(head_node, adv_node)

    update_deprels([adv_node])

    changes.append(exp)

def SC_PR_VB(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    pr_node = exp['children'][0]
    vb_node = exp['children'][1]

    if parent_node.deprel in ['nmod', 'acl']:
        set_new_deps(vb_node, parent_node.parent, 'acl')
    else:
        set_new_deps(vb_node, parent_node.parent, 'advcl')

    if parent_node.deprel in ['nmod', 'obl']:
        set_new_deps(parent_node, vb_node, 'obj')
    elif parent_node.feats['VerbForm'] == 'Fin':
        set_new_deps(parent_node, vb_node, 'ccomp')
    else:
        set_new_deps(parent_node, vb_node, 'xcomp')

    set_new_deps(pr_node, vb_node, 'nsubj')

    transfer_children(head_node, vb_node)

    update_deprels([vb_node, pr_node, parent_node])

    changes.append(exp)

def som_ADV(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    adv_node = exp['children'][0]

    set_new_deps(adv_node, parent_node, 'advcl')
    set_new_deps(head_node, adv_node, 'mark')

    transfer_children(head_node, adv_node)

    update_deprels([adv_node])

    changes.append(exp)

def som_helst(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    som_node = exp['children'][0]
    helst_node = exp['children'][1]

    set_new_deps(som_node, head_node, 'advmod')
    set_new_deps(helst_node, som_node, 'fixed')

    som_node.misc['ExtPos'] = 'ADV'

    changes.append(exp)

def som_SC(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    sc_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'mark')
    set_new_deps(sc_node, parent_node, 'mark')

    update_deprels([parent_node])

    changes.append(exp)

def som_VB(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    vb_node = exp['children'][0]

    set_new_deps(vb_node, parent_node, 'advcl')
    set_new_deps(head_node, vb_node, 'mark')

    transfer_children(head_node, vb_node)

    update_deprels([parent_node, vb_node])

    changes.append(exp)

def till_att_börja_med(exp):
    assert len(exp['children']) == 3

    head_node = exp['head']
    parent_node = head_node.parent

    att_node = exp['children'][0]
    börja_node = exp['children'][1]
    med_node = exp['children'][2]

    set_new_deps(börja_node, parent_node, 'advcl')
    set_new_deps(head_node, börja_node, 'mark')
    set_new_deps(att_node, börja_node, 'mark')
    set_new_deps(med_node, börja_node, 'obl')

    transfer_children(head_node, börja_node)

    update_deprels([börja_node, med_node])

    changes.append(exp)

def VAD_EXPL_VB(exp):
    assert len(exp['children']) == 2

    head_node = exp['head']
    parent_node = head_node.parent

    expl_node = exp['children'][0]
    vb_node = exp['children'][1]
    
    set_new_deps(vb_node, parent_node, head_node.deprel)
    set_new_deps(head_node, vb_node, 'nsubj')
    set_new_deps(expl_node, vb_node, 'expl')

    transfer_children(head_node, vb_node)
    
    changes.append(exp)

def VAD_VB(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    vb_node = exp['children'][0]
    
    set_new_deps(vb_node, parent_node, head_node.deprel)
    set_new_deps(head_node, vb_node, 'nsubj')

    transfer_children(head_node, vb_node)
    
    changes.append(exp)

def VAR_ORD(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    ord_node = exp['children'][0]
    
    if parent_node.upos in {'NOUN', 'PRON', 'PROPN'} or head_node.deprel in {'det'}:
        set_new_deps(head_node, parent_node, 'det')
        set_new_deps(ord_node, parent_node, 'amod')
    else:
        set_new_deps(ord_node, parent_node, head_node.deprel)
        set_new_deps(head_node, ord_node, 'det')
        transfer_children(head_node, ord_node)

    changes.append(exp)

def VAR_PS(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    ps_node = exp['children'][0]
    
    if head_node.deprel == 'det':
        set_new_deps(ps_node, parent_node, 'nmod:poss')
    else:
        set_new_deps(ps_node, parent_node, head_node.deprel)
    set_new_deps(head_node, ps_node, 'det')

    changes.append(exp)

def VB_P(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]
    
    if parent_node.parent.upos in {'NOUN', 'PRON', 'PROPN'}:
        set_new_deps(head_node, parent_node.parent, 'acl')
    else:
        set_new_deps(head_node, parent_node.parent, 'advcl')

    if parent_node.upos in {'NOUN', 'PRON', 'PROPN'}:
        set_new_deps(parent_node, head_node, 'obl')
        set_new_deps(p_node, parent_node, 'case')
    else:
        set_new_deps(parent_node, head_node, 'advcl')
        set_new_deps(p_node, parent_node, 'mark')

    update_deprels([head_node, parent_node])

    changes.append(exp)

def VB_PR(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    pr_node = exp['children'][0]
    
    set_new_deps(head_node, parent_node, 'advcl')
    set_new_deps(pr_node, head_node, 'obj')

    update_deprels([head_node])

    changes.append(exp)

def VB_PR_PR_VB_VB(exp):
    assert len(exp['children']) == 4

    head_node = exp['head']
    parent_node = head_node.parent

    pr1_node = exp['children'][0]
    pr2_node = exp['children'][1]
    vb2_node = exp['children'][2]
    vb3_node = exp['children'][3]
    
    set_new_deps(pr1_node, head_node, 'obj')
    set_new_deps(vb2_node, pr1_node, 'acl:relcl')
    set_new_deps(vb3_node, vb2_node, 'aux')
    set_new_deps(pr2_node, vb2_node, 'nsubj')

    changes.append(exp)

def X_att(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    att_node = exp['children'][0]

    set_new_deps(head_node, parent_node, 'mark')
    set_new_deps(att_node, parent_node, 'mark')

    update_deprels([parent_node])

    changes.append(exp)

def X_SÅ1(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    så_node = exp['children'][0]

    set_new_deps(så_node, parent_node, head_node.deprel)
    set_new_deps(head_node, så_node, 'advmod')

    transfer_children(head_node, så_node)

    changes.append(exp)

def X_SÅ2(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    så_node = exp['children'][0]

    set_new_deps(så_node, parent_node, 'advmod')
    set_new_deps(head_node, parent_node, 'advmod')

    changes.append(exp)

def X_GAP_X(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    som_node = exp['children'][0]


    set_new_deps(head_node, parent_node, 'cc')
    set_new_deps(som_node, parent_node, 'cc')

    update_deprels([parent_node.parent, parent_node])

    changes.append(exp)

def CMP_ÄN(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    än_node = exp['children'][0]

    set_new_deps(head_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, head_node, 'obl')
    set_new_deps(än_node, parent_node, 'case')

    update_deprels([parent_node])

    changes.append(exp)

def I_NN_P(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    p_node = exp['children'][0]

    set_new_deps(head_node, parent_node.parent, 'advmod')
    set_new_deps(parent_node, head_node, 'nmod')
    set_new_deps(p_node, parent_node, 
                 'case')

    update_deprels([parent_node])

    changes.append(exp)

def PR_som(exp):
    assert len(exp['children']) == 1

    head_node = exp['head']
    parent_node = head_node.parent

    som_node = exp['children'][0]

    set_new_deps(som_node, parent_node, head_node.deprel)
    set_new_deps(head_node, parent_node.parent, parent_node.deprel)
    set_new_deps(parent_node, head_node, 'acl:relcl')

    update_deprels([parent_node, head_node])

    changes.append(exp)

def apply_rules(exp):
    if exp['rule'] in globals():
        globals()[exp['rule']](exp)
    else:
        print(f"RULE DOES NOT EXIST: {exp['rule']}")
        
def apply_conversion(doc, fixed_df):
    nodes = list(doc.nodes)
    id2node = {node.address(): i for i, node in enumerate(nodes)}
    fixed_expressions = get_fixed(doc)

    # assert all(exp['expression'] in fixed_df['expression'].to_list() for exp in fixed_expressions)

    for exp in fixed_expressions:
        if exp['expression'] in fixed_df['expression'].to_list():
            if fixed_df.loc[fixed_df['expression']==exp['expression']]['fixed'].values[0] == 'No':
                exp['rule'] = fixed_df.loc[fixed_df['expression']==exp['expression']]['rule'].values[0]
                if exp['rule']:
                    apply_rules(exp) 
                else:
                    print('ERROR RULE NOT DEFINED:', exp['rule'], file=sys.stderr)

            elif fixed_df.loc[fixed_df['expression']==exp['expression']]['fixed'].values[0] == 'Yes':
                exp['rule'] = 'FIXED'
                extpos = fixed_df.loc[fixed_df['expression']==exp['expression']]['extpos'].values[0]
                exp['head'].misc['ExtPos'] = extpos

                changes.append(exp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--infile', required=True)
    parser.add_argument('--outfile', required=True)
    parser.add_argument('--fixedfile', required=True)
    parser.add_argument('--verbose', action='store_true', default=False)

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

    # print(fixed_df)

    apply_conversion(doc, fixed_df)

    changes = sorted(changes, key=lambda exp: exp['rule'])

    if args.verbose:
        for exp_dict in changes:
            print('EXPRESSION:', exp_dict['expression'])
            print('ID:', exp_dict['head'].ord)
            print('RULE:', fixed_df.loc[fixed_df['expression']==exp_dict['expression']]['rule'].values[0])
            print(*[get_conllu(node) for node in exp_dict['head'].root.descendants], sep='\n')
            print()
    
    print('Writing to', outfile)
    doc.store_conllu(filename=outfile)
