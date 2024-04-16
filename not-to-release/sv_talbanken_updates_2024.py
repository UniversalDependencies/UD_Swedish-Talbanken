import udapi
import sys, re
import argparse
from collections import defaultdict, Counter


SVART_ADJ = ['gravid', 'orange', 'mycket', 'höger', 'vänster', 'separat', 'moderat', 
             'desperat', 'privat', 'kokhet', 'konkret', 'diskret', 'indiskret', 
             'gift', 'omgift', 'ogift', 'nygift', 'oskift', 'upplyft', 'implicit', 
             'kompakt', 'abstrakt', 'exakt', 'tryckt', 'undertryckt', 'uttryckt', 
             'omtyckt', 'knäckt', 'dödsförskräckt', 'spräckt', 'uppsträckt', 'utsträckt', 'täckt', 
             'oupptäckt', 'perfekt', 'solblekt', 'direkt', 'indirekt', 'korrekt', 
             'smörstekt', 'strikt', 'ovikt', 'sankt', 'sakrosankt', 'kränkt', 'oinskränkt', 
             'sänkt', 'tänkt', 'genomtänkt', 'misstänkt', 'kokt', 'skalkokt', 'okokt', 
             'märkt', 'dödsmärkt', 'utmärkt', 'stärkt', 'styvstärkt', 'ihopläkt', 
             'undersökt', 'utsökt', 'halt', 'salt', 'stolt', 'osmält', 'extravagant', 
             'elegant', 'arrogant', 'bekant', 'välbekant', 'obekant', 'brant', 'tolerant', 
             'intressant', 'ointressant', 'militant', 'bastant', 'konstant', 'irrelevant', 
             'trebent', 'fyrbent', 'independent', 'intelligent', 'ointelligent', 'förment', 
             'permanent', 'indifferent', 'latent', 'kompetent', 'inkompetent', 'konsekvent', 
             'tungsint', 'styvsint', 'gladlynt', 'vidsynt', 'sällsynt', 'närsynt', 
             'kortsynt', 'bevänt', 'snökrönt', 'insvept', 'klippt', 'sönderklippt', 
             'skärpt', 'smart', 'svart', 'korpsvart', 'alert', 'kort', 'bjärt', 'fast', 
             'handfast', 'rest', 'högrest', 'trist', 'sist', 'främst', 'robust', 
             'förtjust', 'belyst', 'månbelyst', 'upplyst', 'djupfryst', 'tyst', 
             'stadfäst', 'lättläst', 'låst', 'uppblåst', 'inlåst', 'upplåst', 'löst', 
             'svårlöst', 'platt', 'matt', 'satt', 'nedsatt', 'djävulsbesatt', 
             'sysselsatt', 'fullsatt', 'omsatt', 'sammansatt', 'bosatt', 'typsatt', 
             'översatt', 'motsatt', 'fortsatt', 'utsatt', 'förutsatt', 'komplett', 
             'kvitt', 'blott', 'lätt', 'mätt', 'rätt', 'orätt', 'upprätt', 'skött', 
             'välskött', 'uppblött', 'nött', 'slätnött', 'trött', 'morgontrött', 
             'krigstrött', 'akut', 'absolut', 'kortväxt']
             
             # OSÄKRA_______________________________________________________
             # 'gravid', 'orange', 'oskift', 'halt', 'mycket'
             

BRA_ADJ = ['bra', 'enda', 'fel', 'enstaka', 'ringa', 'extra', 'många', 'bra', 
           'tiptop', 'udda', 'inrikes', 'långväga', 'förtida', 'gratis', 
           'allsköns', 'framtida', 'slut', 'illa', 'noga', 'urminnes', 
           'gängse', 'stilla', 'inbördes', 'äkta', 'nutida', 'annorlunda', 
           'medeltida', 'omaka', 'yttre', 'samma', 'jättebra', 'samtida', 
           'övre', 'stackars', 'fjärran', 'rosa', 'öde', 'jävla', 'jäkla', 
           'laxrosa', 'lila', 'ense', 'brunrosa', 'nästa', 'urarva', 'varse',
           
           # PARTICIP-LIKNANDE________________________________________
           'hemmavarande', 'nedanstående', 'ensamstående', 'främmande', 
           'otillfredsställande', 'långtgående', 'framstående', 
           'högtsmällande', 'enastående', 'påfallande', 'norrgående', 
           'dåvarande', 'högavkastande', 'arbetskrävande', 'närstående', 
           'avsaktande', 'yrkesutövande', 'ansvarskännande', 'förutvarande', 
           'medkännande', 'närliggande', 'olycksbådande', 'iögonfallande', 
           'utomstående', 'plattformsoberoende', 'spännande', 'gyllene', 
           'välmenande', 'uppåtsipprande', 'växtsaftsliknande', 
           'kerubliknande', 'välgörande', 'häpnadsväckande', 
           'stillasittande', 'enahanda', 'självblandande', 'självreglerande', 
           'filoberoende', 'kalkylbladsliknande', 'förbiilande', 
           'omkringliggande', 'utstående', 'nationsskapande', 'uppfriskande', 
           'havande', 'nattvagabonderande', 'öronbedövande', 'svettglänsande', 
           'halsbrytande', 'motbjudande', 'överseende', 'förtroendeväckande', 
           'ihållande', 'hittillsvarande', 'gränsöverskridande', 'påfrestande', 
           'inkomstskapande', 'överreglerande', 'iögonenfallande', 
           'betryggande', 'omtumlande', 'verklighetsfrämmande', 'hästliknande', 
           'intetsägande', 'stillastående', 'beklämmande', 'sjögående', 
           'dödsliknande', 'vitblänkande', 'förestående']

ENGLISH_ADJ = ['first', 'south', 'royal', 'shaky', 'wild', 'golden', 
               'extensible', 'wide', 'grand', 'visual', 'advertising', 
               'arabic', 'brave', 'free', 'american', 'strange', 'talking', 
               'new', 'central', 'advanced', 'simple', 'boiling', 'economic',
               'european', 'intermittent', 'pressurized', 'swedish', 'united', 
               'national', 'international', 'north', 'strange', 'civil', 
               'breaking', 'environmental', 'political', 'universal']

FOREIGN = ['priori', 'restante']

