#!/usr/bin/perl
use warnings;
use Getopt::Long;

# Perl script to read in manual fixes from file and apply them to a conll file.
# Fix file must have the following format:
#
# 29952
# 2   Paulo   Paulo   PROPN   PM|NOM  Case=Nom    1   mwe _   _   
# 2   Paulo   Paulo   PROPN   PM|NOM  Case=Nom    1   name    _   _
#
# where 29952 indicates the line number in the conll file ignoring comment lines (indexed from 1), 
# followed by the line as it currently stands, followed by the corrected line. A blank line 
# separates corrections. 
#
# Example call: ./fix_errors.plx --fix_file manual_fixes.txt --conll_file sv-ud.conll

my $fix_file = ""; 
my $conll_file = ""; 
GetOptions ('fix_file=s' => \$fix_file, 'conll_file=s' => \$conll_file);

die "ERROR: conll file must have ending .conll or .conllu" unless($conll_file =~ /\.conllu?$/);

#################################################################

# read and store information from fix file in arrays 
my @line_nos;
my @orig_lines;
my @new_lines;

my $fix_index = 0;
die "Could not open $fix_file" unless open(FIXES, $fix_file);
while(my $fix_line = <FIXES>){
    chomp($fix_line);
    $fix_line =~ s/^ +//; # remove any space accidentally added at beginning of line
    $fix_line =~ s/ +$//; # remove any space accidentally added at end of line
    if($fix_index%4 == 0){
        push(@line_nos,$fix_line);
    }
    elsif($fix_index%4 == 1){
        push(@orig_lines,$fix_line);
    }
    elsif($fix_index%4 == 2){
        push(@new_lines,$fix_line);
    }
    $fix_index++;
}

##############################################################

# read conll file
die "ERROR: couldn't open $conll_file for reading" unless open(CONLL_FILE, $conll_file);

my @conll_lines = <CONLL_FILE>;
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

# open output file and print result
(my $outfile = $conll_file) =~ s/(.*)\.(conllu?)/$1.fix.$2/; # set output file name
die "ERROR: couldn't open $outfile for writing" unless open(OUTFILE, ">$outfile");
print STDERR "Printing output to $outfile\n";
foreach (@conll_lines){
    print OUTFILE "$_\n";
}
