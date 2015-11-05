#!/usr/bin/perl
use warnings;
use Getopt::Long;
use List::MoreUtils qw(uniq);

# finds mwe or name relations in the Swedish UD treebank and all dependents of the head word.
# assumes that dependents in a name relation follow the head, i.e. the head always has to come
# first or this script will stop working properly. finds both the 'real' line number, i.e.
# the line number in the current version of sv-ud.conll, and the 'dummy' line number, which is 
# the line number not counting comment lines. this script was created in order to find 
# name and mwe relations that are not being used correctly and subsequently fix them via the
# manual_changes.txt file.
#
# perl find_mwes.plx --relation name --conll_file sv-ud.conll > names.txt


my $relation = "mwe";
my $conll_file = "sv-ud.conllu";

GetOptions ('relation=s' => \$relation, 'conll_file=s' => \$conll_file);

open(CONLL_FILE, $conll_file);
my @conll_lines = <CONLL_FILE>; 

my %line_no; # hash to hold real and dummy line numbers

my @current_sentence; # array to hold the conll lines for the current sentence
my @print_lines; # array to hold the indices of the lines in the current sentence that need to be printed

$line_no{dummy} = 0; # line number without comments
for($line_no{real}=1;$line_no{real}<scalar(@conll_lines);$line_no{real}++){
    my $conll_line = $conll_lines[$line_no{real}-1];
    unless($conll_line =~ /^#/){ # check line is not a comment
        $line_no{dummy}++;
        if($conll_line =~ /^$/){ # check if line is blank and therefore a sentence boundary
            @current_sentence = ();
            @print_lines = ();
        }
        else{ 
            my @conll_elements = split("\t",$conll_line); # split line into columns 
            # if we are at the first line of a new sentence store the line numbers and fill 
            # @current_sentence
            if($conll_elements[0] == 1){
                $line_no{sentence_start_real} = $line_no{real};
                $line_no{sentence_start_dummy} = $line_no{dummy};
                my $temp_index = $line_no{real}-1;
                my $temp_line = $conll_line;
                # put the words of the sentence in @current_sentence array
                while($temp_line !~ /^$/){ 
                    push(@current_sentence,$temp_line) unless($temp_line =~ /^#/);
                    $temp_index++;
                    $temp_line = $conll_lines[$temp_index];
                }
            }
            if($conll_elements[7] eq $relation){ # check if dependency relation is equal to the desired relation
                my $word_index = $conll_elements[0]; # find index of the current token in its sentence
                my $head_index1 = $conll_elements[6]; # find index of head word in the current sentence
#            print STDERR "warning: head not previous line $i\n" if($head_index1 != ($word_index-1));
                print STDERR "warning: head comes after dependent on line $line_no{real}\n" if($head_index1 > $word_index);
                push(@print_lines,($head_index1,$word_index)); # add the current token and its head to the print lines
                my $conll_next_line = $conll_lines[$line_no{real}]; # we need to check subsequent tokens as well
                if($conll_next_line =~ /^#/){
                    print STDERR "warning: comment in middle of the relation on line $line_no{real}\n";
                }
                else{
                    unless($conll_next_line =~ /^$/){
                        $line_no{real}++; # move to the next line
                        $line_no{dummy}++;
                        my @conll_next_elements = split("\t",$conll_next_line);
                        if($conll_next_elements[7] eq $relation){ # check for the relation
                            push(@print_lines,$conll_next_elements[0]); # add to print lines
                            my $head_index2 = $conll_elements[6]; # check head is the same
                            print STDERR "warning: heads don't match on line $line_no{dummy}:$line_no{real}\n" if($head_index2 != $head_index1);
                            my $next_rel = $relation;
                            while($next_rel eq $relation){
                                $conll_next_line = $conll_lines[$line_no{real}];             
                                unless($conll_next_line =~ /^#/){ # check line is not a comment
                                    if($conll_next_line =~ /^$/){
                                        last;
                                    }
                                    else{
                                        $line_no{real}++;
                                        $line_no{dummy}++;
                                        @conll_next_elements = split("\t",$conll_next_line);
                                        if($conll_next_elements[7] eq $relation){
                                            push(@print_lines,$conll_next_elements[0]);
                                            my $head_index2 = $conll_elements[6];
                                            print STDERR "warning: heads don't match on line $line_no{real}\n" if($head_index2 != $head_index1);
                                        }
                                        else{
                                            $next_rel = "X";
                                        }
                                    }
                                }
                            }
                        }   
                    }
                }
                # go through the sentence and look for any dependents of the previous head
                foreach my $line (@current_sentence){
                    my @columns = split("\t",$line);
                    if($columns[6] == $head_index1){
                        push(@print_lines,$columns[0]);
                    }
                }
                # sort and find all unique print numbers and print
                my @sorted_print_lines = sort { $a <=> $b } @print_lines;
                my @unique_lines = uniq @sorted_print_lines;
                my $real_index = $line_no{sentence_start_real} + $unique_lines[0] - 1;
                my $dummy_index = $line_no{sentence_start_dummy} + $unique_lines[0] - 1;
                print "$dummy_index:$real_index\n";
                for(my $token_index=0; $token_index<scalar(@unique_lines);$token_index++){
                    my $ind = $unique_lines[$token_index]-1;
                    my $size = scalar(@current_sentence);
#                    foreach (@current_sentence) { print STDERR "$_ "; }
#                    print STDERR "$ind $size\n";
                    print "$current_sentence[$unique_lines[$token_index]-1]";
                }
                print "\n";
                @print_lines = ();
            }
        }
    }
}