OVERSPEC = {'diverse': {'Case': 'Nom', 'Definite': None, 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},
            'förenta': {'Case': 'Nom', 'Definite': None, 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},
            'flera': {'Case': 'Nom', 'Definite': None, 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},
            'fler': {'Case': 'Nom', 'Definite': None, 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},

            'båda': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},
            
            'desamma': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},

            'ljusan': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},
            'sakta': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},
            'lika': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},

            'kvitt': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'lite': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'sinom': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'redo': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'bevänt': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            
            'södra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'norra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'västra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'östra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'sydvästra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'sydöstra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'nordvästra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},
            'nordöstra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': None},

            'rädd': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},
            'humanoid': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},
            
            'sankta': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},
            'förra': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},
            'ena': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},

            'ene': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},
            'ende': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},

            'blotta': {'Case': 'Nom', 'Definite': 'Def', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},

            'lilla': {'Case': 'Nom', 'Definite': None, 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},
            'pyttelilla': {'Case': 'Nom', 'Definite': None, 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},

            'liten': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},
            'pytteliten': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},

            'litet': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'},
            'pyttelitet': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'},   

            # words that didn't fit the rules_____________________________________________________________

            'tekniskt-teoretiskt': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'},
            
            'så': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': 'Sing'},
            'sån': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},
            'sånt': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'},
            'såna': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': None, 'Number': 'Plur'},

            'mantalskriven': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Com', 'Number': 'Sing'},
            'villkorstyrt': {'Case': 'Nom', 'Definite': 'Ind', 'Degree': 'Pos', 'Gender': 'Neut', 'Number': 'Sing'},
            
            }



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
    
    roman_num = ['I', 'II', 'III', 'IV', 'V', 
                 'VI', 'VII', 'VIII', 'IX', 'X', 
                 'XI', 'XII', 'XIII', 'XIV', 'XV', 
                 'XVI', 'XVII', 'XIII', 'XIX', 'XX']

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_lemma = tok.lemma.lower().lower()

            if (any(tok.form.lower().endswith(ord) for ord in ordinals) or
                re.search(r'^[0-9]+:[ae]$', tok.form)):
                tok.lemma = tok.form.lower()

                change_id = 'adj_ordinal'

            elif any(tok.form.lower().endswith(ord) for ord in gen_ordinals):
                tok.lemma = tok.form.lower()[:-1]

                change_id = 'adj_gen_ordinal'

            elif tok.form.lower().endswith('förste') or tok.form.lower().endswith('förstes'):
                tok.lemma = 'första'

                change_id = 'adj_förste'

            elif tok.form in roman_num:
                tok.lemma = tok.form

                change_id = 'adj_roman_ordinal'

            elif tok.form.lower().endswith('andra'): 
                if tok.lemma.lower() != 'annan' and tok.feats['Number'] != 'Plur':
                    tok.lemma = 'andra'

                    change_id = 'adj_andra_ordinal'
                else:
                    tok.lemma = 'annan'

                    change_id = 'adj_andra_annan'

            elif str.isnumeric(tok.form) and (tok.xpos == 'ORD' or 'RO' in tok.xpos):
                tok.lemma = tok.form + ':e' if tok.form[-1] != '1' else ':a'

                change_id = 'adj_dates_ordinal'

            if change_id != None:
                if tok.lemma.lower() != old_lemma:
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
        'spänna_för': 'förspänd',
        'hemskt': 'hemsk',
        'lika': 'lik',
        'sån': 'sådan',
    }

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_lemma = tok.lemma.lower().lower()

            if tok.lemma.lower() in change_dict:
                tok.lemma = change_dict[tok.lemma.lower()]
                change_id = 'adj_lemma'

            if change_id != None:
                if tok.lemma.lower() != old_lemma:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

