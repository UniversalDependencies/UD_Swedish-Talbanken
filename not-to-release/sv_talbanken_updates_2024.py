import udapi
import sys, re
from collections import defaultdict, Counter

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

def write_to_change_log(outfile, change_ids, changed_forms_by_id, change_log):
    change_ids = Counter(change_ids)
    change_log = sorted(change_log, key=lambda a: a.split('\t')[0])
    with open(outfile, 'w') as f:
        for k, v in sorted(list(change_ids.items()), key=lambda a: a[0]):
            f.write(f'{k}: {v}\n')
        f.write('\n')
        for k, v in sorted(list(changed_forms_by_id.items()), key=lambda a: a[0]):
            f.write(f'{k}: {v}\n')
        f.write('\n')
        for line in change_log:
            f.write(line+'\n')
        
def change_den_det_de(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []
    for tok in doc.nodes:
        change_id = None
        old_lemma = tok.lemma
        old_feats = tok.feats.__str__()

        if tok.upos == 'PRON':

            # den är...
            if tok.form.lower() == 'den':
                tok.lemma = 'den'
                tok.feats = {'Definite': 'Def',
                              'Gender': 'Com',
                              'Number': 'Sing',
                              'PronType' :'Prs'}
                change_id = 'pron_den_person'

            # det är...
            elif tok.form.lower() == 'det':
                tok.lemma = 'den'
                tok.feats = {'Definite': 'Def',
                              'Gender': 'Neut',
                              'Number': 'Sing',
                              'PronType' :'Prs'}
                change_id = 'pron_det_person'

            # de är... 
            elif tok.form.lower() == 'de':
                tok.lemma = 'de'
                tok.feats = {'Case': 'Nom',
                              'Definite': 'Def',
                              'Number': 'Plur',
                              'PronType' :'Prs'}
                change_id = 'pron_de_person'

            # ... till dem...
            elif tok.form.lower() == 'dem':
                tok.lemma = 'de'
                tok.feats = {'Case': 'Acc',
                             'Definite': 'Def',
                             'Number': 'Plur',
                             'PronType' :'Prs'}
                change_id = 'pron_dem_person'
            
            # dom är... / till dom...
            elif tok.form.lower() == 'dom':
                tok.lemma = 'de'
                tok.feats = {'Definite': 'Def',
                              'Number': 'Plur',
                              'PronType' :'Prs'}
                change_id = 'pron_dom_person'

            
        elif tok.upos == 'DET':

            # den stora...
            if tok.form.lower() == 'den':
                tok.lemma = 'den'
                tok.feats = {'Definite': 'Def',
                              'Gender': 'Com',
                              'Number': 'Sing',
                              'PronType' :'Art'}
                change_id = 'det_den_article'
                
            # det stora...
            elif tok.form.lower() == 'det':
                tok.lemma = 'den'
                tok.feats = {'Definite': 'Def',
                              'Gender': 'Neut',
                              'Number': 'Sing',
                              'PronType' :'Art'}
                change_id = 'det_det_article'
            
            # de stora...
            elif tok.form.lower() == 'de':
                tok.lemma = 'de'
                tok.feats = {'Definite': 'Def',
                              'Number': 'Plur',
                              'PronType' :'Art'}
                change_id = 'det_de_article'
            
            # dom stora...
            elif tok.form.lower() == 'dom':
                tok.lemma = 'de'
                tok.feats = {'Definite': 'Def',
                              'Number': 'Plur',
                              'PronType' :'Art'}
                change_id = 'det_dom_article'
        
        if change_id != None:
            new_feats = tok.feats.__str__()
            if tok.lemma != old_lemma or new_feats != old_feats:
                
                change_ids.append(change_id)
                changed_forms_by_id[change_id].add(tok.form)
                change_log.append(f"{change_id=}\tsent_id='{tok.root.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\t{old_feats=}\t{new_feats=}\ttext='{tok.root.compute_text()}'")

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_den_det_de_changes.log', change_ids, changed_forms_by_id, change_log)
    
def change_adj_feats(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []
    unchanged = []

    ordinals = ['första', 'tredje', 'fjärde', 'femte', 
                'sjätte', 'sjunde', 'åttonde', 'nionde', 'tionde', 
                'elfte', 'tolfte', 'trettonde', 'fjortonde', 'femtonde', 
                'sextonde', 'sjuttonde', 'artonde', 'nittonde', 'tjugonde', 
                'trettionde', 'fyrtionde', 'femtionde', 'sextionde',
                'sjuttionde', 'åttionde', 'nittionde', 'hundrade', 'tusende', 'miljonte']
    
    roman2swe = {'I': 'första', 'II': 'andra', 'III': 'tredje', 'IV': 'fjärde', 'V': 'femte', 
                 'VI': 'sjätte', 'VII': 'sjunde', 'VIII': 'åttonde', 'IX': 'nionde', 'X': 'tionde', 
                 'XI': 'elfte', 'XII': 'tolfte', 'XIII': 'trettonde', 'XIV': 'fjortonde', 'XV': 'femtonde', 
                 'XVI': 'sextonde', 'XVII': 'sjuttonde', 'XIII': 'artonde', 'XIX': 'nittonde', 'XX': 'tjugonde'}

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_feats = tok.feats.__str__()

            # ovanligt / visst / negativt
            if (tok.lemma[-1] in ['f', 'g', 'l', 'm', 'n', 'p', 'r', 's', 'v']) and (tok.form.lower() == tok.lemma+'t'):
                gender = tok.feats.get('Gender', 'Neut')
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Ind',
                            'Degree': 'Pos',
                            'Gender': gender,
                            'Number': 'Sing'}
                
                change_id = 'adj_utrum+t' 
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing'
            
            # pressad / definerad / integrerad
            elif tok.form.lower().endswith('ad') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Ind',
                            'Degree': 'Pos',
                            'Gender': 'Com',
                            'Number': 'Sing',
                            'Tense': 'Past',
                            'VerbForm': 'Part'}
                
                change_id = 'adj_past_parciple_ad_sing' 
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Com|Number=Sing|Tense=Past|VerbForm=Part'

            # numrerade / väntade / älskade
            elif tok.form.lower().endswith('ade') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):

                # flera numrerade
                if tok.feats.get('Number', None) == 'Plur':
                    tok.feats = {'Case': 'Nom',
                                'Definite': 'Ind',
                                'Degree': 'Pos',
                                'Number': 'Plur',
                                'Tense': 'Past',
                                'VerbForm': 'Part'}
                    
                    change_id = 'adj_past_parciple_ade_plur' 
                    # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Number=Plur|Tense=Past|VerbForm=Part'

                # de/den/det numrerade
                else: 
                    tok.feats = {'Case': 'Nom',
                                'Definite': 'Def',
                                'Degree': 'Pos',
                                'Tense': 'Past',
                                'VerbForm': 'Part'}
                    
                    change_id = 'adj_past_parciple_ade_def' 
                    # nfeats = 'Case=Nom|Definite=Def|Degree=Pos|Tense=Past|VerbForm=Part'
            
            # ordnat / utformat / outnyttjat
            elif tok.form.lower().endswith('at') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Ind',
                            'Degree': 'Pos',
                            'Gender': 'Neut',
                            'Number': 'Sing',
                            'Tense': 'Past',
                            'VerbForm': 'Part'}
                
                change_id = 'adj_past_parciple_at' 
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing|Tense=Past|VerbForm=Part'

            # bästa / största / värste
            elif (tok.form.lower().endswith('sta') or tok.form.lower().endswith('ste')) and tok.feats['Degree'] == 'Sup' and tok.feats['Definite'] != 'Ind':
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Def',
                            'Degree': 'Sup'}
                
                change_id = 'adj_superlative_def'
                # nfeats = 'Case=Nom|Definite=Def|Degree=Sup'
            
            # bäst / störst / värst
            elif tok.form.lower().endswith('st') and tok.feats['Degree'] == 'Sup':
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Ind',
                            'Degree': 'Sup'}
                
                change_id = 'adj_superlative_ind'
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Sup'
                
            # bättre / större / värre
            elif tok.form.lower().endswith('re') and tok.feats['Degree'] == 'Cmp':
                tok.feats = {'Case': 'Nom',
                            'Degree': 'Cmp'}
                
                change_id = 'adj_comperative'
                # nfeats = 'Case=Nom|Degree=Cmp'

            # (den/det) civila / nya / statistiska
            elif not tok.form.lower().endswith('sta') and tok.form.lower() == tok.lemma + 'a' and tok.feats['Definite'] == 'Def':
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Def',
                            'Degree': 'Pos'}
                
                change_id = 'adj_lemma+a_def'
                # nfeats = 'Case=Nom|Definite=Def|Degree=Pos'
            
            # civila / nya / statistiska
            elif not tok.form.lower().endswith('sta') and tok.form.lower() == tok.lemma + 'a' and tok.feats['Number'] == 'Plur':
                tok.feats = {'Case': 'Nom',
                            'Definite': 'Ind',
                            'Degree': 'Pos',
                            'Number': 'Plur'}
                
                change_id = 'adj_lemma+a_plur'
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Number=Plur'
            
            # första / andra / 700:e / III
            elif ((tok.xpos is not None and ('RO' in tok.xpos or tok.xpos == 'ORD') and tok.lemma != 'annan') or 
                  tok.feats['NumType'] == 'Ord' or
                  any(tok.form.lower().endswith(ord) for ord in ordinals) or 
                  re.search(r'^[0-9]+:[ae]$', tok.form) or
                  tok.form in roman2swe.keys()):
                
                tok.feats = {'Case': 'Nom',
                            'Number': 'Sing',
                            'NumType': 'Ord'}
                
                change_id = 'adj_ordinals'
                # nfeats = 'Case=Nom|Number=Sing|NumType=Ord'
    
            # sjungande / dansande / gående
            elif (tok.form.lower().endswith('ande') or tok.form.lower().endswith('ende')) and tok.form.lower() not in ['ende', 'ande']:
                tok.feats = {'Case': 'Nom',
                            'Degree': 'Pos',
                            'Tense': 'Pres',
                            'VerbForm': 'Part'}
                
                change_id = 'adj_pres_participle'
                # nfeats = 'Case=Nom|Degree=Pos|Tense=Pres|VerbForm=Part'
        

            if change_id != None:
                new_feats = tok.feats.__str__()
                if new_feats != old_feats:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{tok.lemma=}\t{old_feats=}\t{new_feats=}\ttext='{tok.root.compute_text()}'")
            else:
                unchanged.append(tok)

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_feats_changes.log', change_ids, changed_forms_by_id, change_log)

    with open(outfile.rsplit('.', maxsplit=1)[0]+'_unchanged_adj.log', 'w') as f:
        unchanged = sorted(unchanged, key=lambda tok: tok.lemma)
        unchanged = [f"sent_id='{tok.address()}'\ntext='{tok.root.compute_text()}'\n{get_conllu(tok)}\n" for tok in unchanged]
        for line in unchanged:
            f.write(line+'\n')
        
