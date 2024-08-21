mkdir ./output
mkdir ./output/temp


python3 mamba2ud.py P.original.txt ./output/temp/sv1.conllu
python3 manual_fixes.py --infile ./output/temp/sv1.conllu --outfile ./output/temp/sv2.conllu --fixfile manual_fixes.json
# perl fix_errors.plx --fix-file manual_fixes.txt --in-file ./output/temp/sv1.conllu --out-file ./output/temp/sv2.conllu
python3 comments.py ./output/temp/sv2.conllu ./output/temp/sv3.conllu 
python3 harmonize-sv.py ./output/temp/sv3.conllu ./output/temp/sv4.conllu
python3 insert-enhanced.py sv_talbanken-ud.enhanced.txt ./output/temp/sv4.conllu ./output/temp/sv5.conllu

python3 sv_talbanken_updates_2024.py \
    --infile ./output/temp/sv5.conllu \
    --outfile ./output/temp/sv6.conllu \
    --prefixes ./prefixes.tsv \
    --postfixes ./postfixes.tsv \
    --partlist ./participle_classification_list.tsv \
    --manual_def_num ./manual_def_num.tsv

python3 ucxn_update.py \
    --infile ./output/temp/sv6.conllu \
    --ucxnfile ./ucxn_ud_swedish-talbanken.conllu \
    --outfile ./output/temp/sv7.conllu

python3 tokens-with-spaces.py ./output/temp/sv7.conllu ./output/tokens-with-spaces.txt
python3 make_edeprel.py ./output/temp/sv7.conllu ./output/edeprel.sv

python3 split.py ./output/temp/sv7.conllu ./output/sv_talbanken-ud

# comment rm -r output/temp if you want to keep the intermediate generation steps
# rm -r ./output/temp