def change_participle_lemma(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []

    past_exceptions = {'smält': lambda form: form,
                       'smälta': lambda form: form[:-1],
                       'smältas': lambda form: form[:-2],
                       'dött': lambda form: form[:-2] + 'd',
                       'skött': lambda form: form,
                       'skötta': lambda form: form[:-1],
                       'sköttas': lambda form: form[:-2],
                       'mätt': lambda form: form,
                       'mätta': lambda form: form[:-1],
                       'mättas': lambda form: form[:-2],
                       }
    
    typos = {'nurvarande': 'nuvarande', 
             'mantalskriven': 'mantalsskriven'}

    for tok in doc.nodes:
        if tok.upos in ('ADJ', 'VERB'):
            change_prefix = 'adj' if tok.upos == 'ADJ' else 'verb'
            change_id = None
            old_lemma = tok.lemma.lower().lower()
            
            if tok.feats['VerbForm'] == 'Part' or 'aux:pass' in [child.deprel for child in tok.children if child.lemma.lower() == 'bli']:
                # if there the adjective ends in an obvious present participle ending, but for some reason has been classified as 
                # past tense, we fix it before we fix the lemma. 
                if any(tok.form.endswith(end) for end in ['ande', 'andes', 'ende', 'endes']):
                    tok.feats['Tense'] = 'Pres'
                else:
                    tok.feats['Tense'] = 'Past'

                if tok.form.lower() in typos:
                    # print('found:', tok.form.lower())
                    tok.lemma = typos[tok.form.lower()]
                    tok.feats['Typo'] = 'Yes'

                    change_id = f'{change_prefix}_typo_participle_exception_{tok.form.lower()}_lemma'

                elif tok.feats['Tense'] == 'Pres':
                    # nominative
                    if tok.form.lower().endswith('ande') or tok.form.lower().endswith('ende'):
                        tok.lemma = tok.form.lower()
                        change_id = f'{change_prefix}_pres_nom_participle_lemma'

                    # genetive
                    elif tok.form.lower().endswith('andes') or tok.form.lower().endswith('endes'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = f'{change_prefix}_pres_gen_participle_lemma'
      
                elif tok.feats['Tense'] == 'Past':              
                    # for exceptions (död, smält, skött)
                    if any(tok.form.lower().endswith(end) for end in past_exceptions):
                        # print('found:', tok.form.lower())
                        key, rule = sorted(([(key, rule) for key, rule in past_exceptions.items() if tok.form.lower().endswith(key)]), key=lambda item: len(item[0]))[-1]
                        tok.lemma = rule(tok.form.lower())
        
                        change_id = f'{change_prefix}_past_participle_exception_{key}_lemma'

                    # jagad / bruten
                    elif tok.form.lower().endswith('d') or tok.form.lower().endswith('en'):
                        tok.lemma = tok.form.lower()
                        change_id = f'{change_prefix}_past_participle_utrum_sing_lemma'

                    # jagade
                    elif tok.form.lower().endswith('ade'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = f'{change_prefix}_past_participle_ade_lemma'

                    # jagades
                    elif tok.form.lower().endswith('ades'):
                        tok.lemma = tok.form.lower()[:-2]
                        change_id = f'{change_prefix}_past_participle_ades_lemma'

                    # jagat
                    elif tok.form.lower().endswith('at'):
                        tok.lemma = tok.form.lower()[:-1] + 'd'
                        change_id = f'{change_prefix}_past_participle_at_lemma'

                    # brutet
                    elif tok.form.lower().endswith('et'):
                        tok.lemma = tok.form.lower()[:-1] + 'n'
                        change_id = f'{change_prefix}_past_participle_et_lemma'

                    # bortsett
                    elif tok.form.lower().endswith('ett'):
                        tok.lemma = tok.form.lower()[:-2] + 'dd'
                        change_id = f'{change_prefix}_past_participle_ett_lemma'

                    # fortsatt
                    elif tok.form.lower().endswith('att'):
                        tok.lemma = tok.form.lower()
                        change_id = f'{change_prefix}_past_participle_att_lemma'
                    
                    # fortsatta
                    elif tok.form.lower().endswith('atta'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = f'{change_prefix}_past_participle_atta_lemma'

                    # betalda
                    elif tok.form.lower().endswith('da'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = f'{change_prefix}_past_participle_da_lemma'

                    # betaldas
                    elif tok.form.lower().endswith('das'):
                        tok.lemma = tok.form.lower()[:-2]
                        change_id = f'{change_prefix}_past_participle_da_lemma'

                    # brutna / brutne
                    elif tok.form.lower().endswith('na') or tok.form.lower().endswith('ne'):
                        tok.lemma = tok.form.lower()[:-2] + 'en'
                        change_id = f'{change_prefix}_past_participle_nae_lemma'
                    
                    # brutnas / brutnes
                    elif tok.form.lower().endswith('nas') or tok.form.lower().endswith('nes'):
                        tok.lemma = tok.form.lower()[:-3] + 'en'
                        change_id = f'{change_prefix}_past_participle_naes_lemma'

                    # gift / kokt / klippt / låst
                    elif tok.form.lower()[-2] in ['f', 'k', 'p', 's'] and tok.form.lower().endswith('t'):
                        tok.lemma = tok.form.lower()
                        change_id = f'{change_prefix}_past_participle_unvoiced_sing_lemma'
                    
                    # gifta / kokta / klippta / låsta
                    elif tok.form.lower()[-3] in ['f', 'k', 'p', 's'] and tok.form.lower().endswith('ta'):
                        tok.lemma = tok.form.lower()[:-1]
                        change_id = f'{change_prefix}_past_participle_unvoiced_plur_lemma'

                    # framlagt / höjt / särskilt / bestämt / känt / kört / framhävda
                    elif tok.form.lower()[-2] in ['g', 'j',  'l', 'm', 'n', 'r', 'v'] and tok.form.lower().endswith('t'):
                        tok.lemma = tok.form.lower()[:-1] + 'd'
                        change_id = f'{change_prefix}_past_participle_voiced_sing_lemma'
                    
                    # sett / fött 
                    elif tok.form.lower().endswith('tt'):
                        tok.lemma = tok.form.lower()[:-2] + 'dd'
                        change_id = f'{change_prefix}_past_participle_tt_lemma'

            elif tok.upos == 'ADJ':
                if (tok.form.lower().endswith('ande') or tok.form.lower().endswith('ende')) and (tok.form.lower() != 'ende' and tok.form.lower() != 'ande'):
                        tok.lemma = tok.form.lower()
                        change_id = 'adj_pres_nom_participle_lemma'

                # genetive
                elif (tok.form.lower().endswith('andes') or tok.form.lower().endswith('endes')) and tok.form.lower() != 'endes' and tok.form.lower() != 'andes':
                    tok.lemma = tok.form.lower()[:-1]
                    change_id = 'adj_pres_gen_participle_lemma'

                # numrerad / väntad / älskad
                elif tok.form.lower().endswith('ad') and ((tok.lemma.lower().endswith('a')) or (tok.lemma.lower().endswith('d'))):
                    tok.lemma = tok.form.lower()
                    change_id = 'adj_past_participle_ad_sing' 
                    

                # numrerade / väntade / älskade
                elif tok.form.lower().endswith('ade') and ((tok.lemma.lower().endswith('a')) or (tok.lemma.lower().endswith('d'))):
                    tok.lemma = tok.form.lower()[:-1]
                    change_id = 'adj_past_participle_ade_plur'
                
                # ordnat / utformat / outnyttjat
                elif tok.form.lower().endswith('at') and ((tok.lemma.lower().endswith('a')) or (tok.lemma.lower().endswith('d'))):
                    tok.lemma = tok.form.lower()[:-1] + 'd'
                    change_id = 'adj_past_participle_at' 

            if change_id != None:
                if tok.lemma.lower() != old_lemma:
                    change_ids.append(change_id)
                    changed_forms_by_id[change_id].add(tok.form)
                    change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_participle_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

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
            old_lemma = tok.lemma.lower()

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
                if tok.lemma.lower() != old_lemma:
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
            old_lemma = tok.lemma.lower()

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

                change_id = 'abbr_adj'

            elif tok.upos == 'ADV':
                if tok.form.lower() in ['bl a', 'bl.a.']:
                    tok.lemma = 'bland_annat'
                elif tok.form.lower() in ['ca', 'c:a']:
                    tok.lemma = 'circa'
                elif tok.form.lower() in ['d v s', 'd.v.s.', 'dvs', 'dvs.']:
                    tok.lemma = 'det_vill_säga'
                elif tok.form.lower() in ['e d', 'e.d.']:
                    tok.lemma = 'eller_dylikt'
                elif tok.form.lower() in ['e.kr.']:
                    tok.lemma = 'efter_kristus'
                elif tok.form.lower() in ['f.kr.']:
                    tok.lemma = 'före_kristus'
                elif tok.form.lower() in ['eg']:
                    tok.lemma = 'exempli_gratia'
                elif tok.form.lower() in ['etc', 'etc.']:
                    tok.lemma = 'et_cetera'
                elif tok.form.lower() in ['f', 'f.']:
                    tok.lemma = 'och_följande_sida'
                elif tok.form.lower() in ['ff', 'ff.']:
                    tok.lemma = 'och_följande_sidor'    
                elif tok.form.lower() in ['f n', 'f.n.']:
                    tok.lemma = 'för_närvarande'
                elif tok.form.lower() in ['fr o m', 'fr.o.m.']:
                    tok.lemma = 'från_och_med'
                elif tok.form.lower() in ['m fl', 'm.fl.', 'm.fl']:
                    tok.lemma = 'med_flera'
                elif tok.form.lower() in ['m m', 'm.m.', 'm.m']:
                    tok.lemma = 'med_mera'
                elif tok.form.lower() in ['osv', 'o s v', 'o.s.v.', 'o.s.v']:
                    tok.lemma = 'och_så_vidare'
                elif tok.form.lower() in ['resp', 'resp.']:
                    tok.lemma = 'respektive'
                elif tok.form.lower() in ['t ex', 't.ex.', 't.ex']:
                    tok.lemma = 'till_exempel'
                elif tok.form.lower() in ['resp', 'resp.']:
                    tok.lemma = 'respektive'
                elif tok.form.lower() in ['t o m', 't.o.m.', 't.o.m']:
                    tok.lemma = 'till_och_med'
                elif tok.form.lower() in ['t v', 't.v.', 't.v']:
                    tok.lemma = 'till_vänster'
                elif tok.form.lower() in ['t h', 't.h.', 't.h']:
                    tok.lemma = 'till_höger'
                
                change_id = 'abbr_adv'
                     
            elif tok.upos == 'NOUN':
                if tok.form.lower() in ['%', 'proc', 'proc.']:
                    tok.lemma = 'procent'
                elif tok.form.lower() in ['°']:
                    tok.lemma = 'grader'
                elif tok.form.lower() in ['bb']:
                    tok.lemma = 'barnsbördsavdelning'
                elif tok.form.lower() in ['bnp']:
                    tok.lemma = 'bruttonationalprodukt'
                elif tok.form.lower() in ['cal']:
                    tok.lemma = 'kalori'
                elif tok.form.lower() in ['c']:
                    tok.lemma = 'celsius'
                elif tok.form.lower() in ['cl']:
                    tok.lemma = 'centiliter'
                elif tok.form.lower() in ['cm']:
                    tok.lemma = 'cm'
                elif tok.form.lower() in ['aids']:
                    tok.lemma = 'förvärvat_immunbristsyndrom'
                elif tok.form.lower() in ['ddt']:
                    tok.lemma = 'diklordifenyltrikloretan'
                elif tok.form.lower() in ['dl']:
                    tok.lemma = 'deciliter'
                elif tok.form.lower() in ['dl']:
                    tok.lemma = 'deciliter'
                elif tok.form.lower() in ['doc', 'doc.']:
                    tok.lemma = 'docent'
                elif tok.form.lower() in ['dr', 'dr.']:
                    tok.lemma = 'doktor'
                elif tok.form.lower() in ['e.kr.']:
                    tok.lemma = 'efter_kristus'
                elif tok.form.lower() in ['f.kr.']:
                    tok.lemma = 'före_kristus'
                elif tok.form.lower() in ['f.v.t.', 'fvt']:
                    tok.lemma = 'före_vår_tideräkning'
                elif tok.form.lower() in ['ff', 'ff.']:
                    tok.lemma = 'och_följande_sidor'   
                elif tok.form.lower() in ['fig', 'fig.']:
                    tok.lemma = 'figur'
                elif tok.form.lower() in ['g', 'gr']:
                    tok.lemma = 'gram'
                elif tok.form.lower() in ['hr']:
                    tok.lemma = 'herr' 
                elif tok.form.lower() in ['i']:
                    tok.lemma = 'infanteribrigad'
                elif tok.form.lower() in ['jan', 'jan.']:
                    tok.lemma = 'januari'
                elif tok.form.lower() in ['kap', 'kap.']:
                    tok.lemma = 'kapitel'
                elif tok.form.lower() in ['kg']:
                    tok.lemma = 'kilogram'
                elif tok.form.lower() in ['kl', 'kl.']:
                    tok.lemma = 'klockan'
                elif tok.form.lower() in ['km']:
                    tok.lemma = 'kilometer'
                elif tok.form.lower() in ['kor']:
                    tok.lemma = 'korinthierbrevet'
                elif tok.form.lower() in ['kpi']:
                    tok.lemma = 'konsumentprisindex'
                elif tok.form.lower() in ['kr']:
                    tok.lemma = 'krona'
                elif tok.form.lower() in ['kvkm']:
                    tok.lemma = 'kvadratkilometer'
                elif tok.form.lower() in ['kvm']:
                    tok.lemma = 'kvadratmeter'
                elif tok.form.lower() in ['lic', 'lic.']:
                    tok.lemma = 'licentiat'
                elif tok.form.lower() in ['kvkm']:
                    tok.lemma = 'kvadratkilometer'
                elif tok.form.lower() in ['lsd']:
                    tok.lemma = 'lysergsyradietylamid'
                elif tok.form.lower() in ['m']:
                    tok.lemma = 'meter'
                elif tok.form.lower() in ['m3/s', 'm3/sek']:
                    tok.lemma = 'kubikmeter_per_sekund'
                elif tok.form.lower() in ['maj:t']:
                    tok.lemma = 'majestät'
                elif tok.form.lower() in ['md']:
                    tok.lemma = 'miljard'
                elif tok.form.lower() in ['mg']:
                    tok.lemma = 'miligram'
                elif tok.form.lower() in ['milj', 'mn']:
                    tok.lemma = 'miljon'
                elif tok.form.lower() in ['mm']:
                    tok.lemma = 'milimeter'
                elif tok.form.lower() in ['mos.']:
                    tok.lemma = 'moseboken'
                elif tok.form.lower() in ['mr', 'mr.']:
                    tok.lemma = 'mister'
                elif tok.form.lower() in ['mrs']:
                    tok.lemma = 'mistress'
                elif tok.form.lower() in ['mån', 'mån.']:
                    tok.lemma = 'måndag'
                elif tok.form.lower() in ['nr', 'nr.']:
                    tok.lemma = 'nummer'
                elif tok.form.lower() in ['okt', 'okt.']:
                    tok.lemma = 'oktober'
                elif tok.form.lower() in ['pcb']:
                    tok.lemma = 'polyklorerade_bifenyler'
                elif tok.form.lower() in ['prof', 'prof.']:
                    tok.lemma = 'professor'
                elif tok.form.lower() in ['s', 's.', 'sid', 'sid.']:
                    tok.lemma = 'sida'
                elif tok.form.lower() in ['st']:
                    tok.lemma = 'styck'
                elif tok.form.lower() in ['t']:
                    tok.lemma = 'ton'
                elif tok.form.lower() in ['tel.', 'tel']:
                    tok.lemma = 'telefon'
                elif tok.form.lower() in ['tr', 'tr.']:
                    tok.lemma = 'trappor'
                elif tok.form.lower() in ['vol', 'vol.']:
                    tok.lemma = 'volym'
                elif tok.form.lower() in ['x']:
                    tok.lemma = 'gånger'

                change_id = 'abbr_noun'
            
            elif tok.upos == 'VERB':
                if tok.form.lower() in ['jfr']:
                    tok.lemma = 'jämför'

                change_id = 'abbr_verb'

            elif tok.upos == 'ADP':
                if tok.form.lower() in ['f']:
                    tok.lemma = 'före'

                change_id = 'abbr_adp'

            elif tok.upos == 'CCONJ':
                if tok.form.lower() in ['&']:
                    tok.lemma = 'and'

                change_id = 'abbr_cconj'

            elif tok.upos == 'PROPN':
                if tok.form.lower() in ['AKP:s']:
                    tok.lemma = 'adalet_ve_kalkınma_partisi'
                elif tok.form.lower() in ['ECB:s']:
                    tok.lemma = 'europeiska_centralbanken'
                elif tok.form.lower() in ['mps']:
                    tok.lemma = 'miljöpartiet'
                elif tok.form.lower() in ['mps']:
                    tok.lemma = 'miljöpartiet'
                elif tok.form.lower() in ['rhs']:
                    tok.lemma = 'refugee_health_screener'
                elif tok.form.lower() in ['RSPB:s']:
                    tok.lemma = 'the_royal_society_for_the_protection_of_birds'

                change_id = 'abbr_propn'
           
            if old_lemma != tok.lemma.lower():
                change_ids.append(change_id)
                changed_forms_by_id[change_id].add(tok.form)
                change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\ttext='{tok.root.compute_text()}'")
        

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_adj_abbr_lemma_changes.log', change_ids, changed_forms_by_id, change_log)

def reclassify_participles(doc, outfile, participle_class_doc):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []

    with open(participle_class_doc, 'r') as f:
        participle_classification = {}
        for line in f:
            if line.strip():
                lemma, part_class = line.split('\t')[:2]
                part_class = part_class.strip()
                lemma = lemma.split('=')[-1].strip("'")
                participle_classification[lemma.lower()] = part_class if not part_class == 'No' else None

    for tok in doc.nodes:
        change_id = None
        old_feats = tok.feats.__str__()
        was_verb = False
        
        

        if tok.upos == 'VERB' and tok.feats['VerbForm'] == 'Part' and (not 'aux:pass' in [child.deprel for child in tok.children if child.lemma == 'bli']):
            # if tagged as a verb and does not have a child with lemma 'bli'
            # set it as ADJ
            # set Case=Nom/Gen depending on if it ends with "s"
            # set Tense based on its previous Voice (Pass=Past, Act=Pres)
            # set Definite based on Mood=In
            # set Degree=Pos
            tok.upos = 'ADJ'
            tok.feats['Case'] = 'Nom' if not tok.form.endswith('s') else 'Gen'

            if tok.feats.get('Voice', None) == 'Act':
                tok.feats['Tense'] = 'Pres'
            
            elif tok.feats.get('Voice', None) == 'Pass':
                tok.feats['Tense'] = 'Past'

            tok.feats['Voice'] = None
            
            if tok.feats.get('Mood', None) == 'Ind':
                tok.feats['Definite'] = 'Ind'

            tok.feats['Mood'] = None

            tok.feats['Degree'] = 'Pos'

            was_verb = True
        

        if tok.lemma.lower() in participle_classification:
            # if the lemma is in the list of participle-like candidates, 
            # check if it is classified as a participle or not
            if participle_classification[tok.lemma.lower()]:
                # if it is a participle, set VerbForm=Part and Tense=Pres/Past if ADJ and also Voice=Pass if 
                # VERB and bli-passive construction
                if tok.upos == 'ADJ':
                    tok.feats['VerbForm'] = 'Part'
                    tok.feats['Tense'] = participle_classification[tok.lemma.lower()]

                    change_id = f"{'adj' if not was_verb else 'verb'}_{participle_classification[tok.lemma.lower()]}_participle"

                elif tok.upos == 'VERB' and 'aux:pass' in [child.deprel for child in tok.children if child.lemma == 'bli']:
                    tok.feats['VerbForm'] = 'Part'
                    tok.feats['Tense'] = participle_classification[tok.lemma.lower()]
                    tok.feats['Voice'] = 'Pass'

                    change_id = f"verb_bli_pass_participle"

            else:
                # if it is not considered a participle, remove VerbForm and Tense, but if VERB leave Voice=Pass
                if tok.upos == 'ADJ':
                    tok.feats['VerbForm'] = None
                    tok.feats['Tense'] = None
                    
                    change_id = f"{'adj' if not was_verb else 'verb'}_not_participle"

                elif tok.upos == 'VERB' and 'aux:pass' in [child.deprel for child in tok.children if child.lemma == 'bli']:
                    tok.feats['VerbForm'] = None
                    tok.feats['Tense'] = None
                    tok.feats['Voice'] = 'Pass'

                    change_id = f"verb_bli_pass_not_participle"
                
                    
        if change_id != None:
            if tok.feats.__str__() != old_feats:
                change_ids.append(change_id)
                changed_forms_by_id[change_id].add(tok.form)
                change_log.append(f"{change_id=}\tsent_id='{tok.address()}'\tupos='{tok.upos}'\tform='{tok.form}'\t{old_feats=}\tfeats='{tok.feats.__str__()}'\ttext='{tok.root.compute_text()}'")

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_reclassify_participle_changes.log', change_ids, changed_forms_by_id, change_log)

def change_den_det_de(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []
    for tok in doc.nodes:
        change_id = None
        old_lemma = tok.lemma.lower()
        old_feats = tok.feats.__str__()

        if tok.upos == 'PRON':

            # den är...
            if tok.form.lower() == 'den':
                tok.lemma = 'den'
                tok.feats = {'Definite': 'Def',
                              'Gender': 'Com',
                              'Number': 'Sing',
                              'PronType': 'Prs'}
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
            if tok.lemma.lower() != old_lemma or new_feats != old_feats:
                
                change_ids.append(change_id)
                changed_forms_by_id[change_id].add(tok.form)
                change_log.append(f"{change_id=}\tsent_id='{tok.root.address()}'\t{tok.form=}\t{old_lemma=}\t{tok.lemma=}\t{old_feats=}\t{new_feats=}\ttext='{tok.root.compute_text()}'")

    write_to_change_log(outfile.rsplit('.', maxsplit=1)[0]+'_den_det_de_changes.log', change_ids, changed_forms_by_id, change_log)

def change_adj_feats(doc, outfile):
    change_ids = []
    changed_forms_by_id = defaultdict(set)
    change_log = []
    unchanged = []
    flagged = []

    ordinals = ['första', 'förste', 'andra', 'andre', 'tredje', 'fjärde', 'femte', 
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

    roman_num = ['I', 'II', 'III', 'IV', 'V', 
                 'VI', 'VII', 'VIII', 'IX', 'X', 
                 'XI', 'XII', 'XIII', 'XIV', 'XV', 
                 'XVI', 'XVII', 'XIII', 'XIX', 'XX']

    for tok in doc.nodes:
        if tok.upos == 'ADJ':
            change_id = None
            old_feats = tok.feats.__str__()

            if tok.form.lower() in OVERSPEC:
                for key, value in OVERSPEC[tok.form.lower()].items():
                    tok.feats[key] = value

                    change_id = 'overspecified'

            elif tok.form.lower() in ENGLISH_ADJ and tok.feats['Foreign'] == 'Yes':
                change_id = 'eng'
            
            elif tok.form.lower() in FOREIGN or tok.feats['Foreign'] == 'Yes':
                change_id = 'foreign'

            elif tok.feats['Abbr'] == 'Yes':
                change_id = 'abbr'

            elif tok.form.lower().endswith('-'):
                change_id = 'ends_in_dash'

            # svart-types:
            elif tok.lemma.lower() in SVART_ADJ and tok.form.lower() == tok.lemma.lower():
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Number'] = 'Sing'

                tok.feats['Gender'] = None

                change_id = 'svart_sing'

            # bra-types
            elif tok.form.lower() in BRA_ADJ:
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Pos'

                tok.feats['Definite'] = None
                tok.feats['Gender'] = None
                tok.feats['Number'] = None

                change_id = 'bra_types'
            
            # visst / formellt / 
            elif (tok.lemma.lower()[-1] in ['f', 'g', 'l', 'm', 'n', 'p', 'r', 's', 'v', 'k', 'x', 'b']) and (tok.form.lower() == tok.lemma.lower() + 't'):
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum+t' 
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing'
            
            # pressad / definerad / integrerad
            elif tok.form.lower().endswith('ad') and tok.form.lower() == tok.lemma.lower():
                # We don't touch VerbForm and Tense because these are set during 
                # the reclassification of participles. If we change them here
                # we undo the reclassification
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'past_parciple_ad_sing' 
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Com|Number=Sing'
            
            # ordnat / utformat / outnyttjat
            elif tok.form.lower().endswith('at') and tok.form.lower()[:-1] + 'd' == tok.lemma.lower():
                # We don't touch VerbForm and Tense because these are set during 
                # the reclassification of participles. If we change them here
                # we undo the reclassification
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'past_parciple_at' 
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing|Tense=Past|VerbForm=Part'

            # bästa / största / värste
            elif (((tok.form.lower().endswith('sta') or tok.form.lower().endswith('aste')) and 
                  tok.feats['Degree'] == 'Sup') or
                  tok.form.lower() in ['bästa']):
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Sup'
                tok.feats['Definite'] = tok.feats.get('Definite', 'Def')
                tok.feats['Gender'] =  None
                
                tok.feats['Number'] = None
                
                change_id = 'sup'
                # nfeats = 'Case=Nom|Definite=Def|Degree=Sup'

            # bästa / största / värste
            elif (((tok.form.lower().endswith('ste') and not tok.form.lower().endswith('aste') ) 
                   and tok.feats['Degree'] == 'Sup') or
                   tok.form.lower() == ['bäste']):
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Sup'
                tok.feats['Definite'] = tok.feats.get('Definite', 'Def')
                tok.feats['Gender'] = 'Com'
                
                tok.feats['Number'] = None
                
                change_id = 'sup_masc'
                # nfeats = 'Case=Nom|Definite=Def|Degree=Sup'
            
            # bäst / störst / värst
            elif ((tok.form.lower().endswith('st') and tok.feats['Degree'] == 'Sup') or
                  tok.form.lower() in ['bäst']):
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Sup'
                tok.feats['Definite'] = 'Ind'
                
                tok.feats['Gender'] = None
                tok.feats['Number'] = None

                
                change_id = 'sup_ind'
                # nfeats = 'Case=Nom|Definite=Ind|Degree=Sup'
                
            # bättre / större / värre
            elif ((tok.form.lower().endswith('re') and tok.feats['Degree'] == 'Cmp') or
                  tok.form.lower() in ['bättre', 'mera', 'mer']):
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Cmp'

                tok.feats['Definite'] = None
                tok.feats['Gender'] = None
                tok.feats['Number'] = None
                
                change_id = 'comperative'
                # nfeats = 'Case=Nom|Degree=Cmp'

            # (den/det/dessa/sin) civil(a) / ny(a) / statistisk(a) / svart(a) / numrerade / väntade / älskade
            elif ((tok.feats['Degree'] != 'Sup' and tok.form.lower() == tok.lemma.lower() + 'a') or 
                  (tok.form.lower().endswith('a') and tok.form.lower() == tok.lemma.lower() + tok.lemma.lower()[-1] + 'a') or 
                  (tok.form.lower().endswith('ade') and tok.form.lower()[:-1] == tok.lemma.lower()) or
                  (tok.form.lower().endswith('na') and tok.form.lower()[:-2] + 'en' == tok.lemma.lower()) or
                  (tok.form.lower().endswith('ra') and tok.form.lower()[:-2] + 'er' == tok.lemma.lower()) or
                  (tok.form.lower().endswith('la') and tok.form.lower()[:-2] + 'el' == tok.lemma.lower()) or
                  ((tok.form.lower().endswith('la') and 
                    tok.form.lower()[:-2] + tok.form.lower()[-3] + 'al' == tok.lemma.lower())) or
                  ((tok.form.lower().endswith('na') and 
                    tok.form.lower()[:-2] + tok.form.lower()[-3] + 'en' == tok.lemma.lower())) or
                  tok.form.lower() in ['små', 'audio-visuella'] or
                  (tok.form.lower() == 'andra' and tok.lemma.lower() == 'annan')):
                
                if tok.form.endswith('ade'):
                    adj_type = 'past_participle_ade'
                elif tok.lemma.lower() in SVART_ADJ:
                    adj_type = 'svart+a'
                elif tok.form.lower() == tok.lemma.lower() + tok.lemma.lower()[-1] + 'a':
                    adj_type = 'double_consonant'
                elif tok.form.lower().endswith('ra') and tok.form.lower()[:-2] + 'er' == tok.lemma.lower():
                    adj_type = 'utrum-er+ra'
                elif (tok.form.lower().endswith('la') and 
                      tok.form.lower()[:-2] + tok.form.lower()[-3] + 'al' == tok.lemma.lower()):
                    adj_type = '-mla'
                elif (tok.form.lower().endswith('na') and 
                      tok.form.lower()[:-2] + tok.form.lower()[-3] + 'en' == tok.lemma.lower()):
                    adj_type = '-mna'
                elif tok.form.lower().endswith('na') and tok.form.lower()[:-2] + 'en' == tok.lemma.lower():
                    adj_type = 'past_participle_na'
                elif tok.form.lower() == 'andra' and tok.lemma.lower() == 'annan':
                    adj_type = 'andra'
                elif tok.form.lower() == 'små':
                    adj_type = 'små'
                else:
                    adj_type = 'utrum+a'

                # Kolla Number/Definite mot substantiv och artikel om de finns, flagga om de inte stämmer överens.
                # Om Definite=Def|Number=Sing, ta bort Number
                # Om Number=Plur, kolla substantiv och artikel, om det inte finns, flagga och ändra manuellt.
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Pos'

                tok.feats['Gender'] = None

                # i.      (den) stora stol(en)             Definite=Def, Number=None, Gender=None
                # ii.     (de) stora stolar(na)            Definite=Def, Number=None, Gender=None
                # iii.    stora stolar                     Definite=Ind, Number=Plur, Gender=None
                if tok.deprel == 'amod' or (tok.deprel == 'conj' and tok.parent.deprel == 'amod'):
                    # if deprel=conj, we need to look to the parent (noun) of the head of the conjugation
                    parent = tok.parent if tok.deprel == 'amod' else tok.parent.parent
                    siblings = tok.siblings if tok.deprel == 'amod' else tok.parent.siblings

                    # If we do not have the necessary information in the parent 
                    # we flagg the token and move on.
                    if not parent.feats['Definite']:
                        flagged.append(tok)
                        continue
                    else:
                        
                        # if the parent (noun) has Definite=Def and there is a definite article, 
                        # then we set the adjective to Definite=Def and remove number
                        # i.      (den) stora stol(en)             Definite=Def, Number=None, Gender=None
                        # ii.     (de) stora stolar(na)            Definite=Def, Number=None, Gender=None 
                        if parent.feats['Definite'] == 'Def' and \
                            any(art in [sibling.lemma.lower() for sibling in siblings if sibling.deprel == 'det'] for art in ('den', 'de')):
                            tok.feats['Definite'] = 'Def'
                            tok.feats['Number'] = None

                            change_id = f"{adj_type}_def_den_de"

                        elif parent.feats['Definite'] == 'Def':
                            tok.feats['Definite'] = 'Def'
                            tok.feats['Number'] = None

                            change_id = f"{adj_type}_def_no_art"

                        # if the parent (noun) has Definite=Ind and there is either the determiner 
                        # denna, detta or dessa in the siblings, set Definite=Def and remove Number
                        elif parent.feats['Definite'] == 'Ind' and \
                            any(art in [sibling.lemma.lower() for sibling in siblings if sibling.deprel == 'det'] for art in ('denna')):
                            tok.feats['Definite'] = 'Def'
                            tok.feats['Number'] = None

                            change_id = f"{adj_type}_ind_dessa"
                        
                        # else if parent (noun) has Definite=Ind there is no definite article,
                        # and one of the siblings of the parent (noun) has the deprel nmod:poss
                        # we set the adjective to Definite=Def and Number=None
                        elif parent.feats['Definite'] == 'Ind' and \
                                'nmod:poss' in [sibling.deprel for sibling in 
                                                siblings] and \
                                not any(art in [sibling.lemma.lower() for sibling in siblings if sibling.deprel == 'det'] for art in ('den', 'de')):
                            tok.feats['Definite'] = 'Def'
                            tok.feats['Number'] = None

                            change_id = f"{adj_type}_ind_nmod:poss"
                            
                        
                        # else if parent (noun) has Definite=Ind|Number=Plur and there is no definite article,
                        # we set the adjective to Definite=Ind and since we know that indefinite svart+a
                        # must be plural we set the adjective to Number=Plur
                        # iii.    stora stolar                     Definite=Ind, Number=Plur, Gender=None
                        elif parent.feats['Definite'] == 'Ind' and \
                                parent.feats['Number'] == 'Plur' and \
                                not any(art in [sibling.lemma.lower() for sibling in siblings if sibling.deprel == 'det'] for art in ('den', 'de')):
                            tok.feats['Definite'] = 'Ind'
                            tok.feats['Number'] = 'Plur'

                            change_id = change_id = f"{adj_type}_ind_plur"

                        # if we have something like: 
                        # Den stora stol som...
                        # then we flagg it for manual check
                        else:
                            flagged.append(tok)
                            continue
                    
                # if the adjective is not amod
                else:
                    # de utvalda, de vita, de gröna
                    if any(art in [child.lemma.lower() for child in tok.children if child.deprel == 'det'] for art in ('den', 'de')):
                        tok.feats['Definite'] = 'Def'
                        tok.feats['Number'] = None

                        change_id = f"{adj_type}_not_amod_def_art"

                    # if not amod and lacks definite article
                    # then it has to be indefinite such as in:
                    # stolarna är stora
                    # Levnadskostnaderna hölls konstanta (xcomp)
                    # som är intressanta (acl:relcl)
                    # då är färgerna irrelevanta (root)
                    else:
                        tok.feats['Definite'] = 'Ind'
                        tok.feats['Number'] = 'Plur'

                        change_id = f"{adj_type}_not_amod_no_def_art"

            # första / andra / 700:e / III
            elif (((tok.xpos is not None and ('RO' in tok.xpos or tok.xpos == 'ORD')) 
                   and tok.lemma.lower() != 'annan') or 
                  tok.feats['NumType'] == 'Ord' or
                  any(tok.form.lower().endswith(ord) for ord in ordinals) or 
                  re.search(r'^[0-9]+:[ae]$', tok.form) or
                  tok.form in roman_num):
                
                tok.feats['Case'] = 'Nom' if not tok.form.lower().endswith('s') else 'Gen'
                tok.feats['Number'] = 'Sing'
                tok.feats['NumType'] = 'Ord'

                tok.feats['Gender'] = None if not (tok.form.lower().endswith('förste') or 
                                                   tok.form.lower().endswith('andre')) else 'Com'
                tok.feats['Number'] = None
                
                change_id = 'ordinals'
                # nfeats = 'Case=Nom|Number=Sing|NumType=Ord'
    
            # sjungande / dansande / gående
            elif (tok.form.lower().endswith('ande') or tok.form.lower().endswith('ende')) and tok.form.lower() not in ['ende', 'ande']:
                # We don't touch VerbForm and Tense because these are set during 
                # the reclassification of participles. If we change them here
                # we undo the reclassification
                tok.feats['Case'] = 'Nom'
                tok.feats['Degree'] = 'Pos'

                tok.feats['Definite'] = None
                tok.feats['Gender'] = None
                tok.feats['Number'] = None
                
                change_id = 'pres_nom_participle'
                # nfeats = 'Case=Nom|Degree=Pos|Tense=Pres|VerbForm=Part'

            # absurt / inställt / känt
            elif tok.form.lower().endswith('t') and tok.form.lower()[:-1] + 'd' == tok.lemma.lower():
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum-d+t' 
            
            # sett
            elif tok.form.lower().endswith('tt') and tok.form.lower()[:-2] + 'dd' == tok.lemma.lower() :
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum-dd+tt' 

            # absurt / inställt / känt
            elif tok.form.lower().endswith('tt') and tok.form.lower()[:-2] + 'd' == tok.lemma.lower() :
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum-d+tt' 

            # fritt
            elif tok.form.lower().endswith('tt') and tok.form.lower()[:-2] == tok.lemma.lower() :
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum+tt' 

            # sött
            elif tok.form.lower().endswith('tt') and tok.form.lower()[:-1] == tok.lemma.lower() :
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum+t+t' 

            # angeläget
            elif tok.form.lower().endswith('t') and tok.form.lower()[:-1] + 'n' == tok.lemma.lower():
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Neut'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum-n+t' 
            
            # nye / brittiske / ensamme
            elif (tok.form.lower().endswith('e') and 
                  not tok.form.lower().endswith('ade') and 
                  not tok.form.lower().endswith('ande') and 
                  not tok.form.lower().endswith('ende') and
                  not tok.form.lower().endswith('ste') and
                  tok.form.lower() != tok.lemma.lower() and
                  tok.feats['NumType'] != 'Ord' and
                  tok.feats['Foreign'] != 'Yes' and
                  tok.feats['Degree'] not in ('Sup', 'Cmp')):
                
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Def'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Com'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'masc_pos'

            # nyas / nyes / tredjes / studerandes
            elif (tok.form.lower().endswith('s') and 
                  tok.form.lower() != tok.lemma.lower()):
                
                tok.feats['Case'] = 'Gen'
                
                # den/det/de störstas
                if tok.form.lower().endswith('stas') and tok.feats['Degree'] == 'Sup':
                    tok.feats['Definite'] = 'Def'

                    tok.feats['Gender'] = None
                    tok.feats['Number'] = None

                    change_id = 'gen_sup'

                # den störstes
                elif tok.form.lower().endswith('stes') and tok.feats['Degree'] == 'Sup':
                    tok.feats['Definite'] = 'Def'
                    tok.feats['Gender'] = 'Com'

                    tok.feats['Number'] = None

                    change_id = 'gen_sup_masc'
                
                # (den/det/de) störres
                elif tok.form.lower().endswith('res') and tok.feats['Degree'] == 'Cmp':
                    tok.feats['Definite'] = None
                    tok.feats['Gender'] = None
                    tok.feats['Number'] = None

                    change_id = 'gen_cmp'
                
                # sjungandes / dansandes / gåendes
                elif (tok.form.lower().endswith('andes') or tok.form.lower().endswith('endes')) and tok.form.lower() not in ['endes', 'andes']:
                    
                    tok.feats['Case'] = 'Gen'
                    tok.feats['Degree'] = 'Pos'

                    tok.feats['Definite'] = None
                    tok.feats['Gender'] = None
                    tok.feats['Number'] = None

                    change_id = 'gen_pres_participle'

                # förstas / förstes 
                elif (((tok.xpos is not None and ('RO' in tok.xpos or tok.xpos == 'ORD')) 
                       and tok.lemma.lower() != 'annan') or 
                      tok.feats['NumType'] == 'Ord' or
                      any(tok.form.lower().endswith(end) for end in gen_ordinals) or 
                      re.search(r'^[0-9]+:[ae]s$', tok.form)):
                    tok.feats['Number'] = 'Sing'
                    tok.feats['NumType'] = 'Ord'

                    tok.feats['Definite'] = None if not tok.form.lower().endswith('förstes') else 'Def'
                    tok.feats['Gender'] = None if not tok.form.lower().endswith('förstes') else 'Com'

                    change_id = 'gen_ord'
            
                # storas / stores / svartas / svartes 

                elif tok.form.lower().endswith('es') and not tok.form.lower().endswith('ades'):
                    tok.feats['Definite'] = 'Def'
                    tok.feats['Degree'] = 'Pos'
                    tok.feats['Gender'] = 'Com'
                    tok.feats['Number'] = 'Sing'
                    
                    change_id = 'gen_masc'

                else:
                    tok.feats['Definite'] = 'Def'
                    tok.feats['Degree'] = 'Pos'

                    tok.feats['Gender'] = None
                    tok.feats['Number'] = None 

                    change_id = 'gen'

            elif tok.form.lower() == tok.lemma.lower():
                if tok.feats['Number'] == 'Plur':
                    flagged.append(tok)
                    continue
                tok.feats['Case'] = 'Nom'
                tok.feats['Definite'] = 'Ind'
                tok.feats['Degree'] = 'Pos'
                tok.feats['Gender'] = 'Com'
                tok.feats['Number'] = 'Sing'
                
                change_id = 'utrum' 

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
        lemma_not_form = sorted([tok for tok in unchanged if tok.form.lower() != tok.lemma.lower()], key=lambda tok: tok.lemma.lower())
        lemma_not_form = [f"sent_id='{tok.address()}'\ntext='{tok.root.compute_text()}'\n{get_conllu(tok)}\n" for tok in lemma_not_form]
        unchanged = sorted(unchanged, key=lambda tok: tok.lemma.lower())
        unchanged = [f"sent_id='{tok.address()}'\ntext='{tok.root.compute_text()}'\n{get_conllu(tok)}\n" for tok in unchanged]
        for line in lemma_not_form:
            f.write(line+'\n')
        f.write('\n\n\n\n\n\n\n')
        for line in unchanged:
            f.write(line+'\n')

    with open(outfile.rsplit('.', maxsplit=1)[0]+'_flagged_adj.log', 'w') as f:
        flagged = sorted(flagged, key=lambda tok: tok.lemma.lower())
        flagged = [f"id={tok.address()}\ntext='{tok.root.compute_text()}'\n{get_conllu(tok)}\n" for tok in flagged]
        for line in flagged:
            f.write(line+'\n')

def manual_changes(doc, outfile, manual_changes_document):
    change_log = list()
    nodes = list(doc.nodes)
    id2node = {node.address(): i for i, node in enumerate(nodes)}
    
    with open(manual_changes_document, 'r') as f:
        for line in f:
            if line.startswith('id='):
                node_id = line.strip().split('=')[-1]
            elif line.startswith('text='):
                continue
            elif line.strip():
                line = line.strip().split('\t')
                assert len(line) == 10, line
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

                    new_parent = nodes[id2node[node_id.split('#')[0]+f'#{head}']] if head != '0' else node.root

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
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--infile', required=True)
    parser.add_argument('--outfile', required=True)
    parser.add_argument('--prefixes')
    parser.add_argument('--postfixes')
    parser.add_argument('--partlist')

    args = parser.parse_args()

    infile = args.infile
    outfile = args.outfile
    prefixes_doc = args.prefixes
    postfixes_doc = args.postfixes
    partlist_doc = args.partlist

    print('Reading', infile)
    doc = udapi.Document(infile)

    if prefixes_doc:
        manual_changes(doc, outfile, prefixes_doc)

    change_adj_lemma(doc, outfile)
    change_adj_ordinal_lemma(doc, outfile)
    change_participle_lemma(doc, outfile)
    change_adj_exception_lemma(doc, outfile)
    change_abbr_lemma(doc, outfile)

    if partlist_doc:
        reclassify_participles(doc, outfile, partlist_doc)

    change_den_det_de(doc, outfile)
    change_adj_feats(doc, outfile)

    if postfixes_doc:
        manual_changes(doc, outfile, postfixes_doc)

    doc.store_conllu(filename=outfile)

