#!/usr/bin/env perl
#
# Create one regexp from a set of regexps.
# Regexps can be submitted via standard input, one per line.
#
# Requires Regexp::Assemble Perl module.
# To install: cpan install Regexp::Assemble
#
# See: https://coreruleset.org/20190826/optimizing-regular-expressions/
#

use strict;
use Regexp::Assemble;

my $ra = Regexp::Assemble->new;
my $flags = '';
my $prefix = '';
my $suffix = '';

while (<>)
{
  # strip new lines
  CORE::chomp($_);

  # this is a flag comment (#!), save it for later
  # we currently only support the `i` flag
  $flags = $1 if $_ =~ /^\s*#!\s*([i]+)/;
  # this is a prefix comment (#^), save it for later
  $prefix = $1 if $_ =~ /^\s*#\^\s*(.*)/;
  # this is a prefix comment (#$), save it for later
  $suffix = $1 if $_ =~ /^\s*#\$\s*(.*)/;
  # skip comments
  next if $_ =~ /^\s*#/;
  # skip empty lines
  next if $_ =~ /^\s*$/;

  # Handle possessive qualifiers
  # https://rt.cpan.org/Public/Bug/Display.html?id=50228#txn-672717
  # the code below does nearly the same thing as add(), which is enough for our pruposes

  # parse an expression like `(a++|b)++|b` into an array of `["(a++|b)+", "+", "|", "b"]`
  my $arr = $ra->lexstr($_);
  for (my $n = 0; $n < $#$arr - 1; ++$n)
  {
    # find consecutive pairs where the first element ends with `+` and the last element is only `+`
    if ($arr->[$n] =~ /\+$/ and $arr->[$n + 1] eq '+') {
      # delete the second of the pair, concatenating it with the first element
      $arr->[$n] .= splice(@$arr, $n + 1, 1);
    }
  }
  # at this point the array looks like this: `["(a++|b)++", "|", "b"]`
  # we now have what we would want to pass to add(), so add it
  $ra->insert(@$arr);
}
# print flags
if ($flags ne '') {
  print '(?' . $flags . ')';
}
# print the assembly, surrounded by prefix and suffix
print $prefix . $ra->as_string() . $suffix . "\n";