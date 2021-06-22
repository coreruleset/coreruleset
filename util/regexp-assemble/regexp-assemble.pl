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
while (<>)
{
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
print $ra->as_string() . "\n";
