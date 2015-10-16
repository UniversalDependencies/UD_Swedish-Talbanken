#!/usr/bin/perl
use warnings;
use Getopt::Long;

# Perl script to read in manual fixes from file and apply them to a conll file.
# Fix file must have the following format:
#
# 4112
# 34  Västra  Västra  ADJ JJ|POS|UTR/NEU|SIN|DEF|NOM  Case=Nom|Definite=Def|Degree=Pos|Number=Sing    29  conj    _   _   
# 35  Frölunda    Frölunda    PROPN   PM|NOM  Case=Nom    34  name    _   _   
# ---
# 34  Västra  Västra  ADJ JJ|POS|UTR/NEU|SIN|DEF|NOM  Case=Nom|Definite=Def|Degree=Pos|Number=Sing    35  amod    _   _   
# 35  Frölunda    Frölunda    PROPN   PM|NOM  Case=Nom    29  conj    _   _ 
#
# where 4112 indicates the line number of the first line in the conll file ignoring comment lines (indexed from 1), 
# followed consecutive lines as they currently stand, followed by the corrected lines. Blank lines separate corrections. 
#
# Example call: ./fix_errors.plx --fix_file manual_fixes.txt --infile sv-ud.conllu --outfile sv-ud.fix.conllu

# set default names for the input/output files
my $fix_file = "manual_fixes.txt";
my $infile = "sv-ud.conllu"; 
my $outfile = "";

# read in user names for input/output files
GetOptions ('fix-file=s' => \$fix_file, 'in-file=s' => \$infile, 'out-file=s' => \$outfile);
die "ERROR: conll file must have ending .conll or .conllu" unless($infile =~ /\.conllu?$/);

($outfile = $infile) =~ s/(.*)\.(conllu?)/$1.fix.$2/ if($outfile eq ""); # set output file name if not specified by user
die "ERROR: couldn't open $outfile for writing" unless open(OUTFILE, ">$outfile");

#################################################################

# read and store information from fix file in arrays 
my @line_nos;
my @orig_lines;
my @new_lines;

my $fix_index = 0;
die "Could not open $fix_file" unless open(FIXES, $fix_file);
my @fix_lines = <FIXES>;
chomp(@fix_lines);

for(my $index = 0; $index<scalar(@fix_lines); $index++){
    while($fix_lines[$index] !~ /^[0-9]+$/){
        $index++;
        last if($index == scalar(@fix_lines));
    }
    last if($index == scalar(@fix_lines));
    my $line_no = $fix_lines[$index]-1;
    $index++;
    while($fix_lines[$index] !~ /^---/){
        $line_no++;
        push(@line_nos,$line_no);
        push(@orig_lines,$fix_lines[$index]);
        $index++;
    }
    $index++;
    while($fix_lines[$index] !~ /^$/){
        push(@new_lines,$fix_lines[$index]);
        $index++;
    }
}

die if(scalar(@orig_lines) != scalar(@new_lines));
die if(scalar(@orig_lines) != scalar(@line_nos));

# this was an older method based on a different format for the manual_changes.txt file
#while(my $fix_line = <FIXES>){
#    chomp($fix_line);
#    $fix_line =~ s/^ +//; # remove any space accidentally added at beginning of line
#    $fix_line =~ s/ +$//; # remove any space accidentally added at end of line
#    if($fix_index%4 == 0){
#        push(@line_nos,$fix_line);
#    }
#    elsif($fix_index%4 == 1){
#        push(@orig_lines,$fix_line);
#    }
#    elsif($fix_index%4 == 2){
#        push(@new_lines,$fix_line);
#    }
#    $fix_index++;
#}

##############################################################

# read conll file
die "ERROR: couldn't open $infile for reading" unless open(INFILE, $infile);

my @conll_lines = <INFILE>;
chomp(@conll_lines);

# create mapping between line numbers without comments and original index numbers
my @index_mapping; 
push(@index_mapping, -1); # there should be no line number 0 so arbitrarily set 0th element to -1
for(my $orig_index=0; $orig_index <= $#conll_lines; $orig_index++){
    unless($conll_lines[$orig_index] =~ /^#/){
        push(@index_mapping, $orig_index);
    }
}

################################################################

# Apply changes

for(my $i=0;$i<=$#line_nos;$i++){
    if($conll_lines[$index_mapping[$line_nos[$i]]] eq $orig_lines[$i]){ 
        $conll_lines[$index_mapping[$line_nos[$i]]] = $new_lines[$i];
    }
    else{
        print STDERR "Warning: \nexpected line $index_mapping[$line_nos[$i]]\n$orig_lines[$i]\ngot line\n$conll_lines[$index_mapping[$line_nos[$i]]]\n\n";
   }
}

################################################################

# print result
print STDERR "Printing output to $outfile\n";
foreach (@conll_lines){
    print OUTFILE "$_\n";
}
