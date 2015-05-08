#!/usr/bin/perl
use strict;

if($#ARGV < 0){
  print STDERR "One argument required (Dictionary lookup output file)\n";
  exit;
}

open my $dictFP, '>', $ARGV[0] or die("One argument required");
my %words;

while(<STDIN>){
  my @words = split /\s+/;
  my $buf;
  for my $word (@words){
    $word = lc($word);
    if(!exists($words{$word})){
      my $hashSize = keys %words;
      $words{$word} = $hashSize+1;
#      print STDERR "Size of words is: ".$hashSize."\n";
    }
    $buf .= "$words{$word} ";
  }
  print substr($buf, 0, length($buf)-1)."\n";
}

for my $key (sort keys %words){
  print $dictFP "$key $words{$key}\n";
}

