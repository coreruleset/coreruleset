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
use FindBin qw( $RealBin );

# load Regexp::Assemble from the submodule, not from any other location
use lib "$RealBin/lib/lib";
use Regexp::Assemble;

# cook_hex: disable replacing hex escapes with decodec bytes
# force_escape_tokens: we embed the resulting regex within double quotes,
#                      so they all need to be escaped
my $ra = Regexp::Assemble->new(cook_hex => 0, force_escape_tokens => q("));
my @flags = ();
my @prefixes = ();
my @suffixes = ();

while (<>)
{
  # strip new lines
  CORE::chomp($_);

  # this is a flag comment (##!+), save it for later
  # we currently only support the `i` flag
  push (@flags, $1) if $_ =~ /^##!\+\s*([i]+)/;
  # this is a prefix comment (##!^), save it for later
  push (@prefixes, $1) if $_ =~ /^##!\^\s*(.*)/;
  # this is a suffix comment (##!$), save it for later
  push (@suffixes, $1) if $_ =~ /^##!\$\s*(.*)/;
  # skip comments
  next if $_ =~ /^##!/;
  # skip empty lines
  next if $_ =~ /^\s*$/;

  # Handle possessive qualifiers
  # https://rt.cpan.org/Public/Bug/Display.html?id=50228#txn-672717
  # the code below does nearly the same thing as add(), which is enough for our pruposes

  # The following lines parse an expression like `(a++|b)++|b` into an array of `["(a++|b)+", "+", "|", "b"]`

  # We explicitly don't use `_fastlex` or `split` here (as is done in `_add`). `lexstr` uses `_lex`, which is
  # more expensive but produces more reliable output. On the downside, some characters will be escaped (or
  # will retain their escape) even though they don't need to be.
  #
  # Example issue solved by `_lex`: `\(?` produces `\(\?` with `_fastlex`
  # Example escape introduced by `_lex`: `/` produces `\/`
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
if (@flags > 0) {
  print "(?" . join('', @flags) . ")";
}
# print the prefixes
print join('', @prefixes);
# call as_string() to make stats_length() work
my $pattern = $ra->as_string();
# don't print the assembled string if nothing was added, the module will produce an all-matching pattern
print $pattern if $ra->stats_length() > 0;
# print the suffixes
print join('', @suffixes) . "\n";
