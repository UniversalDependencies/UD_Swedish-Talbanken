import conllutils as cu
import sys, re
from collections import defaultdict, Counter

def change_den_det_de(tok):
    change_id = None
    if token.upos == 'PRON':
        if token.form.lower() == 'den':
            token.lemma = 'den'
            token.feats = {'Definite': 'Def',
                           'Gender': 'Com',
                           'Number': 'Sing',
                           'PronType' :'Prs'}
            change_id = 'pron_1'

        elif token.form.lower() == 'det':
            token.lemma = 'den'
            token.feats = {'Definite': 'Def',
                           'Gender': 'Neut',
                           'Number': 'Sing',
                           'PronType' :'Prs'}
            change_id = 'pron_2'
            
        elif token.form.lower() == 'de':
            token.lemma = 'de'
            token.feats = {'Case': 'Nom',
                           'Definite': 'Def',
                           'Number': 'Plur',
                           'PronType' :'Prs'}
            change_id = 'pron_3'
            
        elif token.form.lower() == 'dem':
            token.lemma = 'de'
            token.feats = {'Case': 'Acc',
                           'Definite': 'Def',
                           'Number': 'Plur',
                           'PronType' :'Prs'}
            change_id = 'pron_4'
            
        elif token.form.lower() == 'dom':
            token.lemma = 'de'
            token.feats = {'Definite': 'Def',
                           'Number': 'Plur',
                           'PronType' :'Prs'}
            change_id = 'pron_5'

        
    elif token.upos == 'DET':
        if token.form.lower() == 'den':
            token.lemma = 'den'
            token.feats = {'Definite': 'Def',
                           'Gender': 'Com',
                           'Number': 'Sing',
                           'PronType' :'Art'}
            change_id = 'det_1'
            
        elif token.form.lower() == 'det':
            token.lemma = 'den'
            token.feats = {'Definite': 'Def',
                           'Gender': 'Neut',
                           'Number': 'Sing',
                           'PronType' :'Art'}
            change_id = 'det_2'
            
        elif token.form.lower() == 'de':
            token.lemma = 'de'
            token.feats = {'Definite': 'Def',
                           'Number': 'Plur',
                           'PronType' :'Art'}
            change_id = 'det_3'
            
        elif token.form.lower() == 'dom':
            token.lemma = 'de'
            token.feats = {'Definite': 'Def',
                           'Number': 'Plur',
                           'PronType' :'Art'}
            change_id = 'det_4'
    return change_id        
    
