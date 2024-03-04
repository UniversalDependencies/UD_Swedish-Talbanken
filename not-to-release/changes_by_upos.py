import re, sys, os
from collections import Counter
from changes_by_upos_config import config 

def setNewAnnotation (udfile, outfile):
    ''' writes a changed annotation from <udfile> to <outfile> using a <UPOS> and dictionaries with new values '''
    
    # for easier indexing of the info variable
    i = {
        'ID': 0, 
        'FORM': 1, 
        'LEMMA': 2, 
        'UPOS': 3, 
        'XPOS': 4, 
        'FEATS': 5, 
        'HEAD': 6, 
        'DEPREL': 7, 
        'DEPS': 8, 
        'MISC': 9}

    # sets to reference if a token is of interest
    token_set = set()
    upos_set = set()
    
    # populate the token and upos set from the config file
    for upos, info in config.items():
        upos_set.add(upos)
        for info_key, change_dict in info.items():
            for token in change_dict.keys():
                token_set.add(token)

    # for tracking changes to the tree bank
    changes = Counter()
    change_log = list()
    sentence_count = 0

    print(f'Reading from: ./{infile}', file=sys.stderr)
    print(f'Writing to: ./{outfile}', file=sys.stderr)
        
    with open (outfile, "w") as w:
        with open (udfile, "r") as u:
            for line in u:

                # store sentence ID for log file
                if re.match(r'# sent_id', line):
                    sentence_count += 1
                    sentid = line.split('=')[-1].strip()

                # if the line contains a token
                if re.match(r'\d', line):
                    info = line.strip().split('\t')

                    # get form and upos from line
                    form = info[i['FORM']] 
                    upos = info[i['UPOS']]

                    # check if this token is of interest agains the token and upos sets
                    if (form in token_set) and (upos in upos_set):
                        # loop through the config dictionary (eg. FEATS and LEMMA) 
                        # to change all relevant entries for current token
                        for info_key, change_dict in config[upos].items():
                            # if the form is a key in the current dictionary of changes
                            # log the change and change the entry to the new value.
                            if form in change_dict.keys():
                                change_log.append(f'{sentid=}\t{form=}\t{upos=}\toriginal_entry=\'{info[i[info_key]]}\'\tnew_entry=\'{change_dict[form]}\'')

                                # we change the entry of the relevant field to the new value.
                                info[i[info_key]] = change_dict[form]


                                # we create a key for the counter object that we will be able
                                # to print when all changes have been done.
                                counter_key = f'UPOS={upos}|FORM={form}|{info_key}={change_dict[form]}'
                                if counter_key not in changes.keys():
                                    changes[counter_key] = 1
                                else:
                                    changes[counter_key] += 1

                        # we write the modified token line to the new document
                        newline = '\t'.join(info) + '\n'
                        w.write(newline)
                    # if the token is not of interest we write the line unchanged
                    else:
                        w.write(line)                    
                # if it is not a token line we also write the line unchanged
                else:
                    w.write(line)
    
    # we modify the output file name to create a change-log file
    change_log_file = '.'.join(outfile.split('.')[:-1])+'-changes.log'
    ## places the log_file one directory above the output file. 
    # change_log_file = change_log_file.split('/')
    # change_log_file = '/'.join(change_log_file[:-2]) + '/' + change_log_file[-1]
    
    with open(change_log_file, 'w') as log:
        for line in change_log:
            log.write(line+'\n')
    print(f'Wrote {sentence_count}', file=sys.stderr)
    print(f'Changed {len(change_log)} entries', file=sys.stderr)
    return changes

def sys_arg_error():
    command = 'python3 feats_by_upos.py <ud-input-file> <ud-output-file>'
    print(f"ERROR: Incorrect number of system arguments.\n\n{command}", file=sys.stderr)

if __name__ == '__main__':
    '''
        python3 feats_by_upos.py <ud-input-file> <ud-output-file>
        <ud-input-file>: .conllu file
        <ud-output-file>: file name for output
    '''
    if len(sys.argv) != 3:
        sys_arg_error()
        exit()
    else:
        infile, outfile = sys.argv[1:]
        changes = setNewAnnotation(infile, outfile)
        for change, count in changes.items():
            print(change, 'CHANGES='+str(count), file=sys.stderr)
        