def change_adj_ordinal_lemma(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []

    ordinals = ['första', 'tredje', 'fjärde', 'femte', 
                'sjätte', 'sjunde', 'åttonde', 'nionde', 'tionde', 
                'elfte', 'tolfte', 'trettonde', 'fjortonde', 'femtonde', 
                'sextonde', 'sjuttonde', 'artonde', 'nittonde', 'tjugonde', 
                'trettionde', 'fyrtionde', 'femtionde', 'sextionde',
                'sjuttionde', 'åttionde', 'nittionde', 'hundrade', 'tusende', 'miljonte']
    
    gen_ordinals = ['förstas', 'förstes', 'tredjes', 'fjärdes', 'femtes', 
                'sjättes', 'sjundes', 'åttondes', 'niondes', 'tiondes', 
                'elftes', 'tolftes', 'trettondes', 'fjortondes', 'femtondes', 
                'sextondes', 'sjuttondes', 'artondes', 'nittondes', 'tjugondes', 
                'trettiondes', 'fyrtiondes', 'femtiondes', 'sextiondes',
                'sjuttiondes', 'åttiondes', 'nittiondes', 'hundrades', 'tusendes', 'miljontes']
    
    roman2swe = {'I': 'första', 'II': 'andra', 'III': 'tredje', 'IV': 'fjärde', 'V': 'femte', 
                 'VI': 'sjätte', 'VII': 'sjunde', 'VIII': 'åttonde', 'IX': 'nionde', 'X': 'tionde', 
                 'XI': 'elfte', 'XII': 'tolfte', 'XIII': 'trettonde', 'XIV': 'fjortonde', 'XV': 'femtonde', 
                 'XVI': 'sextonde', 'XVII': 'sjuttonde', 'XIII': 'artonde', 'XIX': 'nittonde', 'XX': 'tjugonde'}

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_lemma = tok.lemma

            if (any(tok.form.lower().endswith(ord) for ord in ordinals) or 
                any(tok.form.lower().endswith(ord) for ord in gen_ordinals) or
                re.search(r'^[0-9]+:[ae]$', tok.form)):
                tok.lemma = tok.form.lower()

                change_id = 'adj_ordinal'

            elif tok.form in roman2swe.keys():
                tok.lemma = roman2swe[tok.form]

                change_id = 'adj_roman_ordinal'

            elif tok.form.lower().endswith('andra'): 
                if tok.lemma != 'annan' and tok.feats['Number'] != 'Plur':
                    tok.lemma = 'andra'

                    change_id = 'adj_andra_ordinal'
                else:
                    tok.lemma = 'annan'

                    change_id = 'adj_andra_annan'

            if change_id != None:
                if tok.lemma != old_lemma:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_ordinal_lemma_changes.log', change_ids, changed_forms_by_id, change_log)
  
def change_adj_lemma(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []

    change_dict = {
        'rädda': 'rädd',
        'buggiga': 'buggig',
        'tvåpoliga': 'tvåpolig',
        'nyliga': 'nylig',
        '10-åriga': '10-årig',
        'befullmäktiga': 'befullmäktig',
        'artiga': 'artig',
        'karibiska': 'karibisk',
        'akamenidiska': 'akamenidisk',
        'akemenidiska': 'akemenidisk',
        'yazidiska': 'yazidisk',
        'indiska': 'indisk',
        'sefardiska': 'sefardisk',
        'europeiska': 'europeisk',
        'apuliska': 'apulisk',
        'messeniska': 'messenisk',
        'mähriska': 'mährisk',
        'logistiska': 'logistisk',
        'khitanska': 'khitansk',
        'mayanska': 'mayansk',
        'mykenska': 'mykensk',
        'svenska': 'svensk',
        'avundsjuka': 'avundsjuk',
        'autosomala': 'autosomal',
        'klara': 'klar',
        'förenta': 'förenad',
        'matta': 'matt',
        'lätta': 'lätt',
        'rätta': 'rätt',
        'räta': 'rät',
        'vitas': 'vit',
        'svartas': 'svart',
        'tidigt': 'tidig',
        'löjligt': 'löjlig',
        'otroligt': 'otrolig',
        'husligt': 'huslig',
        'kvalmigt': 'kvalmig',
        'övrigt': 'övrig',
        'sacrococcygealt': 'sacrococcygeal',
        'ont': 'ond',
        'runt': 'rund',
        'gott': 'god',
        'ingrott': 'ingrodd',
        'vått': 'våt',
        'yra': 'yra',
        'reaktionärt': 'reaktionär',
        'rent': 'ren',
        'enorma': 'enorm',
        'givet': 'given',
        'glatt': 'glad',
        'godtagbart': 'godtagbar',
        'limbiska': 'limbisk',
        'litet': 'liten',
        'medfarna': 'medfaren',
        'öppna': 'öppen',
        'använda': 'använd',
        'avröja': 'avröjd',
        'avslita': 'avsliten',
        'bereda': 'beredd',
        'beråda': 'berådd',
        'böja': 'böjd',
        'inbygga': 'inbyggd',
        'indämma': 'indämd',
        'inställa': 'inställd',
        'kringskära': 'kringskären',
        'kränka': 'kränkt',
        'lära': 'lärd',
        'ligga': 'låg',
        'planlägga': 'planlagd',
        'skärpa': 'skärpt',
        'slutföra': 'slutförd',
        'städja': 'stadd',
        'trycka': 'tryckt',
        'tära': 'tärd',
        'tömma': 'tömd',
        'undertrycka': 'undertryckt',
        'uppblöta': 'uppblött',
        'upphäva': 'upphävd',
        'upplyfta': 'upplyft',
        'upplysa': 'upplyst',
        'upplåsa': 'upplåst',
        'uppsträcka': 'uppsträckt',
        'uppvända': 'uppvänd',
        'utställa': 'utställd',
        'utsöka': 'utsökt',
        'övergöda': 'övergödd',
        'spänna_för': 'förspänd'
    }

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_lemma = tok.lemma

            if tok.lemma.lower() in change_dict:
                tok.lemma = change_dict[tok.lemma.lower()]
                change_id = 'adj_lemma'

            if change_id != None:
                if tok.lemma != old_lemma:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

def change_adj_participal_lemma(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []

    past_exceptions = {'smält': lambda form: form,
                       'smälta': lambda form: form[:-1],
                       'smältas': lambda form: form[:-2],
                       'dött': lambda form: form[-2] + 'd',
                       'skött': lambda form: form,
                       'skötta': lambda form: form[:-1],
                       'sköttas': lambda form: form[:-2]}

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_lemma = tok.lemma
            
            if tok.feats['VerbForm'] == 'Part':
                # if there the adjective ends in an obvious present participle ending, but for some reason has been classified as 
                # past tense, we fix it before we fix the lemma. 
                if any(tok.form.endswith(end) for end in ['ande', 'andes', 'ende', 'endes']) and tok.feats['Tense'] != 'Pres':
                    tok.feats['Tense'] = 'Pres'

                if tok.feats['Tense'] == 'Pres':
                    # nominative
                    if tok.form.lower().endswith('ande') or tok.form.lower().endswith('ende'):
                        tok.lemma = tok.form.lower()
                        change_id = 'adj_pres_nom_participal_lemma'

                    # genetive
                    elif tok.form.lower().endswith('andes') or tok.form.lower().endswith('endes'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = 'adj_pres_gen_participal_lemma'
      
                elif tok.feats['Tense'] == 'Past':              
                    # for exceptions (död, smält, skött)
                    if any(tok.form.lower().endswith(end) for end in past_exceptions.keys()):
                        key, rule = sorted([(key, rule) for key, rule in past_exceptions.items() if tok.form.lower().endswith(key)], key=lambda item: len(item[0]))[-1]
                        tok.lemma = rule(tok.form.lower())

                        change_id = f'adj_past_participal_exception_{key}_lemma'

                    # jagad / bruten
                    elif tok.form.lower().endswith('d') or tok.form.lower().endswith('en'):
                        tok.lemma = tok.form.lower()
                        change_id = 'adj_past_participal_utrum_sing_lemma'

                    # jagade
                    elif tok.form.lower().endswith('ade'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = 'adj_past_participal_ade_lemma'

                    # jagades
                    elif tok.form.lower().endswith('ades'):
                        tok.lemma = tok.form.lower()[:-2]
                        change_id = 'adj_past_participal_ades_lemma'

                    # jagat
                    elif tok.form.lower().endswith('at'):
                        tok.lemma = tok.form.lower()[:-1] + 'd'
                        change_id = 'adj_past_participal_at_lemma'

                    # brutet
                    elif tok.form.lower().endswith('et'):
                        tok.lemma = tok.form.lower()[:-1] + 'n'
                        change_id = 'adj_past_participal_et_lemma'

                    # bortsett
                    elif tok.form.lower().endswith('ett'):
                        tok.lemma = tok.form.lower()[:-2] + 'dd'
                        change_id = 'adj_past_participal_ett_lemma'

                    # fortsatt
                    elif tok.form.lower().endswith('att'):
                        tok.lemma = tok.form.lower()
                        change_id = 'adj_past_participal_att_lemma'
                    
                    # fortsatta
                    elif tok.form.lower().endswith('atta'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = 'adj_past_participal_atta_lemma'

                    # betalda
                    elif tok.form.lower().endswith('da'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = 'adj_past_participal_da_lemma'

                    # betaldas
                    elif tok.form.lower().endswith('das'):
                        tok.lemma = tok.form.lower()[:-2]
                        change_id = 'adj_past_participal_da_lemma'

                    # brutna / brutne
                    elif tok.form.lower().endswith('na') or tok.form.lower().endswith('ne'):
                        tok.lemma = tok.form.lower()[:-2] + 'en'
                        change_id = 'adj_past_participal_nae_lemma'
                    
                    # brutnas / brutnes
                    elif tok.form.lower().endswith('nas') or tok.form.lower().endswith('nes'):
                        tok.lemma = tok.form.lower()[:-3] + 'en'
                        change_id = 'adj_past_participal_naes_lemma'

                    # gift / kokt / klippt / låst
                    elif tok.form.lower()[-2] in ['f', 'k', 'p', 's'] and tok.form.lower().endswith('t'):
                        tok.lemma = tok.form.lower()
                        change_id = 'adj_past_participle_unvoiced_sing_lemma'
                    
                    # gifta / kokta / klippta / låsta
                    elif tok.form.lower()[-3] in ['f', 'k', 'p', 's'] and tok.form.lower().endswith('ta'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = 'adj_past_participle_unvoiced_plur_lemma'

                    # framlagt / höjt / särskilt / bestämt / känt / kört / framhävda
                    elif tok.form.lower()[-2] in ['g', 'j',  'l', 'm', 'n', 'r', 'v'] and tok.form.lower().endswith('t'):
                        tok.lemma = tok.form.lower()[:-1] + 'd'
                        change_id = 'adj_past_participle_voiced_sing_lemma'
                    
                    # sett / fött 
                    elif tok.form.lower().endswith('tt'):
                        tok.lemma = tok.form.lower()[:-2] + 'dd'

        
            else:
                
                if (tok.form.lower().endswith('ande') or tok.form.lower().endswith('ende')) and (tok.form.lower() != 'ende' and tok.form.lower() != 'ande'):
                        tok.lemma = tok.form.lower()
                        change_id = 'adj_pres_nom_participal_lemma'

                # genetive
                elif (tok.form.lower().endswith('andes') or tok.form.lower().endswith('endes')) and tok.form.lower() != 'endes' and tok.form.lower() != 'andes':
                    tok.lemma = tok.form.lower()[:-1]
                    change_id = 'adj_pres_gen_participal_lemma'

                # numrerad / väntad / älskad
                elif tok.form.lower().endswith('ad') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
                    tok.lemma = tok.form.lower()
                    
                    change_id = 'adj_past_parciple_ad_sing' 
                    

                # numrerade / väntade / älskade
                elif tok.form.lower().endswith('ade') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
                    tok.lemma = tok.form.lower()[:-1]
                    change_id = 'adj_past_parciple_ade_plur'
                
                # ordnat / utformat / outnyttjat
                elif tok.form.lower().endswith('at') and ((tok.lemma.endswith('a')) or (tok.lemma.endswith('d'))):
                    tok.lemma = tok.form.lower()[:-1] + 'd'
                
                    change_id = 'adj_past_parciple_at' 

            if change_id != None:
                if tok.lemma != old_lemma:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_participal_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

def change_adj_exception_lemma(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []


    hard_rules = {'övre': 'övre',
                  'undre': 'undre',
                  'inre': 'inre',
                  'yttre': 'yttre',
                  'översta': 'övre',
                  'understa': 'undre',
                  'innersta': 'inre',
                  'yttersta': 'yttre',

                  'högra': 'höger',
                  'vänstra': 'vänster',
                  'högraste': lambda form: form[:-3],
                  'vänstraste': lambda form: form[:-3]}
    
    flexible_rules = {'södra': lambda form: form,
                      'västra': lambda form: form,
                      'östra': lambda form: form,
                      'norra': lambda form: form,}

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_lemma = tok.lemma

            if tok.form.lower() in hard_rules.keys():
                tok.lemma = hard_rules[tok.form.lower()]
                change_id = f'adj_exception_lemma'

            elif tok.form.endswith('s') and tok.form.lower()[:-1] in hard_rules.keys():
                tok.lemma = hard_rules[tok.form.lower()[:-1]]
                change_id = f'adj_exception_lemma'

            elif any((tok.form.lower().endswith(end)) for end in flexible_rules.keys()):
                key, rule = sorted([(key, rule) for key, rule in flexible_rules.items() if tok.form.lower().endswith(key)], key=lambda item: len(item[0]))[-1]
                tok.lemma = rule(tok.form.lower())
                change_id = f'adj_exception_lemma'
                
            elif any((tok.form.lower().endswith(end + 's')) for end in flexible_rules.keys()):
                key, rule = sorted([(key, rule) for key, rule in flexible_rules.items() if tok.form.lower().endswith(key + 's')], key=lambda item: len(item[0]))[-1]
                tok.lemma = rule(tok.form[:-1].lower())
                change_id = f'adj_exception_lemma'

            if change_id != None:
                if tok.lemma != old_lemma:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_exception_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

def change_abbr_lemma(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []

    

    for tok in doc.nodes:
        if tok.feats['Abbr'] == 'Yes':
            change_id = None
            old_lemma = tok.lemma

            if tok.upos == 'ADJ':
                if tok.form.lower() in ['kungl', 'kungl.']:
                    tok.lemma = 'kunglig'
                elif tok.form.lower() in ['s.k.', 's k']:
                    tok.lemma = 'så_kallad'
                elif tok.form.lower() in ['teol', 'teol.']:
                    tok.lemma = 'teologie'
                elif tok.form.lower() in ['fil', 'fil.']:
                    tok.lemma = 'filosofie'
                elif tok.form.lower() in ['st.', 's:t']:
                    tok.lemma = 'sankt'
                elif tok.form.lower() in ['med', 'med.']:
                    tok.lemma = 'medicine'
                elif tok.form.lower() in ['resp', 'resp.']:
                    tok.lemma = 'respektive'
                elif tok.form.lower() in ['ev', 'ev.']:
                    tok.lemma = 'eventuell'
            
                if old_lemma != tok.lemma:
                    change_id = 'abbr_adj'
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_abbr_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

def manual_changes(doc, outfile, manual_changes_document):
    change_log = list()
    nodes = list(doc.nodes)
    id2node = {node.address(): i for i, node in enumerate(nodes)}
    

    
    with open(manual_changes_document, 'r') as f:
        for line in f:
            if line.startswith('id='):
                node_id = line.strip().split('=')[-1]
            elif line.strip():
                line = line.strip().split('\t')
                assert len(line) == 10
                (tok_id, form, lemma, upos, xpos, 
                    feats, head, deprel, deps, misc) = line
                
                
                node_idx = id2node.get(node_id, None)
                if node_idx:
                    node = nodes[node_idx]
                
                    old_node = get_conllu(node)

                    node.form = form
                    node.lemma = lemma
                    node.upos = upos
                    node.xpos = xpos
                    node.feats = feats
                    node.deprel = deprel
                    node.raw_deps = deps
                    node.misc = misc

                    new_parent = nodes[id2node[node_id.split('#')[0]+f'#{head}']]

                    if node.parent is not new_parent:
                        node.parent = new_parent

                    new_node = get_conllu(node)

                    if new_node != old_node:
                        change_log.append(f"{node_id=}\ntext='{node.root.compute_text()}'\n{old_node}\n{new_node}\n")
                    
    if change_log:
        with open(outfile.rsplit('.', maxsplit=1)[0]+'_manual_fixes_changes.log', 'w') as f:
            for line in change_log:
                f.write(line+'\n')


if __name__ == '__main__':
    
    if len(sys.argv) == 3:
        infile, outfile = sys.argv[1:]
        manual_changes_doc = None
    elif len(sys.argv) == 4:
        infile, outfile, manual_changes_doc = sys.argv[1:]
    else:
        print('Usage: python3 script conllu_treebank output_filepath manual_fixes_document')
    
    print('Reading', infile)
    doc = udapi.Document(infile)

    change_adj_lemma(doc, outfile)
    change_adj_ordinal_lemma(doc, outfile)
    change_adj_participal_lemma(doc, outfile)
    change_adj_exception_lemma(doc, outfile)
    change_abbr_lemma(doc, outfile)

    change_den_det_de(doc, outfile)
    # change_adj_feats(doc, outfile)
    if manual_changes_doc:
        manual_changes(doc, outfile, manual_changes_doc)

    doc.store_conllu(filename=outfile)