def change_adj (tok):
    ''' returns new features for adjectives, not complete and will miss several tokens that are now annotated wrongly '''
    change_id = None

    if tok.feats.get('Gender', None) == 'Masc':
        tok.feats['Gender'] = 'Com'
        change_id = change_id + '_RmMasc' if change_id is not None else 'adj_RmMasc'

    if tok.feats.get('Abbr', None) == 'Yes':
        tok.feats['Case'] = 'Nom'
        tok.feats['Degree'] = 'Pos'
        if tok.form.lower() in ['s.k.', 's k']:
            tok.lemma = 'så_kallad'
        elif tok.form.lower() in ['kungl.', 'kungl']:
            tok.lemma = 'kunglig'
        elif tok.form.lower() in ['s:t', 'st.', 'st']:
            tok.lemma = 'sankt'
        elif tok.form.lower() in ['ev', 'ev.']:
            tok.lemma = 'eventuell'
        elif tok.form.lower() in ['resp', 'resp.']:
            tok.lemma = 'respektive'
        elif tok.form.lower() in ['med', 'med.']:
            tok.lemma = 'medicine'
        elif tok.form.lower() in ['fil', 'fil.']:
            tok.lemma = 'filosofie'
        elif tok.form.lower() in ['teol', 'teol.']:
            tok.lemma = 'teologie'
                
        change_id = change_id + '_abbr' if change_id is not None else 'adj_abbr'

    elif (tok.lemma[-1] in ['f', 'g', 'l', 'm', 'n', 'p', 'r', 's', 'v']) and (tok.form.lower() == tok.lemma+'t'):
        gender = tok.feats.get('Gender', 'Neut')
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Ind',
                     'Degree': 'Pos',
                     'Gender': gender,
                     'Number': 'Sing'}
        
        change_id = 'adj_0' if change_id is None else '_'.join(['adj_0', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing'
        
    elif tok.form.lower().endswith('ad') and tok.lemma.endswith('a'):
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Ind',
                     'Degree': 'Pos',
                     'Gender': 'Com',
                     'Number': 'Sing',
                     'Tense': 'Past',
                     'VerbForm': 'Part'}
        
        change_id = 'adj_1' if change_id is None else '_'.join(['adj_1', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Com|Number=Sing|Tense=Past|VerbForm=Part'
        
    elif tok.form.lower().endswith('ade') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
        if tok.feats.get('Number', None) == 'Plur':
            tok.feats = {'Case': 'Nom',
                         'Definite': 'Ind',
                         'Degree': 'Pos',
                         'Number': 'Plur',
                         'Tense': 'Past',
                         'VerbForm': 'Part'}
            
            change_id = 'adj_2' if change_id is None else '_'.join(['adj_2', *change_id.lstrip('adj').split('_')])
            # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Number=Plur|Tense=Past|VerbForm=Part'
    
        else: 
            tok.feats = {'Case': 'Nom',
                         'Definite': 'Def',
                         'Degree': 'Pos',
                         'Tense': 'Past',
                         'VerbForm': 'Part'}
            
            change_id = 'adj_3' if change_id is None else '_'.join(['adj_3', *change_id.lstrip('adj').split('_')])
            # nfeats = 'Case=Nom|Definite=Def|Degree=Pos|Tense=Past|VerbForm=Part'
    
    elif tok.form.lower().endswith('at') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Ind',
                     'Degree': 'Pos',
                     'Gender': 'Neut',
                     'Number': 'Sing',
                     'Tense': 'Past',
                     'VerbForm': 'Part'}
        
        change_id = 'adj_4' if change_id is None else '_'.join(['adj_4', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing|Tense=Past|VerbForm=Part'

    elif (tok.form.lower().endswith('sta') or token.form.lower().endswith('ste')) and tok.feats.get('Degree', None) == 'Sup' and tok.feats.get('Definite', None) != 'Ind':
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Def',
                     'Degree': 'Sup'}
        
        change_id = 'adj_5' if change_id is None else '_'.join(['adj_5', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Def|Degree=Sup'
        
    elif tok.form.lower().endswith('st') and tok.feats.get('Degree', None) == 'Sup':
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Ind',
                     'Degree': 'Sup'}
        
        change_id = 'adj_6' if change_id is None else '_'.join(['adj_6', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Ind|Degree=Sup'
        
    elif tok.form.lower().endswith('re') and tok.feats.get('Degree', None) == 'Cmp':
        tok.feats = {'Case': 'Nom',
                     'Degree': 'Cmp'}
        
        change_id = 'adj_7' if change_id is None else '_'.join(['adj_7', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Degree=Cmp'

    elif not tok.form.lower().endswith('sta') and tok.form.lower() == tok.lemma + 'a' and tok.feats.get('Definite', None) == 'Def':
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Def',
                     'Degree': 'Pos'}
        
        change_id = 'adj_8' if change_id is None else '_'.join(['adj_8', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Def|Degree=Pos'
    
    elif not tok.form.lower().endswith('sta') and tok.form.lower() == tok.lemma + 'a' and tok.feats.get('Number', None) == 'Plur':
        tok.feats = {'Case': 'Nom',
                     'Definite': 'Ind',
                     'Degree': 'Pos',
                     'Number': 'Plur'}
        
        change_id = 'adj_9' if change_id is None else '_'.join(['adj_9', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Number=Plur'
    
    elif token.xpos is not None and ('RO' in token.xpos or token.xpos == 'ORD'):
        tok.feats = {'Case': 'Nom',
                     'Number': 'Sing',
                     'NumType': 'Ord'}
        
        change_id = 'adj_10' if change_id is None else '_'.join(['adj_10', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Number=Sing|NumType=Ord'

    elif tok.form.lower().endswith('nde'):
        tok.feats = {'Case': 'Nom',
                     'Degree': 'Pos',
                     'Tense': 'Pres',
                     'VerbForm': 'Part'}
        
        change_id = 'adj_11' if change_id is None else '_'.join(['adj_11', *change_id.lstrip('adj').split('_')])
        # nfeats = 'Case=Nom|Degree=Pos|Tense=Pres|VerbForm=Part'
    
    
    if (tok.form.lower().endswith('a') or tok.form.lower().endswith('as')) and tok.feats.get('Definite', None) == 'Def' and tok.feats.get('Number', None) is not None:
        tok.feats['Number'] = None
        change_id = change_id + '_DefRmNum' if change_id is not None else 'adj_DefRmNum'   

    if tok.feats.get('Case', None) is None:
        tok.feats['Case'] = 'Nom' if not tok.form.lower().endswith('s') else 'MANUAL_FIX'
        change_id = change_id + '_AddCase' if change_id is not None else 'adj_AddCase'
    
    if tok.feats.get('Degree', None) is None and tok.feats.get('NumType', None) != 'Ord':
        tok.feats['Degree'] = 'Pos' if (tok.feats.get('VerbForm', None) == 'Part' or 
                                        (not tok.form.lower().endswith('re') and
                                        not tok.form.lower().endswith('res') and
                                        not tok.form.lower().endswith('sta') and
                                        not tok.form.lower().endswith('ste') and
                                        not tok.form.lower().endswith('stas') and
                                        not tok.form.lower().endswith('stes') and
                                        not tok.form.lower().endswith('st'))) else 'MANUAL_FIX'
        change_id = change_id + '_AddDegree' if change_id is not None else 'adj_AddDegree'

    

    return change_id
        
if __name__ == '__main__':
    infile, outfile = sys.argv[1:]

    print('Reading', infile)
    talbanken = cu.ConlluTreebank.load_conllu_from_file(infile)

    change_log = list()
    change_ids = list()

    changed_adj = defaultdict(set)
    
    for token in talbanken.iter_tokens():

        if token.form.lower() in ['den', 'de', 'det', 'dem', 'dom']:
            old_feats = token.reconstruct_feats()
            old_lemma = token.lemma
            change_id = change_den_det_de(token)
            new_feats = token.reconstruct_feats()
            new_lemma = token.lemma
            if new_feats != old_feats or new_lemma != old_lemma:
                item = f"{change_id=}\t{token.sent_id=}\t{token.sent_pos=}\t{token.form=}\t{token.lemma=}\t{old_lemma=}\t{new_lemma=}\t{old_feats=}\t{new_feats=}"
                change_log.append(item)
                change_ids.append(change_id)
            
        if token.upos == 'ADJ':
            old_feats = token.reconstruct_feats()
            change_id = change_adj(token)
            new_feats = token.reconstruct_feats()
            if new_feats != old_feats:
                item = f"{change_id=}\t{token.sent_id=}\t{token.sent_pos=}\t{token.form=}\t{token.lemma=}\t{old_feats=}\t{new_feats=}"
                change_log.append(item)
                change_ids.append(change_id)
                changed_adj[change_id].add(token.form)
        
    
    change_ids = Counter(change_ids)
    change_log = sorted(change_log, key=lambda a: a.split('\t')[0])

    with open(outfile.rsplit('.', maxsplit=1)[0]+'-changes.log', 'w') as f:
        for k, v in sorted(list(change_ids.items()), key=lambda a: a[0]):
            f.write(f'{k}: {v}\n')
        f.write('\n')
        for k, v in sorted(list(changed_adj.items()), key=lambda a: a[0]):
            f.write(f'{k}: {v}\n')
        f.write('\n')
        for line in change_log:
            f.write(line+'\n')

    print('Writing to', outfile)
    talbanken.write_to_file(outfile)
    print('Wrote', len(talbanken), 'sentences with', sum(change_ids.values()), 'changes')
