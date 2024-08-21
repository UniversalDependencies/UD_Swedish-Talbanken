import argparse, json



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--infile', required=True)
    parser.add_argument('--fixfile', required=True)
    parser.add_argument('--outfile', required=True)

    args = parser.parse_args()

    change_dict = json.load(open(args.fixfile, 'r'))

    with open(args.infile, 'r') as f:
        infile = f.readlines()
    
    for change in change_dict:
        assert infile[change['line_number']] == change['old_line']
        infile[change['line_number']] = change['new_line']

    with open(args.outfile, 'w') as f:
        for line in infile:
            f.write(line)

        
    