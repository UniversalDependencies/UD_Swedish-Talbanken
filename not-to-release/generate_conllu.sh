mkdir ./output
mkdir ./output/temp


python3 mamba2ud.py P.original.txt ./output/temp/sv1.conllu
perl fix_errors.plx --fix-file manual_fixes.txt --in-file ./output/temp/sv1.conllu --out-file ./output/temp/sv2.conllu
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


python3 split.py ./output/temp/sv6.conllu ./output/sv_talbanken-ud

# comment rm -r output/temp if you want to keep the intermediate generation steps
# rm -r ./output/temp
