# OWASP ModSecurity Core Rule Set (CRS) CHANGES

## Report Bugs/Issues to GitHub Issues Tracker or the mailinglist
* https://github.com/coreruleset/coreruleset/issues
  or the CRS Google Group at
* https://groups.google.com/a/owasp.org/g/modsecurity-core-rule-set-project

## Nightly builds
New changelog entries are written to `.changes-pending.md`. They will be moved to the main changelog before a release.

## Version 4.0.0 - 2022-06-??

Important changes:
 * feat: introduce plugin architecture for extending CRS and minimizing attack surface. (Christian Folini, Max Leske, Jozef Sudolský, Andrew Howe) [#2038, #2448, #2404]
 * feat: early blocking option (Christian Folini) [#1955]
 * feat: support for HTTP/3 (Jozef Sudolský) [#3218]
 * feat: application exclusions and less-used functionality have been migrated to plugins. (Christian Folini, Max Leske, Jozef Sudolský, Andrew Howe)
 * feat: granular control over reporting levels in 9801xx rules (Simon Studer, Andrew Howe, Christian Folini) [#2482, #2488]
 * feat: all formerly PCRE-only regular expressions are now compatible with Re2/Hyperscan WAF engines (Max Leske, Felipe Zipitría, Allan Boll, Franziska Bühler) [#1868, #2356, #2425, #2426, #2371, #2372]
 * feat: new rule 920620 PL1 to explicitly detect multiple Content-Type abuse (CVE-2023-38199) (Andrea Menin) [#3237]
 * feat: nightly packages published regularly (Felipe Zipitría) [#2207]
 * feat: add enable_default_collections flag to not initialize collections by default (Matteo Pace) [#3141]
 * feat: extend definition of restricted headers to include `Content-Encoding` and `Accept-Charset` by default (920450 PL1, 920451 PL2) (Walter Hop) [#2780, #2782]
 * feat: switch to using wordnet instead of spell for finding English words in spell.sh (Max Leske) [#3242]
 * fix: refactor and rename anomaly scoring variables and paranoia level definition (Simon Studer) [#2417]
 * update: drop HTTP/0.9 support to resolve FP (Federico G. Schwindt) [#1966]

Tool changes:
 * feat: extend spell.sh script with an opt-in manual list of common and partial words. (Matteo Pace) [#3273]
 * feat: rework spell.sh utility to help with detection of false positives English words (Andrea Menin) [#3029]
 * feat: improve usability of spell.sh utility (Max Leske) [#3238]
 * feat: extend rules-check.py script to better enforce rule format in project guidelines (Ervin Hegedus) [#3113]
 * feat: extend rules-check.py script to ensure that `auditLogParts` is only used in last chained rule (Ervin Hegedus) [#2609]
 * feat: extend rules-check.py script to ensure that rules use `@rx` operator explicitly (Ervin Hegedus) [#2541]
 * feat: extend rules-check.py script to strip comments when parsing crs-setup.conf.example (Ervin Hegedus) [#3161]

Changes after RC1:
 * feat: add consistent rule references to initialization rule comments (Andrew Howe) [#2813]
 * feat: add placeholder files for new plugin architecture (Walter Hop) [#2515]
 * feat: check initialization and use for all TX variables (Ervin Hegedus) [#3043]
 * feat: disassemble complex regexes for 932xxx rules that were subsequently replaced by other rules (Max Leske) [#2566]
 * feat: extend rules to detect keyword `time` as prefix of *nix and Windows RCE rules (rules later replaced) (Franziska Bühler) [#2819]
 * feat: extend rules to detect path based XSS via new target REQUEST_FILENAME in 941xxx rules (Walter Hop) [#2894]
 * feat: extend rule to detect restricted `method override` headers (Mark Zeman / KramNamez) [#3056]
 * feat: improve rule file 951xxx via the use of `skipAfter` instead of variable `TX:sql_error_match` (Jozef Sudolský) [#2754]
 * feat: move regexp-assemble data files to root directory (Felipe Zipitría) [#3002]
 * fix: reformat several initialization rules to follow project guidelines (Ervin Hegedus) [#3157]
 * fix: remove auditLogParts actions from all rules where present (Andrea Menin, Ervin Hegedüs) [#3034, #3081]
 * fix: remove uncommon Content Types from default in `crs-setup.conf.example` (Andrea Menin) [#2768]
 * fix: update diverse rules to follow new naming convention with paranoia level TX variables (Christoph Hansen) [#2937]
 * fix: remove initialization rules for redundant IP reputation variables (901150, 901152) (Andrew Howe) [#2833]
 * fix: initialize all variables used properly (901169) (Ervin Hegedus) [#2802]
 * fix: remove rule to detect security scanner http headers (913110 PL1) (Christian Folini) [#3241]
 * feat: remove ineffective anti-scanner list scanners-urls.data and associated rule (913120 PL1) (Christian Folini) [#3235]
 * feat: rework restricted headers mechanism into two separate lists (920450 PL1, 920451 PL2) (Andrew Howe) [#3152]
 * feat: new rule detect multiple occurences of charset keyword in content type header (920530 PL1) (Jan Gora / terjanq) [#2571]
 * feat: new rule to detect unicode character bypass check for non JSON requests (920540 PL1) (Franziska Bühler, 0SPwn) [#2512]
 * feat: new rule to detect # char in URIs (920610 PL1) (Karel Knibbe) [#2919]
 * fix: use correct anomaly scoring variables and panaoia level tags across several rules (921170 PL1, 921220 PL4, 932220 PL2, 932331 PL3, 933211 PL3, 934101 PL1, 942362 PL2, 951100) (Christoph Hansen) [#2931]
 * feat: new rules to detect HTTP parameter pollution bypasses (921210 PL3, 921220 PL4) (Christian Folini) [#2747]
 * fix: use correct anomaly scoring variables and paranoia level tags across several rules (921220 PL4, 932101 PL2, 932331 PL3, 933211 PL3, 942362 PL2) (Ervin Hegedus) [#2832]
 * feat: new rule to detect range header that is now forbidden on PL3 and up (921230 PL3) (Christian Folini) [#2760]
 * feat: new rule to detect mod_proxy attack (CVE-2021-40438) (921240 PL1) (Franziska Bühler) [#2818]
 * feat: new rules to detecting ModSecurity body processor confusion using the `Content-Type` HTTP header (921421 PL1, 921422 PL2) (Simon Studer, Ervin Hegedus) [#2763]
 * fix: handle false positives when detecting ModSecurity body processor confusion (921422 PL2) (Ervin Hegedus) [#2784]
 * fix: remove possessive quantifiers (922110 PL1) (Felipe Zipitría) [#2989]
 * feat: extended rule to detect Tomcat specific path traversal attack (930110 PL1) (Christoph Hansen) [#2915]
 * feat: extend rule to detect access attempts to /tmp/ (930120 PL1, 930121 PL2) (Max Leske) [#3131]
 * feat: extend rule to detect ECDSA type SSH identity files via list of sensitive *nix files (930120 PL1) (Pinaki Mondal / 0xInfection) [#2586]
 * feat: extend rule to detect additional sensitive files on *nix systems (930121 PL2, 930130 PL1) (Gwendal Le Coguic / gwen001) [#2560]
 * feat: new rules to detect lfi and sqli in user-agent and referer request headers (930121 PL2, 942152 PL2, 942321 PL2) (Franziska Bühler, Max Leske, Shivam Bathla) [#3102]
 * fix: extend rule to detect more LFI (930121 PL2) (Felipe Zipitría) [#2791]
 * feat: extend data file to include additional restricted file names (restricted-files.data, 930130 PL1) (Jitendra Patro) [#3219]
 * feat: extend data file to include PrestaShop configuration file (restricted-files.data, 930130 PL1) (Jean-François Viguier) [#3192]
 * feat: extend rule to detect `npm-shrinkwrap.json` to restricted-files (930130 PL1) (Esa Jokinen / oh2fih) [#2627]
 * feat: extend rules to detect additional protocols in RFI attacks (931130 PL2, 934120 PL2) (Karel Knibbe) [#2572]
 * feat: extend rule to detect `url:file:` schema in Java RFI attacks (931130 PL2) (Andrew Howe) [#2727]
 * feat: new rule to detect  path traversal attacks using URL encoded URL schemes in Java applications (931131 PL2) (Christoph Hansen) [#2902]
 * feat: extend rule to detect additional *nix shell commands (931160 PL1) (Gwendal Le Coguic / gwen001) [#2563]
 * feat: extend rule to detect additional entries to *nix command lists (932100 PL1, 932105 PL1) (Finn Westendorf / wfinn) [#2552]
 * feat: extend rule to detect additional *nix commands (932100 PL1) (Felipe Zipitría) [#2676]
 * feat: extend rule to detect additional *nix commands (932105 PL1) (Felipe Zipitría) [#2677]
 * feat: extend rule to detect `mshta` in Windows shell commands (932110 PL1) (Somdev Sangwan / s0md3v) [#2588]
 * feat: extend rule to detect additional powershell cmdlet on Windows (932120 PL1) (Pinaki Mondal / 0xInfection) [#2589]
 * feat: extend rule to detect Powershell RCEs better via new automation (932120 PL1) (Felipe Zipitría) [#2669]
 * feat: new rule to detect Windows cmdlet aliases (932125 PL1) (Pinaki Mondal / 0xInfection) [#2589]
 * fix: extend rule to detect character class *nix expressions (932130 PL1) (Somdev Sangwan / s0md3v, Walter Hop) [#2594]
 * feat: extend rule to detect `busybox`, `$SHELL`, and `${SHELL}` in *nix RCE attacks (932150 PL1) (Walter Hop) [#2728]
 * feat: extend rule to detect c99 and printf utilities (932150 PL1) (Karel Knibbe) [#2569]
 * feat: extend rule to detect `ksh` in *unix RCE attacks (932150 PL1) (Andrew Howe) [#2721]
 * feat: extend rule to detect  RCE attacks using compression utilities (932150 PL1) (Andrew Howe) [#2712]
 * feat: extend rule to detect RCEs using base64 evasions (932150 PL1) (Somdev Sangwan / s0md3v, Andrew Howe) [#2590]
 * feat: extend rule to detect RCEs using evasions quotes with `python...` commands (932150 PL1) (Somdev Sangwan / s0md3v, Andrew Howe) [#2590]
 * feat: new rule to detect generalised *nix RCE (932150 PL2) (Karel Knibbe) [#2583]
 * feat: extend rule to detect RCE better via automation (932160 PL1) (Felipe Zipitría) [#2662]
 * fix: remove unnecessary prefixes from paths in `unix-shell.data` (932160 PL1) (Felipe Zipitría) [#2662]
 * feat: extend rule to detect `expre` in unix-shell list (932161 PL2) (Felipe Zipitría) [#2667]
 * feat: new rules to detect *nix commands in user-agent and referer request headers (932161 PL2, 932237 PL3) (Franziska Bühler, Max Leske, Shivam Bathla) [#3132]
 * feat: use new automation to generate `restricted-uploads.data` from `restricted-files.data` (932180 PL1) (Max Leske) [#3282]
 * feat: extend rule to detect RCE in user-agent request header (932200 PL2) (Franziska Bühler, Shivam Bathla) [#3108]
 * fix: new rules to handle referer header and fix false positive (932205 PL2, 932206 PL2) (Max Leske) [#3300]
 * feat: extend rule to detect quote evasion (932210 PL2) (Max Leske) [#3120]
 * feat: extend rule to detect `sh` (932210 PL2) (Franziska Bühler) [#2816]
 * feat: extend rule to detect SQLi via automation of keyword list updates (932210 PL2) (Felipe Zipitría) [#2801]
 * fix: add word boundaries for sh in RCE rules (932230 PL1, 932250 PL1) (Max Leske) [#3186]
 * fix: handle false positive against `sh` in *nix command injection attacks (932230 PL1, 932250 PL1, 932236 PL2) (Max Leske) [#3186]
 * feat: move *nix command injection rule 932101, 932106 into the same range as the other *nix command injection rules (932231 PL2, 932232 PL3) (Felipe Zipitría, Max leske) [#3092]
 * feat: replace *-with-params.ra files with suffix replacements (932235 PL1, 932236 PL2, 932239 PL2, 932237 PL3) (Max Leske) [#3331]
 * fix: add whitespace after keywords `mail` and `task` to solve false positives (932236 PL2) (Franziska Bühler) [#3274]
 * fix: align unix-shell-upto3* files (932236 PL2) (Max Leske) [#3128]
 * fix: solved false positives with creation of word boundaries for commonly used words used in *nix RCE rules (932236 PL2)  (Max Leske) [#3187]
 * fix: use correct anomaly scoring variable (932236 PL2) (Ervin Hegedus) [#3112]
 * feat: new rule to detect *nix commands in user-agent and referer request headers (932239 PL2) (Franziska Bühler, Shivam Bathla) [#3104, #3318]
 * fix: remove ARGS_NAME from target variables in (932240 PL2) (Andrea Menin) [#2960]
 * fix: use correct anomaly scoring variables and panaoia level tags across for rule (932240 PL2) (Ervin Hegedus) [#2963]
 * feat: replace *nix command injection rules 932150 PL1, 932151 PL1 with new rules for commands of less than 4 characters and commands of more than 4 characters in length respetively (932250 PL1, 932260 PL1) (Felipe Zipitría, Max leske) [#3092]
 * fix: false positives by requiring specific tokens to follow commands (932250 PL1) (Max Leske) [#3186]
 * feat: new rules to detect detecting *nix shell history invocations (932330 PL1, 932331 PL3) (Karel Knibbe) [#2577]
 * feat: new Windows commands rules based on lolbas-project replacing 932110, 932115 (932370 PL1, 932380 PL1) (Felipe Zipitría, Franziska Bühler, Max Leske) [#3059, 3170]
 * feat: extend rule to detect additional file extensions via list of executable PHP files (933110) (Jan Gora / terjanq) [#2585]
 * feat: extend data file to add missing PHP config directives (php-config-directives.data, 933120 PL1) (Max Leske) [#3028]
 * feat: extend rule to detect additional sensitive PHP directives (933120 PL1) (Gwendal Le Coguic / gwen001) [#2561]
 * feat: extend rule to detect PHP config directives via automation of keyword list updates (933120 PL1) (Felipe Zipitría) [#2696]
 * feat: extend rule to detect sensitive PHP variables better (933130 PL1) (Felipe Zipitría) [#2668]
 * feat: extend data file to include additional php function names (php-function-names-933151.data, 933151 PL2) (Jitendra Patro) [#3212]
 * feat: automate generation of PHP function dictionaries, revisited detection (933160 PL1, 933161 PL3, 933150 PL1, 933151 PL2) (Juan-Pablo Tosso, Christian Folini, Matteo Pace) [#3273]
 * feat: extend rule to detect `document.domain` XSS (933160 PL1, 941180 PL1) (Franziska Bühler, 0SPwn) [#2567]
 * feat: extend rule to detect evasions in PHP contexts with `"` (933160 PL1) (Somdev Sangwan / s0md3v) [#2596]
 * feat: rearrange keywords (933160 PL1, 941390 PL1) (Karel Knibbe) [#2905]
 * fix: solve ReDoS issue in rule (933161 PL3) (Andrea Menin) [#2302]
 * feat: extend rule to detect `bzip2` wrapper in PHP injection attacks (933200 PL1) (Andrew Howe) [#2723]
 * feat: extend rule to detect `ssh2.*` wrappers in PHP injection attacks (933200 PL1) (Andrew Howe) [#2731]
 * feat: new rule to detct PHP injection attacks without terminating semi-colon (933211 PL3) (Karel Knibbe) [#2581]
 * feat: extended rule to detect Node.js injection attacks using `require` and `child_process` (934100 PL1, 932101 PL2) (Andrea Menin) [#2893]
 * feat: extend rule to detect Node.js RCE better (934100 PL1) (rektor0) [#2578]
 * feat: improve transformation pipeline to detect Base64-encoded evasions (934100 PL1) (Andrew Howe) [#3203]
 * feat: new rule to detect Node.js RCE detection (934101 PL2) (rektor0) [#2578]
 * fix: improve js rule transformation pipelines (934101 PL1, 934130 PL1, 934169 PL1, 934131 PL2) (Andrew Howe) [#3312]
 * feat: extend data file to include additional indicators (ssrf.data, 934110 PL1) (Jitendra Patro) [#3213]
 * feat: extend rule to detect SSRF better (934110 PL1) (Felipe Zipitría) [#2660]
 * feat: extend rule to detect additional schema and IP evasion techniques in SSRF (934120 PL2) (Felipe Zipitría, Max Leske) [#2599]
 * feat: extend rule to detect octal address of AWS metadata endpoints (934120 PL2) (Karel Knibbe) [#2555]
 * feat: extend rule to detect SSRF better by inspecting targets beyond just ARGS (934120 PL2) (Karel Knibbe) [#2555]
 * feat: new rules to detect detection of Perl and Ruby RCE signatures in a generic way (934140 PL2, 934150 PL1) (Karel Knibbe) [#2587]
 * feat: new rule to detect Node DoS attack via expressions resolving to true (934160 PL1) (Karel Knibbe) [#2917]
 * fix: remove unnecessary character escape (941120 PL2) (Andrew Howe) [#2805]
 * feat: disassemble complex regex fully (941160 PL1) (Felipe Zipitría) [#2701]
 * feat: disassemble complex regex (941210 PL1) (Felipe Zipitría) [#3262]
 * feat: extend rule to detect XSS evasions using carriage return (\r) and new line (\n) characters (941210 PL1) (oct0pus7) [#2576]
 * feat: disassemble complex regex (941220 PL1) (Felipe Zipitría) [#3263]
 * feat: new rule to detect JavaScript methods (941390 PL1) (Franziska Bühler) [#2702]
 * feat: extend rule and moved rule from PL3 to PL2 (942101 PL2) (Matteo Pace) [#2922]
 * feat: extended rule to detect common SQL injection probing in path segments (942110 PL2) (Andrea Menin) [#2914]
 * feat: add target REQUEST_FILENAME to rule to detect path-based SQLi attacks (942120 PL2) (Andrew Howe) [#3057]
 * feat: extend rule to detect use of `collate` in SQLite injection attacks (942120 PL2) (Jan Gora / terjanq) [#2584]
 * fix: extend rule to detect more SQLi (942120 PL2) (Karel Knibbe) [#2556]
 * feat: extend rule to detect `glob` in list of SQLi tautologies (942130 PL2) (Franziska Bühler) [#2729]
 * fix: remove unneeded TX variables (942130 PL2, 942131 PL2, 942521 PL3) (Andrea Menin) [#3293]
 * feat: extend rule to detect more SQL function names (942150 PL2) (Karel Knibbe) [#2895]
 * feat: extend rules to detect more SQL error messages and functions (942151 PL1, 942152 PL1, 951220 PL1, 951230 PL1, 951240 PL1) (Jitendra Patros) [#3336]
 * feat: extend rule to detect additional SQL function signatures (942151 PL1) (Karel Knibbe) [#2570]
 * feat: extend rule to detect `endswith`, `startswith`, `unistr`, `pg_client_encoding` and various json sql functions (942151 PL1) (Franziska Bühler) [#2874]
 * feat: extend rule to detect various json functions (942151 PL1) (Franziska Bühler) [#3041]
 * feat: extend rule to detect `sql_compileoption_get` in SQLite injection attacks (942152 PL1) (Andrew Howe) [#2718]
 * feat: new regex-assembly file for rule (942170 PL1) (Andrea Menin) [#2939]
 * feat: extend rule to detect SQL injection authentication bypasses (942180 PL2) (rekter0) [#2575]
 * feat: disassemble complex regex (942200 PL2) (Franziska Bühler, Max Leske) [#2932]
 * feat: extend rule to detect SQLi in user-agent and referer request headers (942200 PL2, 942370 PL2) (Franziska Bühler, Shivam Bathla) [#3106]
 * feat: improve regex-assembly file for rule (942210 PL2) (Andrew Howe) [#2945]
 * feat: disassemble complex regex (942240 PL1) (Franziska Bühler, Max Leske) [#2938]
 * feat: new regex-assembly file for rule (942280 PL1) (Andrea Menin) [#2933]
 * feat: extend rule to detect additional MongoDB operators via NoSQL commands list (942290 PL1) (rekter0) [#2579]
 * feat: new regex-assembly file for rule (942290 PL1) (Andrea Menin) [#2942]
 * feat: improve regex-assembly format (942300 PL2) (Felipe Zipitría) [#3296]
 * feat: extend rule to detect `::int` and `::bool` sql data conversions (942320 PL1) (Franziska Bühler) [#2872]
 * feat: extend rule to detect `lo_get` and `::text` via PostgreSQL functions list (942320 PL2) (Franziska Bühler, Walter Hop, Shivam Bathla) [#2925]
 * feat: extend rule to detect `lo_import` and `div` via PostgreSQL functions list (942320 PL2) (Franziska Bühler, Shivam Bathla) [#2916]
 * feat: extend rule to detect more PostgreSQL data types (942320 PL2) (Franziska Bühler, Shivam Bathla) [#3019]
 * fix: add word boundaries to keywords to solve false positives (942330 PL2) (Franziska Bühler) [#3207]
 * feat: extend rule to detect SQL injection better (942340 PL2) (Karel Knibbe) [#2557]
 * fix: extend rule to detect more SQLi (942340 PL2) (Jan Gora / terjanq) [#2559]
 * feat: new regex-assembly file for rule (942370 PL2) (Christoph Hansen, Max Leske) [#2954]
 * feat: disassemble complex chained regex (942440 PL2) (Felipe Zipitría) [#3295]
 * fix: reformat rules to follow project guidelines (942440 PL2, 949959, 949159, 959059, 959159) (Ervin Hegedus) [#3206]
 * fix: solve errors in regex pattern (942440 PL2) (Andrea Menin) [#3290]
 * feat: extend rules to detect `current_user` and `overlay` (942470 PL1, 942480 PL2) (Franziska Bühler) [#2875]
 * feat: extended rule to detect detect SQL injection attacks using headers (942480 PL2) (Paul Beckett) [#2911]
 * feat: extend rule to detect newlines in overlay (942480 PL2) (Franziska Bühler, Shivam Bathla) [#3040]
 * feat: new rules to detect SQL authentication bypasses (942520 PL2, 942521 PL2, 942522 PL2) (Jan Gora / terjanq) [#2603]
 * feat: extend rule to detect SQLi in user-agent and referer request headers (942521 PL2) (Franziska Bühler, Shivam Bathla) [#3107]
 * feat: new rule to detect `';` in sqli (942530 PL3) (Franziska Bühler) [#2808]
 * fix: update scoring variable (942540 PL2) (Walter Hop) [#2970]
 * feat: new rule to detect MySQL scientific notation attacks (942560 PL1) (Jitendra Patro) [#3316]
 * feat: extend rule to detect JAVA exploits better via java-classes.data file (944130 PL1) (Dennis Brown) [#3048]
 * fix: update administrative rule ids for consistent operation (950011, 950012, 950018) (Ervin Hegedüs) [#3339]
 * feat: extend data file to include additional sql error messages (sql-errors.data, 951100 PL1) (Jitendra Patro) [#3214]
 * fix: handle false positive in SQL error leakage detection (951240 PL1) (Jozef Sudolský) [#3169]
 * feat: extend rule to detect PHP errors better via new automation (953100 PL1) (Felipe Zipitría) [#2663]
 * feat: new rules to detect PHP error leakages with high false positive rates at paranoia level 2 instead of 1 (953100 PL1, 953101 PL2) (Andrea Menin) [#3119]
 * fix: ignore case of `PHP` tag in response text (953210 PL1) (Felipe Zipitría) [#2664]
 * feat: extend rule to detect IIS errors via automation of pattern updates (954120 PL1) (Felipe Zipitría) [#2810]
 * feat: extend data file to include additional web shells (web-shells-php.data, 955100 PL1) (Jitendra Patro) [#3215]
 * feat: extend data file to include additional web shells (web-shells-php.data, 955100 PL1) (Jozef Sudolský) [#2687]

Changes before RC1:
 * Detect Log4j / Log4Shell (Christian Folini, Max Leske, Andrew Howe) [#2349]
 * Detect Spring4Shell (Christian Folini, Andrea Menin) [#2464]
 * Detect JavaScript prototype pollution (Walter Hop) [#2411]
 * Detect use of common webshells by inspecting response (Jozef Sudolský, Andrea Menin) [#1962, #2039, #2116]
 * Add phpMyAdmin exclusion rules (now a plugin) (Jozef Sudolský) [#1951]
 * Add phpBB exclusion rules (now a plugin) (Jozef Sudolský) [#1893]
 * Deny uploading .jsp and .jspx files (Walter Hop) [#2456]
 * Detect path traversal in file upload (k4n5ha0, Franziska Bühler, Felipe Zipitría) [#2451]
 * Block access to AWS cli files (Jozef Sudolský) [#2439]
 * Detect /proc and /sys access attempts (Andrew Howe) [#2154]
 * Detect common IP-based SSRF targets (Felipe Zipitría) [#2259]
 * Detect email protocol attacks (Felipe Zipitría) [#2322]
 * Detect more error based SQL injections (Jozef Sudolský) [#2429]
 * Detect SQLi with 'drop' keyword (Jozef Sudolský) [#2218]
 * Detect RCE attempts with uninitialized shell vars (Andrea Menin) [#2151]
 * Detect more unix RCE commands (Felipe Zipitría) [#2129]
 * Detect SQLi with 'if exists' (NiceYouKnow) [#2121]
 * Detect sqlite system command injection (flo405, Andrea Menin, Christian Folini) [#2032]
 * Include IPv6 in Host Header check (itsTheFae, Ervin Hegedus, Jozef Sudolský) [#1929]
 * Block access to WEB-INF directory (Jozef Sudolský) [#2092]
 * Block access to various sensitive files (Jozef Sudolský) [#1960]
 * Improve SQLi detection with spaces (Manuel Spartan, Max Leske) [#2436, #2290]
 * Improve SQLi detection with 'not between' (NiceYouKnow, Max Leske, Franziska Bühler) [#2115]
 * Fix blind SQLi detection in rule 942160 (Franziska Bühler, Christian Folini) [#1956]
 * Lower FP by moving '-->' keyword to PL2 (Paul Beckett) [#2060]
 * Run libinjection XSS detector on request filename in PL2 (Andrew Howe) [#2208]
 * Validate Sec-Fetch-User header (somechris) [#2020]
 * Detect Krzana bot (Deepshikha Sinha) [#2432]
 * Detect CensysInspect and seoscanners.net crawlers (Andrew Howe) [#2155]
 * Detect burpcollaborator scanner (Amir Hosein Aliakbarian) [#2152]
 * Detect QQGameHall malware (Walter Hop) [#2144]
 * Detect 'httpx' scanner (Will Woodson) [#2045]
 * Detect 'ecairn' crawler (Jozef Sudolský) [#2024]
 * Detect LeakIX scanner (Jozef Sudolský) [#1961]
 * Unified regexp utils to automate error-prone actions and automatically update rules from regexp sources (Max Leske) [#2149, #2223, #2423, #2495, #2489, #2473]
 * Add Google OAuth2 exclusion plugin (Jozef Sudolský) [#2388]
 * Validate Accept-Encoding headers (Franziska Bühler) [#2357]
 * Deny access to sslvpn_websession (Jozef Sudolský) [#2338]
 * Detect 'Invoke-WebRequest' command (Paul Beckett) [#2271]
 * Update send-payload-pls.sh (Manuel Spartan) [#2288]
 * Exclusion profiles and DOS rules have been moved from CRS to plugins (Andrew Howe) [#2469]
 * IP reputation rules have been moved from CRS to plugins (Simon Studer) [#2482]
 * Tests: add utility script to find rules without tests (Ervin Hegedus) [#2279]
 * Add crs-rules-check tool that runs sanity checks against rules (Ervin Hegedus) [#2236]
 * Tests: add utility to find longest data lengths (Ervin Hegedus) [#2277]
 * Improve rule-ctl script to modify rules (Max Leske) [#2193]
 * Add utility to change version numbers (Ervin Hegedus) [#2085]
 * feat: new rule 934170 PL1 for PHP supporting `data:` scheme without using `//` before the content-type (Felipe Zipitría) [#3018]
 * fix: add local_file scheme from python2 in 931130 and 934120 (Felipe Zipitría) [#2809]
 * fix: update sql reserved words in rule 942120 (Felipe Zipitría) [#2798]
 * feat: new rule 932175 PL1 detecting `alias` builtin (Felipe Zipitría) [#2796]
 * feat: new rules 922100-922120 PL1 detecting attacks on multipart headers (Felipe Zipitría) [#2769]
 * feat: improve and extend cmdline processor to find more evasions (Felipe Zipitría) [#2907]
 * feat: new rule to detect authentication bypass via SQL injection that abuses semi-colons to end the SQL query in 942540 PL1 (Karel Knibbe) [#2904]
 * fix: update various rules to consolidate use of backslashes to \x5c representation for better compatibility with known WAF engines (Andrew Howe, Max Leske) [#2335, #2345, #2375, #2376, #2399, #2400, #2402, #2410, #2420, #2441, #2442, #2454, #2426]
 * fix: Adapt rule 942440 to work in all ModSecurity versions (Andrew Howe) [#2201]
 * Fix bypass in rule 931130 (Andrea Menin) [#2479]
 * Fix bypass in rule 933210 (Andrea Menin) [#2214]
 * Fix bypass in rule 942190 (Andrea Menin) [#1910]
 * Fix triple dot false negative in rules 930100, 930110 (Franziska Bühler) [#2309, #2310]
 * Fix false negative in rule 942230 (Max Leske) [#2348]
 * Fix FP in CalDAV Content-Type (Vandan Rohatgi) [#2505]
 * Lower FP in MySQL data leakage rule (Jozef Sudolský) [#2490]
 * Lower FP in SQL function names by splitting between PL1/PL2 (Jozef Sudolský) [#2480]
 * Fix FP in 'having' SQLi (Felipe Zipitría) [#2248]
 * Fix FP in JWT tokens (Andrea Menin) [#2460]
 * Fix FP on 'time' and 'ping' keywords (Walter Hop) [#2457]
 * Fix FP in 'application/*+json' Content-Type (Mirko Dziadzka, Walter Hop) [#2455]
 * Fix FP in Sec-CH-UA header (Franziska Bühler) [#2361]
 * Fix FP in PostgreSQL error messages (Jozef Sudolský, Franziska Bühler) [#1870, #2313]
 * Fix FP in Sybase error message (Jozef Sudolský) [#2307]
 * Fix FP in base64 content (Jozef Sudolský) [#2226]
 * Fix FP in XMLNLS (Walter Hop) [#2192]
 * Fix FP in rule 941310 with Russian characters (Max Leske) [#2107]
 * Fix FP in rule 942300 by adding word boundary checks (Franziska Bühler) [#2099]
 * Fix FP in SQLi by adding word boundary checks (Jozef Sudolský) [#2078]
 * Fix FP in SQLi with keyword 'union' (Franziska Bühler) [#2058]
 * Fix FP in rule 942230 with 'case' (Franziska Bühler) [#2035]
 * Fix FP for YAM package manager (Jozef Sudolský) [#2022]
 * Fix FP for '..' without slashes (Tetrik, Walter Hop) [#2016]
 * Fix FP in rule 932115 on 'sort' (Franziska Bühler) [#2012]
 * Fix FP in rule 933210 when cookie contains slash (Ervin Hegedus) [#1996]
 * Fix FP in rule 932100 (Franziska Bühler) [#1954]
 * Fix FP in Google OAuth2 (Jozef Sudolský, Christian Folini) [#1958]
 * Nextcloud: fix FPs (kam821, Jozef Sudolský, ntimo, Felipe Zipitría, pyllyukko) [#1840, #1843, #1847, #1946]
 * Fix FP on .axd in restricted extensions, these are public (Jozef Sudolský) [#1925]
 * Fix FP on 'version' string in Content-Type header (Jozef Sudolský) [#1901]
 * Fix FP in rule 941120 by adding character limit (Christian Folini) [#1872]
 * Fix FP in Content-Type with '#' character (Jozef Sudolský) [#1856]
 * phpMyAdmin: Fix FPs (Jozef Sudolský) [#2172, #2249, #2321, #2351]
 * WordPress: fix FPs (Jozef Sudolský) [#1899, #1971, #2320]
 * WordPress: fix FPs in Site Health page (Robert de Boer, Fregf, Walter Hop) [#1895, #1920]
 * WordPress: fix FPs and improve performance (Walter Hop) [#1997, #2311]
 * XenForo: fix FPs (Walter Hop, ThanhPT) [#1844, #1865, #1894, #1998, #2421]
 * phpBB: Fix FPs (Jozef Sudolský) [#2057, #2180, #2299, #2343]
 * Fix bypass in rule 933210 (Walter Hop) [#2033]
 * Improve sampling mode efficiency (Paul Beckett) [#2094]
 * Move rules to the lowest phase possible based on their inputs (Ervin Hegedus) [#1941]
 * Stop decoding things twice (Federico G. Schwindt) [#1845]
 * contributing.md: add more information for new developers (Andrew Howe) [#2487]
 * Move 'ecairn' from scanners to crawlers (Felipe Zipitría) [#2408]
 * 93231x rules: simplify already-lowercased regexps (Felipe Zipitría) [#2485]
 * remove double m,n in regexp (Felipe Zipitría) [#2484]
 * update OWASP vulnerability urls (Walter Hop) [#2467]
 * docs: update policy to include signed releases (Felipe Zipitría) [#2465]
 * Change documentation git module link to https (İlteriş Eroğlu) [#2461]
 * Optimize regex in 942440 (Felipe Zipitría) [#2459]
 * Improve performance by removing unnecessary lowercase transformations (Jozef Sudolský) [#2106]
 * change-version: fix typo (Deepshikha Sinha) [#2430]
 * Renaming tx.blocking_early to tx.early_blocking (Christian Folini) [#2414]
 * Add editorconfig file to keep spacing in good shape (Felipe Zipitría) [#2407]
 * Remove all whitespace at EOL (Felipe Zipitría) [#2405, #2406]
 * 920520: improve comment (Max Leske) [#2391]
 * Fix yamllint (Felipe Zipitría) [#2387]
 * README: fix typos (Priyam Patel) [#2494]
 * Initialization: fix typo (Elia Pinto) [#2366]
 * Fix changed Trustwave URLs (Elia Pinto, henkworks, Felipe Zipitría) [#2213, #2364, #2204]
 * Improve logging in some special cases (Jozef Sudolský) [#2347]
 * Rename nodejs to generic category (Felipe Zipitría) [#2340]
 * Fixed assembly of 920120-no-backtracking.data (Max leske) [#2333]
 * Move regexp-assembly to separate directory (Felipe Zipitría) [#2327]
 * Fix attack type of a few rules (Jozef Sudolský) [#2324]
 * Optimize regex in 942400 (Jozef Sudolský) [#2323]
 * Web shells: optimize regexps (Jozef Sudolský) [#2315]
 * Move 941120 from PL1 to PL2 (Christian Folini) [#2306]
 * Move 920300 from PL2 to PL3 (Franziska Bühler) [#2013]
 * Fix ReDOS in rule 942350 (Andrea Menin) [#2300]
 * Fix ReDOS in rule 941140 (Andrea Menin) [#2050]
 * Fix false negative in rule 920480 (katef, Federico G. Schwindt) [#1957]
 * Disassemble regexp in rule 930100 (Andrew Howe) [#2298]
 * Amend 920300 to exclude CONNECT requests (Andrew Howe) [#2297]
 * Restrict rule 941170 (Andrea Menin) [#2292]
 * Fix NextCloud example comments (Joost de Keijzer) [#2282]
 * Fix ruleid typos in comments (Paul Beckett) [#2263]
 * Fix capec id for crawlers (Jozef Sudolský) [#2258]
 * Fix docs for Apache (Jozef Sudolský) [#2238]
 * Align actions in right order (Ervin Hegedus) [#2237]
 * Fix logging by moving ctl action in chain to 2nd rule (Franziska Bühler) [#2202]
 * Fix rule 9004110 to use newer format for var (Andrew Howe) [#2200]
 * Remove the fuzzy regularity of the 942310 rule (NiceYouKnow) [#2189]
 * docs: update links and format of known bugs (Felipe Zipitría) [#2186]
 * Added missing " from the end of actions list (Ervin Hegedus) [#2184]
 * sponsors.md: add file (Christian Folini) [#2174]
 * crs-setup.conf: add note to allowed_request_content_type settings (Ervin Hegedus) [#2164]
 * README: update for Nginx (vijayasija99) [#2158]
 * Replace usage of ctl:ruleEngine=Off by ctl:ruleRemoveByTag=OWASP_CRS (Jozef Sudolský) [#2156]
 * Remove old commented-out rule 910110 (Paul Beckett) [#2148]
 * Replace Blacklist and Whitelist with Deny list and Allow list (Paul Beckett) [#2137]
 * Fix donate URL (Felipe Zipitría) [#2132]
 * Owncloud: Fix rule 9003001 to match both dav and webdav (Abu Dawud) [#2130]
 * Add link to slack invitation to README (Christian Folini) [#2122]
 * Fix bug in rule 942190 and add test case (NiceYouKnow, Max Leske, Franziska Bühler) [#2112]
 * Added directories needed for volume mounts to Git (Max Leske) [#2103]
 * Added a note to a commented rule about unsupported action in v3 (Ervin Hegedus) [#2098]
 * Added missing space after comment mark (Ervin Hegedus) [#2097]
 * Fix typo in sampling mode description (Christian Folini) [#2090]
 * contributing.md: rewording (Christian Folini) [#2077]
 * Replaced ARGS by ARGS_GET in rules in phase:1 (Ervin Hegedus) [#2063]
 * Fix OWASP Slack URL (Jozef Sudolský) [#2056]
 * Add example exclusion rule for monitoring agents (Andrea Menin) [#2037]
 * Fix Nginx logging in docker-compose (Felipe Zipitría) [#2036]
 * Fix Sec-CH-UA and Sec-CH-UA-Mobile request header validation (somechris) [#2028]
 * Fix typo in comment (Federico G. Schwindt) [#2011]
 * Fix magic number that crashes old PHP versions (Kyzentun, Walter Hop) [#2010]
 * Add timezone variable to docker-compose (Felipe Zipitría) [#1995]
 * Enhancement of installation process for Nginx / IIS (Jozef Sudolský) [#1988]
 * Removing %{MATCHED_VAR} from logging (Jozef Sudolský) [#1985]
 * Drop unneeded capture groups (Federico G. Schwindt) [#1983]
 * Add support for sec-ch-ua and sec-ch-ua-mobile within Validate Bytes (Chaim Sanders) [#1970]
 * Update description of rule 920350 (Christian Folini) [#1952]
 * Fix stricter sibling comment for SQL Injection (Stephen Sigwart) [#1913]
 * Fix chained condition for correlation rules 980120 and 980150 (Simon Studer) [#1898]
 * Link fix for docs/OWASP-CRS-Documentation submodule (Ervin Hegedus) [#1885]
 * Add missing PL tags to all rules (Ervin Hegedus) [#1882]
 * Remove 'log' from rules and let SecDefaultAction decide what to do (Federico G. Schwindt) [#1876]
 * Remove unneeded transformation from MATCHED_VARS (Federico G. Schwindt) [#1852]
 * Fix indentations (Ervin Hegedus) [#1851]
 * Drop unneeded escapes (Federico G. Schwindt) [#1842]
 * Tests: 100% test coverage (Christian Folini, Franziska Bühler, Paul Beckett, Ervin Hegedus, Juan-Pablo Tosso, NiceYouKnow)
 * Tests: Normalized keys in test files (Ervin Hegedus) [#2493]
 * Tests: Fix test titles (bxlxx.wu, Ervin Hegedus) [#2504, #2497]
 * Tests: use same user-agent (Felipe Zipitría) [#2393]
 * Tests: fixed end boundary in 932180-2 (Ervin Hegedus) [#2377]
 * Tests: clean up quoting (Max Leske) [#2370]
 * Tests: add tests for 920120 (Max Leske) [#2369]
 * Tests: improve test setup, rewrite of log checker (Max Leske) [#2363]
 * Tests: add common and uniform http headers to tests (Felipe Zipitría) [#2362]
 * Tests: add tests for 921180 (Juan-Pablo Tosso, Christian Folini) [#2308]
 * Tests: add tests for 920275, 913101, 913102, 920410, 920171, 932190, 932110, 932105 (Ervin Hegedus) [#2021, #2253, #2257, #2294, #2295, #2285, #2286, #2287]
 * Tests: add tests for 932170, 932171, 932106, 932180, 942170, 942251, 942460 (Franziska Bühler) [#2252, #2254, #2255, #2280, #2283, #2284, #2269, #2268]
 * Tests: add tests for 933111, 933190, 933200 (NiceYouKnow) [#2281]
 * Tests: add tests for 920341 (Juan-Pablo Tosso) [#2266]
 * Tests: add tests for FP 921110 request smuggling (Franziska Bühler) [#2102]
 * Tests: Add a Chrome and Firefox version 100 UA (Mike Taylor) [#2325]
 * Tests: Add tests for 920121, 932150, 932160, 932120, 932130, 921151 (Paul Beckett) [#2264, #2275, #2276, #2272, #2273, #2270]
 * Tests: add test against FP when using urlDecode for 932140 (Max Leske) [#2191]
 * Tests: fix Python version for tests (Max Leske) [#2247]
 * Tests: fix 933160-21 and 942500-1 due to invalid URI (Takaya Saeki) [#2168]
 * Tests: remove broken test 932100-3 (Felipe Zipitría) [#2165]
 * Tests: fix logging problem for Nginx (vijayasija99) [#2157]
 * Tests: use only valid YAML (Felipe Zipitría) [#2080]
 * Tests: fix requirements version (nobletrout) [#2004]
 * Tests: fix tests lacking charset (Felipe Zipitría) [#1932]

Changes limited to documentation and tests:
 * docs: update SPONSORS.md for new release (Christian Folini) [#3341]
 * docs: update CONTRIBUTORS.md for new release (Ervin Hegedüs) [#3340]
 * docs: Transferred CHANGES to CHANGES.md (Felipe Zipitría) [#2606]
 * docs: Bring CONTRIBUTING.MD in line with documentation (Andrew Howe) [#2558]
 * docs: Add to CONTRIBUTING.MD chain rule commenting guidance (Ervin Hegedus) [#3196]
 * docs: Explained to leave audit log settings alone in CONTRIBUTING.md (Christian Folini) [#3090]
 * docs: update documentation hyperlinks on rules (Dexter Chang) [#3232]
 * docs: add documentation on blocking of archive file extensions that are not blocked by default (Andrew Howe) [#2758]
 * docs: fixed minor typo in comment in file rules/restricted-files.data (Homesteady) [#3305]
 * docs: Add note of lack of rule range support in ModSecv3 (Andrew Howe) [#3303]
 * docs: sync CONTRIBUTING.MD with HTML version (Andrew Howe) [#3301]
 * docs: fix typos across the entire project as reported by codespell (Ervin Hegedus) [#2519]
 * tests: fix duplicated tests for rule 934130 PL1 (Walter Hop) [#2918]
 * tests: add test for rule 941130 PL1 (Paul Beckett) [#2923]
 * tests: increase tests (920280-3, 920430-3, 920430-9) compatibility with other proxies (Matteo Pace) [#3134]
 * tests: detection of *nix RCE using multiple variable assignments (932200 PL2) (Christian Folini) [#2899]
 * tests: additional tests for use in PHP wrappers in PHP injection attacks (rule 933200 PL1) (Andrew Howe) [#2723]
 * tests: Add positive test 920100-16 for rule 920100 PL1 (Andrew Howe) [#2952]
 * tests: Add positive test 920190-3 for rule 920190 PL1 (Andrew Howe) [#2956]
 * tests: Add positive test 921120-4 for rule 921120 PL1 (Andrew Howe) [#3083]
 * tests: Add positive test 920340-3 for rule 920340 PL1 (Andrew Howe) [#2972]
 * tests: Add positive test 920250-4 for rule 920250 PL1 (Andrew Howe) [#2971]
 * tests: Add positive test 920470-18 for rule 920470 PL1 (Andrew Howe) [#3058]
 * tests: Add positive test 921150-2 for rule 921150 PL1 (Andrew Howe) [#3158]
 * tests: Add positive test 932160-8 for rule 932160 PL1 (Christian Folini) [#2997]
 * tests: add test for `sql_compileoption_used` detection (rule 942151 PL1) (Andrew Howe) [#2714]
 * tests: Rearranged tests for rule 920400 PL1 (Matteo Pace) [#2877]
 * tests: fixed URLs tests for rules 934130 PL1 and 934131 PL2 (Matteo Pace) [#3133]
 * tests: fixed URLs tests for rule 932130 PL1 (Matteo Pace) [#2880]
 * tests: Rearranged tests for rule 920340 (Christian Folini) [#3089]
 * tests: add test for rule 941140 PL1 (Franziska Bühler) [#2995]
 * tests: add test for rule 941170 PL1 (Franziska Bühler) [#2994]
 * tests: add test for rule 941200 PL1 (Franziska Bühler) [#2993]
 * tests: add test for rule 941240 PL1 (Franziska Bühler) [#2975]
 * tests: add test for rule 941310 PL1 (Franziska Bühler) [#2974]
 * tests: add test for rule 941400 PL1 (Franziska Bühler) [#2969]
 * tests: add test for rule 942170 PL1 (Franziska Bühler) [#2968]
 * tests: add test for rule 942270 PL1 (Franziska Bühler) [#2967]
 * tests: add test for rule 942350 PL1 (Franziska Bühler) [#2965]
 * tests: add test for rule 942500 PL1 (Franziska Bühler) [#2964]
 * tests: add test for rule 943100 PL1 (Franziska Bühler) [#2962]
 * tests: add test for rule 942520 PL2 (Franziska Bühler) [#2706]
 * tests: add tests for rules 942521 and 942522 PL2 (Franziska Bühler) [#2708]
 * tests: fix tests on rule 932200 to detect FPs (Max Leske) [#3309]
 * tests: deprecate ftw in favor of go-ftw (Felipe Zipitría) [#3076]
 * tests: remove Accept-Charset from test files (Felipe Zipitría) [#2781]
 * tests: enable utf8 encoding validation (Felipe Zipitría) [#2992]
 * tests: fix test using old syntax and add go-ftw check (Felipe Zipitría) [#2715]
 * tests: extend coverage for rule 932220 (Felipe Zipitría) [#3063]
 * tests: extend coverage for rule 932120 (Felipe Zipitría) [#2996]
 * tests: extend coverage for rule 932200 (Felipe Zipitría) [#2950]
 * tests: add test to prove we cover complex shell variables usage in rule 932230 (Felipe Zipitría) [#2966]



## Version 3.3.2 - 2021-06-30

Fixes and improvements:
 * Fix CVE-2021-35368 WAF bypass using pathinfo (Christian Folini)

## Version 3.3.0 - 2020-07-01

Important changes:
 * The format of crs-setup.conf variable "tx.allowed_request_content_type" has been changed to be more in line with the other variables. If you have overridden this variable, please see the example in crs-setup.conf for the new separator to use.

New functionality:
 * Block backup files ending with ~ in filename (Andrea Menin)
 * Detect ffuf vuln scanner (Will Woodson)
 * Detect Nuclei vuln scanner (azurit)
 * Detect SemrushBot crawler (Christian Folini)
 * Detect WFuzz vuln scanner (azurit)
 * New LDAP injection rule (Christian Folini)
 * New HTTP Splitting rule (Andrea Menin)
 * Add .swp to restricted extensions (Andrea Menin)
 * Allow CloudEvents content types (Bobby Earl)
 * Add CAPEC tags for attack classification (Fernando Outeda, Christian Folini)
 * Detect Unix RCE bypass techniques via uninitialized variables, string concatenations and globbing patterns (Andrea Menin)

Removed functionality:
 * Removed outdated rule tags WASCTC, OWASP_TOP_10, OWASP_AppSensor/RE1, and OWASP_CRS/FOO/BAR; note that tags 'OWASP_CRS' and 'attack-type' are kept. (Christian Folini)

Improved compatibility:
 * Changed variable to lowercase (modsec3 behavior fix) (Ervin Hegedus)

Fixes and improvements:
 * WordPress: Add support for upload image/media in Gutenberg Editor (agusmu)
 * Prevent bypass of rule 921110 (Amit Klein, Franziska Bühler)
 * Prevent bypass of rule 921130 (Amit Klein, Franziska Bühler)
 * fix CVE msg in rules 944120 944240 (Fernando Outeda)
 * Remove broken or no longer used files (Federico G. Schwindt)
 * Make content-type case insensitive (Franziska Bühler)
 * Move /util/docker folder from v3.3/dev branch to dedicated repo (Peter Bittner)
 * feat(lint): split actions in linting and regression (Felipe Zipitria)
 * Fix FP in 921120 (Franziska Bühler)
 * Add missing OWASP_CRS tags (Christian Folini)
 * Fix GHA badges (Federico G. Schwindt)
 * feat(badge): add apache license badge
 * fix typos found by fossies codespell (Tim Herren)
 * Decrease processing time of rules (Ervin Hegedüs)
 * handle multiple directives in 920510 (Andrea Menin)
 * handle multiple directives in 920510 (Andrea Menin)
 * fix(ci): use log_contains instead (Felipe Zipitria)
 * Move test where it belongs (Federico G. Schwindt)
 * fix(ci): use docker in DetectionOnly (Felipe Zipitria)
 * fix(rule): remove dangling whitespace (Felipe Zipitria)
 * fix(ci): run actions on .github change (Felipe Zipitria)
 * fix(docs): update badges and links in readme (Felipe Zipitria)
 * README: update repo link (Walter Hop)
 * Update README: Copyright 2019 -> 2020 (Christian Folini)
 * fix(ci): run tests also on PRs (Felipe Zipitria)
 * fix(ci): change test name and fix default params (Felipe Zipitria)
 * Restore Travis Status (was in the wrong repo) (Christian Folini)
 * Remove outdated Travis status after migration (Christian Folini)
 * feat(ci): adds github actions testing (Felipe Zipitria)
 * fix(migration): post migration tasks (Felipe Zipitria)
 * feat(templates): add text to gihub templates about migration. To be reverted after migation is done. (Felipe Zipitria)
 * Added more explanations to comment of 920300 (Christian Folini)
 * Added 'ver' action with current version to all necessary rules (Ervin Hegedus)
 * Update nextcloud excl rules and shorten var (Franziska Bühler)
 * Change to preferred lowercase var (Franziska Bühler)
 * Set var to lowercase and change comment (Franziska Bühler)
 * Resolve issue with allowed_request_content_types (Franziska Bühler)
 * Allow REPORT requests without Content-Type header in Nextcloud (pyllyukko)
 * Suppress rule 200002 when editing contacts in Nextcloud (pyllyukko)
 * XenForo: update exclusions (Walter Hop)
 * WordPress: exclude additional URL fields in profile editor (Walter Hop)
 * add www to link (NullIsNot0)
 * Fix link for 941310 Old link does not work anymore. Change it to new one. (NullIsNot0)
 * Add Content-Type: multipart/related as allowed default (jeremyjpj0916)
 * Resolve issue 1722 and fix content-type whitelisting (Franziska Bühler)
 * make severities and scores consistent (Walter Hop)
 * add QQGameHall UA (#1731) (Andrea Menin)
 * another test (Allan Boll)
 * Add word boundaries around values in SQL tautologies (942130) (Allan Boll)
 * Move tests to their own file, while here also correct permissions for 920180. (Federico G. Schwindt)
 * Rule to check if both C-L and T-E are present (#1310) (Federico G. Schwindt)
 * Fixes for 2 tests in 921200 (Christian Folini)
 * XenForo: add exclusions, remove unnecessary chains (#1673) (Walter Hop)
 * Fix FPs for 942350 (#1706) (Franziska Bühler)
 * Fix typos found by codespell / Fossies project (#1702) (Simon Studer)
 * Ignore check of CT header in POST request if protocol is HTTP/2 (Ervin Hegedus)
 * Narrowing down the subpattern .*? in 941130 (Christian Folini)
 * Restricting a wide regex a bit (Christian Folini)
 * Drop escapes (Christian Folini)
 * Fix FP in 941130 and rearrange regex with new regex-assemble file (Christian Folini)
 * Ignore check of CT header in POST request if protocol is HTTP/2 (Ervin Hegedus)
 * Remove trailing dot in several msg actions (#1678) (Tim Herren)
 * Replace REQUEST_BODY with ARGS on 930100 and 930110 (#1659) (Andrea Menin)
 * Temporary travis workaround to buy time and fix it for good (#1684) (Andrea Menin)
 * Add regression tests (Franziska Bühler)
 * Fix FP with create with 942360 (Franziska Bühler)
 * Avoid embedded anchors in CRS rule 942330 (Allan Boll)
 * Update 942450 for less false positives, more tests (#1662) (Will Woodson)
 * Ensure single ranges are also checked (#1661) (Federico G. Schwindt)
 * WordPress: also exclude posts/pages endpoint in subdirectories (Walter Hop)
 * For bugs, also ask for the environment (#1657) (Federico G. Schwindt)
 * XenForo: fix incorrect escape (Walter Hop)
 * XenForo: additional exclusions (Walter Hop)
 * Pattern cleanup across several rules (#1643). Drop unneeded non-capture groups; No need to escape "-" outside character classes And only if it is not at the end. (Federico G. Schwindt)
 * Improve rule 941350: Previously, this rule will also match on the equivalent to "<..<". Rewrite it so it is only triggered by the equivalent to "<..>", simplifying the pattern quite a bit as a bonus. While here add a link describing the bypass for future reference.
 * Fix test Was using the equivalent to "<...<" instead of "<...>". (Federico G. Schwindt)
 * Move the help and support link to contacts (#1647) While here rename to ensure they are presented in the right order and minor cosmetics. (Federico G. Schwindt)
 * Move remaining regression test data file to new folder, cleanup README (#1646) (Peter Bittner)
 * Also ask for the paranoia level (Federico G. Schwindt)
 * Make it a tiny bit more colorful (Federico G. Schwindt)
 * Spacing (Federico G. Schwindt)
 * Fix emoji (Federico G. Schwindt)
 * Switch to multiple templates for github issues (#1644) (Federico G. Schwindt)
 * Fix paranoia-level log description (Andrea Menin)
 * change IRC to Slack (Walter Hop)
 * fix spacing (Walter Hop)
 * Moving tests and documentation folders (#1627) (Soufiane Benali)
 * add triggered rule (#1636) (Andrea Menin)
 * Drop the translate header from the restricted list Fixes #1410. (Federico G. Schwindt)
 * Mark stale issues (Federico G. Schwindt)
 * Added support for <? in Rule 933100 (meetug)
 * Added test cases (NullIsNot0)
 * Update REQUEST-920-PROTOCOL-ENFORCEMENT.conf (NullIsNot0)
 * Update re for Rule ID: 920480 Update regular expression (NullIsNot0)
 * Create SECURITY.md (Chaim Sanders)
 * Rule: 920480. Make rx recognize charset with quotes. Make rule ID: 920480 recognize not only Content-Type: charset=utf-8 but also charset put in single or double quotes: Content-Type: charset="utf-8" Content-Type: charset='utf-8' (NullIsNot0)
 * Make rule 933100 RE2 compatible (meetug)
 * Fix typo in config file inclusion (Felipe Zipitria)
 * Correct rule 941310 to use single-byte variants and fix FPs (#1596). Fix test to use the single byte characters Add a test that uses utf-8 as well. Change pattern to use the single-byte variants Patterns in ModSecurity are not treated as UTF strings. Fixes #1595. Add negative tests and update descriptions Improve pattern Change it to avoid FPs for \xbc\xbc and \xbe\xbe (i.e. << and >>). Use negated classes for better performance. (Federico G. Schwindt)
 * Add test for issue #1580 (#1612) (Federico G. Schwindt)
 * removes t:lowercase (Andrea Menin)
 * Move integration tests to their own job (#1608) Also cleanup branches' list. (Federico G. Schwindt)
 * Add PL1 tag. (Anna Winkler)
 * Change version number for full version name (Felipe Zipitria)
 * Better document legacy conversion procedure Add text with instructions for a simple conversion utility. (Felipe Zipitria)
 * Correct example text regarding GeoIP. Add maxmind tool for downloading files (Felipe Zipitria)
 * Ignore configuration files generated by the JetBrains editors (Anna Winkler)
 * Update name of branch to use for feature branches. Minor syntax updates. (Anna Winkler)
 * Minor optimisation (Emile-Hugo SPIR)
 * Also fix the `as herefrom` pattern (Emile-Hugo SPIR)
 * More conservative fix (Emile-Hugo SPIR)
 * Update the source file (Emile-Hugo SPIR)
 * Fix a FP (`, aside from`) (Emile-Hugo SPIR)
 * regression fix for #1581 (emphazer)
 * Change order to check ip first in both rules (Felipe Zipitria)
 * Change chain order (Felipe Zipitria)
 * Fix spacing in text (Felipe Zipitria)
 * Add link to mailing list archives (Felipe Zipitria)
 * Adding new test for 941150 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941340 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941280 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941170 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941250 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941220 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941330 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941300 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941230 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941260 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941290 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 941270 based on XSS cheatsheet by portswigger (Christian Folini)
 * Adding new test for 942180 based on XSS cheatsheet by portswigger (Christian Folini)
 * Update mailing list links to google group (Felipe Zipitria)
 * Fix typo and add 2 new entries to 941160 (Franziska Bühler)
 * Switch to dates in YYYY-MM-DD format IOW iso 8601. While here add newlines and drop empty categories. (Federico G. Schwindt)
 * Update badges, add v3.3 and remove v3.0 (#1557) (Federico G. Schwindt)
 * Rearange characters and add positive and negative test cases. Moved the dash to the end of the character set to avoid escaping it. Added test with all the new characters and a test for multiple whitespaces. Allowed a previously blocked charset. (Tim Herren)
 * 920470: include chars from rfc 2046 RFC 2046 allows additional chars for the boundary. \d removed as it is covered by \w in the regex. Removed unnecessary escapes. (Tim Herren)
 * Fix bypass in 931130 Don't rely on beginsWith as it might allow attackers to create subdomains matching the prefix. Add tests to cover this and other cases. The latter fixes #1404. (Federico G. Schwindt)
 * fix rule regex due to remove t:removeComments (Andrea Menin)
 * 920470: include chars from rfc 2046 RFC 2046 allows additional chars for the boundary. \d removed as it is covered by \w in the regex. Removed unnecessary escapes. (Tim Herren)
 * update Dockerfiles and Travis to use v3.3/dev (Walter Hop)

## Version 3.2.0 - 2019-09-24

New functionality:
 * Add AngularJS client side template injection 941380 PL2 (Franziska Bühler)
 * Add docker-compose.yaml and example rule exclusion files for docker-compose (Franziska Bühler)
 * Add extended access.log format to Docker (Franziska Bühler)
 * Add libinjection check on last path segment (Max Leske, Christian Folini)
 * Add PUBLIC identifier for XML entities (#1490) (Rufus125)
 * Add .rdb to default restricted_extensions (Walter Hop)
 * Add .swp to default restricted_extensions (Andrea Menin)
 * Add rule 933200 PHP Wrappers (Andrea Menin)
 * Add send-payload-pls.sh script to test payload against multiple paranoia levels (Christian Folini, Manuel Spartan)
 * Add support for shell evasions with $IFS (Walter Hop, Chaim Sanders)
 * Add unix-shell commands (Christoph Hansen, Chaim Sanders)
 * Also inspect the path for the script tag (Federico G. Schwindt)
 * Detect 80legs, sysscan, Gobuster scanners (Brent Clark)
 * Detect CGI source code leakages (Christoph Hansen, Walter Hop)
 * Detect 'crawler' user-agent (Federico G. Schwindt)
 * Detect Jorgee, Zgrab scanners (Walter Hop)
 * Detect MySQL in-line comments (Franziska Bühler)
 * Detect Wappalyzer scanner (Christian Folini, Chaim Sanders)
 * Java RCE: Add struts namespaces (Walter Hop)
 * Java RCE: Detect more java classes (Manuel Leos)
 * Javascript: Add 941370 preventing a bypass for 941180 (Andrea Menin)
 * Make CRS variables configurable in Docker image (Franziska Bühler)
 * New PL3 rule 920490 to protect against content-type charset bypassing (Christian Folini)
 * Node.js unserialization + javascript RCE snippets (Walter Hop)
 * Request smuggling: Also cover pre http/1.0 requests (Federico G. Schwindt)
 * Restricted files: Added many dotfiles (Dan Ehrlich)
 * SQLi bypass detection: ticks and backticks (Franziska Bühler)
 * XenForo rule exclusion profile (Walter Hop)

Removed functionality:
 * Remove unused protected_uploads setting from setup (Walter Hop)
 * Remove deprecated tx.msg and tx.%{rule.id}-... (Federico G. Schwindt)
 * Remove deprecated upgrade script (Walter Hop)

Improved compatibility:
 * Add OWASP_CRS tags for ModSec 3 changes and replace ruleRemoveTargetByTag arguments (Ervin Hegedus)
 * Replace @contain % with @rx 25; ModSec 3 fails to parse % by itself (or escaped). (Federico G. Schwindt)
 * RE2 compatibility for 941130, 920220, 920240, 920230, 920460, 942200, 942370 (Allan Boll)
 * Hyperscan compatibility and simplification for 942450 (Allan Boll)

Fixes and improvements:
 * 932140: fix ReDoS in FOR expression (Walter Hop)
 * 933200: Simplify pattern (Federico G. Schwindt, Andrea Menin)
 * 941380: fix anomaly score variable (Franziska Bühler)
 * 942510, 942511: fix anomaly score variable (Walter Hop)
 * Add content-type application/csp-report (Andrea Menin)
 * Add content-type application/xss-auditor-report (Andrea Menin)
 * Add CRS 3.2 Badge build support. (Chaim Sanders)
 * Add CVE numbers for Apache Struts vulnerabilities to comments in rules (Franziska Bühler)
 * Add CVE-2018-11776 to comments of 933160 and 933161 (Franziska Bühler)
 * Add CVE-2018-2380 to comments of rules (Franziska Bühler)
 * Add default env vars for anomaly scores in Docker (Franziska Bühler)
 * Add missing OWASP_CRS tags to 921xxx rules (Walter Hop)
 * Add REQUEST_FILENAME to rule id 944130 and add exploits to comment (Franziska Bühler)
 * Add spaces in front of closing square brackets (Franziska Bühler)
 * Add travis changes (#1316) (Chaim Sanders)
 * Allow dot characters in Content-Type multipart boundary (Walter Hop)
 * Also handle dot variant of X_Filename. PHP will transform dots to underscore in variable names since dot is invalid. (Federico G. Schwindt)
 * As per the ref manual, it is compressWhitespace (Federico G. Schwindt)
 * Avoid php leak false positive with WOFF files (Manuel Spartan)
 * Bring back CRS 2.x renumbering utility (Walter Hop)
 * Clean up travis and reorg (Federico G. Schwindt)
 * Code cosmetics: reorder the actions of rules (Ervin Hegedus)
 * Content-Type is case insensitive (Federico G. Schwindt)
 * Disassembled 941160 (Franziska Bühler)
 * Drop separate regexp files. They are not really needed and save us from updating multiple places. (Federico G. Schwindt)
 * Drop t:lowercase from 941350 (Federico G. Schwindt)
 * Drop unneeded capture groups and tidy up (Federico G. Schwindt)
 * Drop unneeded capture groups and tidy up regexps (Federico G. Schwindt)
 * Drop unneeded unicode from 941110. Add tests to cover a few more variants as well as a negative test (Federico G. Schwindt)
 * Fix 920440 "URL file extension is restricted by policy" regex (Andrea Menin)
 * Fix 920460 test (Federico G. Schwindt)
 * Fix 942101 and 942460 by adding to sqli_score variable (Christian Folini)
 * Fix checking the existence of 'HTTP' trailing request verb and request path in the payload for HTTP request smuggling; decreases false-positives on free-form text. (Yu Yagihashi)
 * Fix commit default for non 2.9 branch (Chaim Sanders)
 * Fix CRS2->CRS3 mapping table (973344 -> 941100) (Chaim Sanders)
 * Fix date (Chaim Sanders)
 * Fix Docker image SSL support (Franziska Bühler)
 * Fix duplicate .env (jschleus, Chaim Sanders)
 * Fix executing paranoia level counters (Christian Folini)
 * Fix indentation and python version in crs2-renumbering script (Chaim Sanders)
 * Fix input / headers misordering (Christian Folini)
 * Fix path traversal attack pattern at id:930110 (Ervin Hegedus)
 * Fix regexp in Docker image (Franziska Bühler)
 * Fix regexp with incorrect dot '.' escape in rule 943120 (XeroChen)
 * Fix request header Sec-Fetch-User false positive (na1ex)
 * Fix runaway regexp in 942260. Add variant regexp assemble script to handle possessive qualifiers. Use possessive qualifiers to tight this up and solve ReDoS problem. (Federico G. Schwindt)
 * Fix small typo in variable (Felipe Zipitria)
 * Fix spelling error in variable name (supplient)
 * Fix transform name pointed out by secrules_parsing (Federico G. Schwindt)
 * Fix Travis Merge not being able to find HEAD (Chaim Sanders)
 * Fix vulnerable regexp in rule 942490 (CVE-2019-11387) (Christoph Hansen)
 * Fix wrong regex, assembly result, in 942370 (Franziska Bühler)
 * INSTALL: advise to use release zips, remove upgrade.py, update Nginx (Walter Hop)
 * Java: change tag from COMMAND_INJECTION to JAVA_INJECTION (Manuel Spartan)
 * Jwall auditconsole outbound anomaly scoring requirements (Christoph Hansen)
 * Mark patterns not supported by re2 (Federico G. Schwindt)
 * Move duplicated 900270 to 900280 Fixes #1236. (Federico G. Schwindt)
 * Move PROXYLOCATION var (Franziska Bühler)
 * PHP: move get_defined_functions() and friends into PL1 (Walter Hop)
 * Pin the ftw version to 1.1.7 for now (Federico G. Schwindt)
 * Prevent bypass 933180 PHP Variable Function (Andrea Menin)
 * Reduce comments, introduction of triggered exploits (Franziska Bühler)
 * Remove all trailing spaces from ftw yaml test files (Ervin Hegedus)
 * Remove auditlog No other rules specify it. Add missing quotes and drop rev (Federico G. Schwindt)
 * Remove capture, remove tx.0, add transformation functions, fix regex, add presentation link (Andrea Menin)
 * Remove old and unwanted setvar constructs (Federico G. Schwindt)
 * Remove superfluous comments (Walter Hop)
 * Remove superfluous pmf (Federico G. Schwindt)
 * Remove t:lowercase from 920490 (Christian Folini)
 * Remove WARNING from php-errors.data (Andrea Menin)
 * Reorder actions (Federico G. Schwindt)
 * Replacing all @pmf with @pmFromFile (Christian Treutler)
 * Restricted-files.data: add AWS config (Walter Hop)
 * SQLI: removed unnecessary + (Christoph Hansen)
 * Switch Docker image to owasp/modsecurity:2.9-apache-ubuntu (Federico G. Schwindt)
 * unix-shell.data: fix typo in 'more' (Walter Hop)
 * Update .travis.yml Update to support v3.1 (Chaim Sanders)
 * Update dockerfile to always use 3.2/dev (Federico G. Schwindt)
 * Update OWASP CRS Docker image to support the new upstream and 2.9.3 (Peter Bittner, Chaim Sanders)
 * Update RESPONSE-950-DATA-LEAKAGES.conf (Christoph Hansen)
 * Update RESPONSE-959-BLOCKING-EVALUATION.conf (Christoph Hansen)
 * Wordpress: add support for Gutenberg editor (siric_, Walter Hop)
 * Wordpress: allow searching for any term in admin posts/pages overview (Walter Hop)
 * WordPress: exclude Gutenberg via rest_route (Walter Hop)
 * WordPress: exclude some more profile.php fields from RFI rule (Walter Hop)
 * WordPress: exclude SQL comment rule from _wp_http_referer (Walter Hop)
 * XML Soap Encoding fix 920240 (Christoph Hansen)

Unit tests:
 * 932140: add regression tests (Walter Hop)
 * 933180: fix tests which were doing nothing (Walter Hop)
 * 941370: add some more tests, fix whitespace (Walter Hop)
 * Add more tests for 941130 (Christian Folini)
 * Add regression test for 941101 (Avery Wong)
 * Add regression tests for 942150, 942100, 942260 (Christian Folini)
 * Add regression tests to 941160 (Franziska Bühler)
 * Add some regression tests (Ervin Hegedus)
 * Add testing support for libmodsecurity running on Apache and Nginx (Chaim Sanders)
 * Add tests for 941360 that fights JSFuck and Hieroglyphy (Christian Folini)
 * Add tests for rule 921110 (Yu Yagihashi)
 * Added regression tests for rules 942320, 942360, 942361, 942210, 942380, 942410, 942470, 942120, 942240, 942160, 942190, 942140, 942490, 942120 (Christoph Hansen)
 * Drop tests for removed rules (Federico G. Schwindt)
 * Fix failing regression tests (Ervin Hegedus)
 * Fix failing tests (Manuel Spartan, Chaim Sanders)
 * Fix readme typos in example rule (Walter Hop)
 * Fix test 941110-2 (Federico G. Schwindt)
 * Fix YAML 1.2 compliance with "true" (Federico G. Schwindt)
 * RCE: Add tests for the for command (Federico G. Schwindt)
 * Update regression tests for rules 931110, 931120, 931130 (Simon Studer)

Documentation:
 * Add details to README for Dockerhub (Franziska Bühler)
 * Add intro/comment to CVE comments (Franziska Bühler)
 * CONTRIBUTING: add note about separate PRs (Walter Hop)
 * Erased gitter chat. Added CII badge (Felipe Zipitria)
 * Replaced descriptions (Christian Folini)
 * Summarized authors on single line in tests for 941160 (Christian Folini)
 * Update broken link in regexp-assemble blog URLs (Walter Hop)
 * Update CONTRIBUTING.md To base changes on v3.2/dev. (Felipe Zipitría)
 * Update CONTRIBUTORS order (Andrea Menin)
 * Update README.md (Rufus125)
 * Updating crs site location (Chaim Sanders)

## Version 3.1.1 - 2019-06-26

 * Fix CVE-2019-11387 ReDoS against CRS on ModSecurity 3 at PL 2 (Christoph Hansen, Federico G. Schwindt)
 * Content-Type made case insensitive in 920240, 920400 (Federico G. Schwindt)
 * Allow % encoding in 920240 (Christoph Hansen)
 * Fix bug in 920440 (Andrea Menin)
 * Fix bug in 920470 (Walter Hop)
 * Reduce false positives in 921110 (Yu Yagihashi, Federico G. Schwindt)
 * Fix bug in 943120 (XeroChen)

## Version 3.1.0 - 2018-08-07

 * Add Detectify scanner (Andrea Menin)
 * Renaming matched_var/s (Victor Hora)
 * Remove lines with bare '#' comment char (Walter Hop)
 * Drop the XML variable from rule 932190 (Federico G. Schwindt)
 * Update outdated URLs (Walter Hop)
 * remove unused rule 901180 (Walter Hop)
 * Drop exit from unix and windows RCE (Federico G. Schwindt)
 * Fix anomaly_score counters (Federico G. Schwindt)
 * Remove mostly redundant 944220 in favor of 944240 (Christian Folini)
 * Add self[ and document[ to rule 941180 (Andrea Menin)
 * Provide proxy support within CRS docker image (Scott O'Neil)
 * Prevent bypass in rule 930120 PL3 (Andrea Menin)
 * Fix small typo in variable (Felipe Zipitría)
 * Fix bug #1166 in Docker image (Franziska Bühler)
 * Remove revision status from rules (Federico G. Schwindt)
 * Add template for issues (Federico G. Schwindt)
 * Correct failing travis tests in merge situations (Federico G. Schwindt)
 * Remove unused global variable in IIS rules (Chaim Sanders)
 * Refactor to use phase number instead of name (Federico G. Schwindt)
 * Add uploaded file name check; refresh LFI / filename checks (Walter Hop)
 * Introduce critical sibling of 920340 in PL2 (Walter Hop)
 * Fix bypass caused by multiple spaces in RCE rules (Walter Hop)
 * Remove unneeded regex capture groups (Federico G. Schwindt)
 * Add built-in exceptions for CPanel (Christoph Hansen)
 * Add additional file restrictios for ws_ftp, DS_Store... (Jose Nazario)
 * Fix missing strings in 942410 (Franziska Bühler)
 * Add 2 missing PDO errors (Christoph Hansen)
 * Fix issues with FPs in regression tests (Chaim Sanders)
 * Add Nextcloud client exclusion support (Christoph Hansen)
 * Fix spelling mistakes in REQUEST-942- (Padraig Doran, Chaim Sanders)
 * Explicitly ignore the user defined rules (Aaron Haaf, Chaim Sanders)
 * Add regression tests for 942490 (Christoph Hansen, Chaim Sanders)
 * Add Owncloud client exclusion support (Christoph Hansen, Christian Folini)
 * Adding 'F-Secure Radar' vulnerability scanner UA (Christian Folini, Chaim Sanders)
 * Update DockerFile to use Ubuntu as base (Chaim Sanders)
 * False positives 942360: move alter and union (Franziska Bühler, Chaim Sanders)
 * Add support for Java style attacks (Manuel Spartan, Walter Hop)
 * Fix various regression tests issues caused by webserver handling (azhao155, Chaim Sanders)
 * Update TravisCI to build on a per PR basis (Chaim Sanders)
 * Optimized rule 921160 and regex (Allan Boll, Chaim Sanders)
 * Update the consistency across various files (Federico G. Schwindt)
 * Add missing transform, 944120 sibling 944240 (Manuel Spartan)
 * Fix false positive for 'like' in 942120 (Walter Hop)
 * Add regression tests for Java Rules (Manuel Spartan)
 * Fixup and small reorg of dokuwiki rule exclusion package (Christian Folini)
 * Make TravisCI tests fail if Apache can't load rules (Felipe Zipitría)
 * Add exclusion rules for Dokuwiki (Matt Bagley, Christian Folini)
 * Initial exclusions for NextCloud installs (Matt Bagley, Christian Folini)
 * Added struts-pwn UA to list (Manuel Spartan)
 * Uses MULTIPART_MISSING_SEMICOLON instead of MULTIPART_SEMICOLON_MISSING (Felipe Zimmerle)
 * Add file upload checks (Manuel Spartan)
 * Check if Transfer-Encoding is missing (Federico G. Schwindt, Christian Folini)
 * Remove duplicated variables (Federico G. Schwindt)
 * Reduce FP by splitting classic SQL injection rule 942370 (Christoph Hansen)
 * Fix typo in REQUEST-920-PROTOCOL-ENFORCEMENT (ihacku, Franziska Bühler)
 * Add configurable timestamp format to FTW integration (Christian Folini)
 * Add badges to README (Felipe Zipitría)
 * Add clarifying comments to 910110 (Christian Folini)
 * Making rule 933131 case-insensitive (Manuel Spartan)
 * Merge and reorder rules as part of cleanup (Federico G. Schwindt)
 * Update copyright date and syntax (Jose Nazario, Felipe Zipitría)
 * Updated SecMarker and SkipAfter names to use meet guidelines (Felipe Zipitría)
 * Tidy up single quotes and other guidelines updates (Felipe Zipitría)
 * Syntax fix for setvar crs_exclusions_wordpress (Manuel Spartan)
 * Updated various contributors to developers (Christian Folini)
 * Revise SQL rules by disassembling them into their core protections (Franziska Bühler)
 * Add an example payload to 920220 (coolt)
 * Add a missing regex to rule 942310 (Franziska Bühler)
 * Detect GET or HEAD with Transfer-Encoding header (Federico G. Schwindt)
 * Fix broken links in references (Pásztor Gábor)
 * Add contributing guidelines (Felipe Zipitría)
 * Fix processing bypasses in rule 931130 (Felipe Zipitría, Christian Folini)
 * Correct small omissions in unix-shell.data (Walter Hop)
 * Add IIS specific detection to LFI-os-files.data (Manuel Spartan)
 * Update examples to match the current cleanup (Federico G. Schwindt)
 * Corrected the ordering of actions to meet guidelines (Felipe Zipitría)
 * Remove unused capture groups (Federico G. Schwindt)
 * Use explicit rx operator (Federico G. Schwindt)
 * Update the RCE regular expressions(Walter Hop, Federico G. Schwindt)
 * Removing maturity & accuracy from rules (Felipe Zipitría)
 * Increasing range header (Christoph Hansen)
 * Fixed upgrade.py script argument options (Glyn Mooney)
 * Updating to reflect OWASP flagship status (Chaim Sanders)
 * Adding Docker support for CRS (Chaim Sanders)
 * Initial Travis deployment (Zack Allen, Walter Hop)
 * Initial commit of regression tests (Chaim Sanders, Walter Hop)
 * Remove test for 921170 because it won't ever fire (Chaim Sanders, Walter Hop)
 * Update minor incorrectness in asp.net regex (Chaim Sanders, Walter Hop)
 * Add notification for builds against #modsecurity on freenode (Zack Allen, Walter Hop)
 * Add all past code contributors and convert to markdown (Walter Hop)
 * Block uploads of files with .phps extension (Walter Hop)
 * Improve message for script upload with superfluous extension (Walter Hop)
 * Remove trailing whitespace in various regexs (Walter Hop)
 * Add command popd to direct unix rce list in rule 932150 (Franziska Bühler)
 * Remove unnecessary END_XSS_CHECKS marker (Christian Folini)
 * Ignore Whitespaces in Rule 942110 (Christoph Hansen)
 * Update missing RCE Commands (Umar Farook)
 * Update lfi-os-files.data (Umar Farook)
 * Removed deprecated t:removeComments from 942100 (Christian Folini)
 * Add word boundary to rule 942410 (Franziska Bühler)

## Version 3.0.2 - 2017-05-12

 * Remove debug rule that popped up in 3.0.1 (Christian Folini)


## Version 3.0.1 - 2017-05-09

 * SECURITY: Removed insecure handling of X-Forwarded-For header;
   reported by Christoph Hansen (Walter Hop)
 * Fixed documentation errors in RESPONSE-999-... (Chaim Sanders)
 * Reduced FPs on 942190 by adding a word boundary to regex (Franziska Bühler)
 * Reduced FPs on 932150 by removing keyword reset (Franziska Bühler)
 * Tidied exceptions in 930100 (Roberto Paprocki)
 * Reduced FPs for 920120 by splitting into stricter sibling (Franziska Bühler)
 * Simplified some Drupal rule exclusions (Damien McKenna, Christian Folini)
 * Extended KNOWN_BUGS with remarks on JSON support on Debian (Franziska Bühler)
 * Updated README to add gitter support (Chaim Sanders)
 * Clarified DoS documentation for static extensions (Roberto Paprocki)
 * Added application/octet-stream to allowed content types (Christian Folini)
 * Typo in 942220 alert message (Chaim Sanders, @bossloper)
 * Moved referrer check of 941100 into new PL2 rule (Franziska Bühler)
 * Closed multiple @pmf evasions via lowercase transformation (Roberto Paprocki)
 * Clarified libinjection bundling in INSTALL file (@cjdp)
 * Reduced FPs via Wordpress Rule Exclusions (Walter Hop)
 * Support for RFC 3902 (Content Type application/soap+xml; Christoph Hansen)
   Make sure you update ModSecurity recommended rule 200000 as well.
 * Bugfix in 942410 regex (Christian Folini)
 * Reduced FPs for 942360 (Walter Hop)
 * Reduced FPs for 941120 by restricting event handler names (Franziska Bühler)
 * Extended 931000 with scheme "file" to fix false negative (Federico Schwindt)
 * Extended 905100 and 905110 for HTTP/2.0 (includes bugfix, Christoph Hansen)
 * Moved 941150 from PL1 to PL2; includes Bugfix for rule (Christian Folini)
 * Updated documentation for 920260 (Chaim Sanders)
 * Bugfix in upgrade.py (Victor Hora)
 * Fixed FP in RCE rule 932140 (Walter Hop)
 * Fixed comment for arg limit check rule 920370 (Christian Folini)
 * Created CONTRIBUTORS file
 * Added Christoph Hansen (emphazer) to CONTRIBUTORS file
 * Added Franziska Bühler (Franziska Bühler) to CONTRIBUTORS file
 * Fixed bug with DoS rule 912160 (@loudly-soft, Christian Folini)


## Version 3.0.0 - 2016-11-10

Huge changeset running in separate branch from September 2013 to September 2016.
This is a cursory summary of the most important changes:

 * Huge reduction of false positives (Ryan Barnett, Felipe Zimmerle, Chaim
   Sanders, Walter Hop, Christian Folini)
 * Anomaly scoring is the new default, renamed thresholds from
   tx.(in|out)bound_anomaly_score_level to
   tx.(in|out)bound_anomaly_score_threshold
 * Introduction of libinjection for SQLi detection
 * Introduction of libinjection for XSS detection
 * Big improvement on detection of Remote Command Execution (Walter Hop)
 * Big improvement on PHP function name detection (Walter Hop)
 * Paranoia Mode (Christian Folini, Noël Zindel, Franziska Bühler,
   Manuel Leos, Walter Hop)
 * Shifted dozens of rules into higher paranoia levels
 * Introduced a lot of stricter sibling rules in higher levels
 * Generic mechanism to support application specific rule exclusions
   (Chaim Sanders)
 * Initial Wordpress rule exclusions (Walter Hop)
 * Initial Drupal rule exclusions (Christian Folini, @emphazer)
 * Renumbering of rules. See folder id_renumbering for a
   csv map (Chaim Sanders)
 * Consolidation of rules, namely XSS and SQLi (Spider Labs/Trustwave team)
 * Sampling mode / Easing in (Christian Folini)
 * Cleanup of reputation checks / persistent blocking
   (Christian Folini / Walter Hop)
 * Tags much more systematic (Walter Hop)
 * IP reputation checks / persistent blocking of certain clients
   (Spider Labs/Trustwave team)
 * Phase actions use request/response/logging now instead of
   numerical phases (Spider Labs/Trustwave team)
 * Added NoScript XSS Filters (Spider Labs/Trustwave team)
 * Updated "severity" action to use words (CRITICAL, WARNING, etc...)
   vs. numbers (5, 4, etc..)
 * Various regex fixes after research by Vladimir Ivanov (Chaim Sanders)
 * Overhaul of the regression mode into debug mode (Walter Hop, Ryan Barnett)
 * Introduction of util/upgrade.py (Walter Hop)
 * Removal of GeoIP database. Download via util/upgrade.py now.
 * Introduction of Initialization rules with
   default values (Walter Hop, Christian Folini)
 * Sorting out terminology with
   whitelisting and rule exclusions (Christian Folini)
 * Overhaul of testing (Chaim Sanders)
 * Protection from HTTP Parameter Pollution (Franziska Bühler)
 * Simplification of setup config file, renamed file to crs-setup.conf.example
 * Improved session fixation detection logic (Christian Peron, credits to
   Eric Hodel for the discovery)
 * Updated list of malicious webscanners
 * Splitting scanner user agents data files (github user @ygrek)
 * Countless bugfixes in severities, anomaly scores, tags, etc.
   across the board
 * Cleanup of formerly experimental DDoS rules,
   fix documentation (Ryan Barnett, Christian Folini)
 * Improves http blacklist checks (Walter Hop)
 * Extended XSS detection (as suggested by Mazin Ahmed)
 * Added support for Travis CI
 * Added support for HTTP/2 in recent Apache 2.4 (Walter Hop)
 * Added many, many bots and scanners (among others suggested by
   github user @toby78, @jamuse, Matt Koch)
 * Fixed mime types suitable for XML processor (Chaim Sanders)
 * Include script in util/join-multiline-rules to work around
   Apache 2.4 < 2.4.11 bug with long lines (Walter Hop)
 * New detection for request smuggling attacks (Achim Hofmann,
   Christian Folini)
 * Fixes with project honeypot setup (Ryan Barnett)
 * Separated DB / SQL messages by DB software (Ryan Barnett)
 * CPanel integration (Chaim Sanders)
 * Introduction of var for static resources (Chaim Sanders)
 * Many improvements to rules in 2014/5 (Ryan Barnett)


## Version 2.2.9 - 2013-09-30

Improvements:
* Updated the /util directory structure


Bug Fixes:
* fix 950901 - word boundary added
* modsecurity_35_bad_robots.data - gecko/25 blocks Firefox Android
  https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/157


## Version 2.2.8 - 2013-06-30

Improvements:
* Updatd the /util directory structure
* Added scripts to check Rule ID duplicates
* Added script to remove v2.7 actions so older ModSecurity rules will work
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/pull/43
* Added new PHP rule (958977) to detect PHP exploits (Plesk 0-day from king cope)
  - http://seclists.org/fulldisclosure/2013/Jun/21
  - http://blog.spiderlabs.com/2013/06/honeypot-alert-active-exploits-attempts-for-plesk-vulnerability-.html


Bug Fixes:
* fix 950901 - word boundary added
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/pull/48
* fix regex error
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/pull/44
* Updated the Regex in 981244 to include word boundaries
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/36
* Problem with Regression Test (Invalid use of backslash) - Rule 960911 - Test2
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/34
* ModSecurity: No action id present within the rule - ignore_static.conf
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/17
* "Bad robots" rule blocks all Java applets on Windows XP machines
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/16
* duplicated rules id 981173
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/18


## Version 2.2.7 - 2012-12-19

Improvements:
* Added JS Overrides file to identify successful XSS probes
* Added new XSS Detection Rules from Ashar Javed (http://twitter.com/soaj1664ashar)
  - http://jsfiddle.net/U9RmU/4/
* Updated the SQLi Filters to add in Oracle specific functions
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/pull/7

Bug Fixes:
* Fixed Session Hijacking rules
  - https://github.com/SpiderLabs/owasp-modsecurity-crs/pull/8
* Fixed bug in XSS rules checking TX:PM_XSS_SCORE variable


## Version 2.2.6 - 2012-09-14

Improvements:
* Started rule formatting update for better readability
* Added maturity and accuracy action data to each rule
* Updated rule revision (rev) action
* Added rule version (ver) action
* Added more regression tests (util/regression_tests/)
* Modified Rule ID 960342 to block large file attachments in phase:1
* Removed all PARANOID rule checks
* Added new Session Fixation rules

Bug Fixes:
* Fixed missing ending double-quotes in XSS rules file
* Moved SecDefaultAction setting from phase:2 to phase:1
* Fixed Session Hijacking SessionID Regex
  https://www.modsecurity.org/tracker/browse/CORERULES-79
* Changed the variable listing for many generic attack rules to exclude REQUEST_FILENAME
  https://www.modsecurity.org/tracker/browse/CORERULES-78


## Version 2.2.5 - 2012-06-14

Security Fixes:
* Updated the anomaly scoring value for rule ID 960000 to critical
  (Identified by Qualys Vulnerability & Malware Research Labs (VMRL))
  (https://community.qualys.com/blogs/securitylabs/2012/06/15/modsecurity-and-modsecurity-core-rule-set-multipart-bypasses)
* Updated Content-Type check to fix possible evasion with @within
  (Identified by Qualys Vulnerability & Malware Research Labs (VMRL))
  (https://community.qualys.com/blogs/securitylabs/2012/06/15/modsecurity-and-modsecurity-core-rule-set-multipart-bypasses)

Improvements:
* Renamed main config file to modsecurity_crs_10_setup.conf
* Updated the rule IDs to start from CRS reserved range: 900000
* Updated rule formatting for readability
* Updated the CSRF rules to use UNIQUE_ID as the token source
* Added the zap2modsec.pl script to the /util directory which converts
  OWASP ZAP Scanner XML data into ModSecurity Virtual Patches
* Updated the Directory Traversal Signatures to include more obfuscated data
* Added Arachni Scanner Integration Lua script/rules files

Bug Fixes:
* Added forceRequestBodyVariable action to rule ID 960904


## Version 2.2.4 - 2012-03-14

Improvements:
* Added Location and Set-Cookie checks to Response Splitting rule ID 950910
* Added a README file to the activated_rules directory
* Consolidate a number of SQL Injection rules into optimized regexs
* Removed multiMatch and replaceComments from SQL Injection rules
* Updated the SQLi regexs for greediness
* Updated the SQLi setvar anomaly score values to use macro expansion
* Removed PARANOID mode rules

Bug Fixes:
* Fixed missing comma before severity action in rules 958291, 958230 and 958231
* Fixed duplidate rule IDs


## Version 2.2.3 - 2011-12-19

Improvements:
* Added Watcher Cookie Checks to optional_rules/modsecurity_crs_55_appication_defects.conf file
  http://websecuritytool.codeplex.com/wikipage?title=Checks#cookies
* Added Watcher Charset Checks to optional_rules/modsecurity_crs_55_application_defects.conf file
  http://websecuritytool.codeplex.com/wikipage?title=Checks#charset
* Added Watcher Header Checks to optional_rules/modsecurity_crs_55_application_defects.conf file
  http://websecuritytool.codeplex.com/wikipage?title=Checks#header

Bug Fixes:
* Fixed Content-Type evasion issue by adding ctl:forceRequestBodyVariable action to
  rule ID 960010. (Identified by Andrew Wilson of Trustwave SpiderLabs).
* Updated the regex and added tags for RFI rules.


## Version 2.2.2 - 2011-09-28


Improvements:
* Updated the AppSensor Profiling (to use Lua scripts) for Request Exceptions Detection Points
* Added new Range header detection checks to prevent Apache DoS
* Added new Security Scanner User-Agent strings
* Added example script to the /util directory to convert Arachni DAST scanner
  XML data into ModSecurity virtual patching rules.
* Updated the SQLi Character Anomaly Detection Rules
* Added Host header info to the RESOURCE collection key for AppSensor profiling rules

Bug Fixes:
* Fixed action list for XSS rules (replaced pass,nolog,auditlog with block)
* Fixed Request Limit rules by removing & from variables
* Fixed Session Hijacking IP/UA hash captures
* Updated the SQLi regex for rule ID 981242


## Version 2.2.1 - 2011-07-20


Improvements:
* Extensive SQL Injection signature updates as a result of the SQLi Challenge
  http://www.modsecurity.org/demo/challenge.html
* Updated the SQL Error message detection in response bodies
* Updated SQL Injection signatures to include more DB functions
* Updated the WEAK SQL Injection signatures
* Added tag AppSensor/RE8 to rule ID 960018

Bug Fixes:
* Fixed Bad Robot logic for rule ID 990012 to further qualify User-Agent matches
  https://www.modsecurity.org/tracker/browse/CORERULES-70
* Fixed Session Hijacking rules to properly capture IP address network hashes.
* Added the multiMatch action to the SQLi rules
* Fixed a false negative logic flaw within the advanced_filter_converter.lua script
* Fixed missing : in id action in DoS ruleset.
* Updated rule ID 971150 signature to remove ;


## Version 2.2.0 - 2011-05-26


Improvements:
* Changed Licensing from GPLv2 to Apache Software License v2 (ASLv2)
  http://www.apache.org/licenses/LICENSE-2.0.txt
* Created new INSTALL file outlining quick config setup
* Added a new rule regression testing framework to the /util directory
* Added new activated_rules directory which will allow users to place symlinks pointing
  to files they want to run.  This allows for easier Apache Include wild-carding
* Adding in new RULE_MATURITY and RULE_ACCURACY tags
* Adding in a check for X-Forwarded-For source IP when creating IP collection
* Added new Application Defect checks (55 app defect file) from Watcher tool (Check Charset)
  http://websecuritytool.codeplex.com/wikipage?title=Checks#charset
* Added new AppSensor rules to experimental_dir
  https://owasp.org/www-project-appsensor/
* Added new Generic Malicious JS checks in outbound content
* Added experimental IP Forensic rules to gather Client hostname/whois info
  http://blog.spiderlabs.com/2010/11/detecting-malice-with-modsecurity-ip-forensics.html
* Added support for Mozilla's Content Security Policy (CSP) to the experimental_rules
  http://blog.spiderlabs.com/2011/04/modsecurity-advanced-topic-of-the-week-integrating-content-security-policy-csp.html
* Global collection in the 10 file now uses the Host Request Header as the collection key.
  This allows for per-site global collections.
* Added new SpiderLabs Research (SLR) rules directory (slr_rules) for known vulnerabilities.
  This includes both converted web rules from Emerging Threats (ET) and from SLR Team.
* Added new SLR rule packs for known application vulns for WordPress, Joomla and phpBB
* Added experimental rules for detecting Open Proxy Abuse
  http://blog.spiderlabs.com/2011/03/detecting-malice-with-modsecurity-open-proxy-abuse.html
* Added experimental Passive Vulnerability Scanning ruleset using OSVDB and Lua API
  http://blog.spiderlabs.com/2011/02/modsecurity-advanced-topic-of-the-week-passive-vulnerability-scanning-part-1-osvdb-checks.html
* Added additional URI Request Validation rule to the 20 protocol violations file (Rule ID - 981227)
* Added new SQLi detection rules (959070, 959071 and 959072)
* Added "Toata dragostea mea pentru diavola" to the malicious User-Agent data
  https://www.modsecurity.org/tracker/browse/CORERULES-64

Bug Fixes:
* Assigned IDs to all active SecRules/SecActions
* Removed rule inversion (!) from rule ID 960902
* Fixed false negative issue in Response Splitting Rule
* Fixed false negative issue with @validateByteRange check
* Updated the TARGETS listing for rule ID 950908
* Updated TX data for REQBODY processing
* Changed the pass action to block in the RFI rules in the 40 generic file
* Updated RFI regex to catch IP address usage in hostname
  https://www.modsecurity.org/tracker/browse/CORERULES-68
* Changed REQUEST_URI_RAW variable to REQUEST_LINE in SLR rules to allow matches on request methods.
* Updated the RFI rules in the 40 generic attacks conf file to remove explicit logging actions.
  They will now inherit the settings from the SecDefaultAction


## Version 2.1.2 - 2011-02-17


Improvements:
* Added experimental real-time application profiling ruleset.
* Added experimental Lua script for profiling the # of page scripts, iframes, etc..
  which will help to identify successful XSS attacks and planting of malware links.
* Added new CSRF detection rule which will trigger if a subsequent request comes too
  quickly (need to use the Ignore Static Content rules).

Bug Fixes:
* Added missing " in the skipAfter SecAction in the CC Detection rule set


## Version 2.1.1 - 2010-12-30


Bug Fixes:
* Updated the 10 config conf file to add in pass action to User-Agent rule
* Updated the CSRF ruleset to conditionally do content injection - if the
  csrf token was created by the session hijacking conf file
* Updated the session hijacking conf file to only enforce rules if a SessionID
  Cookie was submitted
* Fixed macro expansion setvar bug in the restricted file extension rule
* Moved the comment spam data file into the optional_rules directory


## Version 2.1.0 - 2010-12-29


Improvements:
* Added Experimental Lua Converter script to normalize payloads. Based on
  PHPIDS Converter code and it used with the advanced filters conf file.
* Changed the name of PHPIDS converted rules to Advanced Filters
* Added Ignore Static Content (Performance enhancement) rule set
* Added XML Enabler (Web Services) rule set which will parse XML data
* Added Authorized Vulnerability Scanning (AVS) Whitelist rule set
* Added Denial of Service (DoS) Protection rule set
* Added Slow HTTP DoS (Connection Consumption) Protection rule set
* Added Brute Force Attack Protection rule set
* Added Session Hijacking Detection rule set
* Added Username Tracking rule set
* Added Authentication Tracking rule set
* Added Anti-Virus Scanning of File Attachments rule set
* Added AV Scanning program to /util directory
* Added Credit Card Usage Tracking/Leakage Prevention rule set
* Added experimental CC Track/PAN Leakage Prevention rule set
* Added an experimental_rules directory to hold new BETA rules
* Moved the local exceptions conf file back into base_rules directory however
  it has a ".example" extension to prevent overwriting customized versions
  when upgrading
* Separated out HTTP Parameter Pollution and Restricted Character Anomaly Detection rules to
  the experimental_rules directory
* Adding the REQUEST_HEADERS:User-Agent macro data to the initcol in 10 config file, which will
  help to make collections a bit more unique



## Version 2.0.10 - 2010-11-29


Improvements:
* Commented out the Anomaly Scoring Blocking Mode TX variable since, by default, the CRS
  is running in traditional mode.

Bug Fixes:
* Moved all skipAfter actions in chained rules to chain starter SecRules
  https://www.modsecurity.org/tracker/browse/MODSEC-159
* Changed phases on several rules in the 20 protocol anomaly rules file to phase:1 to avoid FNs



## Version 2.0.9 - 2010-11-17


Improvements:
* Changed the name of the main config file to modsecurity_crs_10_config.conf.example so that
  it will not overwrite existing config settings.  Users should rename this file to activate
  it.
* Traditional detection mode is now the current default
* Users can now more easily toggle between traditional/standard mode vs. anomaly scoring mode
  by editing the modsecurity_crs_10_config.conf file
* Updated the disruptive actions in most rules to use "block" action instead of "pass".  This
  is to allow for the toggling between traditional vs. anomaly scoring modes.
* Removed logging actions from most rules so that it can be controlled from the SecDefaultAction
  setting in the modsecurity_crs_10_config.conf file
* Updated the anomaly scores in the modsecurity_crs_10_config.conf file to more closely match
  what is used in the PHPIDS rules.  These still have the same factor of severity even though
  the numbers themselves are smaller.
* Updated the 49 and 59 blocking rules to include the matched logdata
* Updated the TAG data to further classify attack/vuln categories.
* Updated the SQL Injection filters to detect more boolean logic attacks
* Moved some files to optional_rules directory (phpids, Emerging Threats rules)

Bug Fixes:
* Fixed Rule ID 960023 in optional_rules/modsecurity_crs_40_experimental.conf is missing 1 single quote
  https://www.modsecurity.org/tracker/browse/CORERULES-63
* Moved all skipAfter actions in chained rules to the rule starter line (must have ModSec v2.5.13 or higher)
  https://www.modsecurity.org/tracker/browse/MODSEC-159
* Fixed restricted file extension bug with macro expansion
  https://www.modsecurity.org/tracker/browse/CORERULES-60
* Updated the SQLI TX variable macro expansion data in the 49 and 60 files so that
  it matches what is being set in the sql injection conf file
* Fixed typo in SQL Injection regexs - missing backslash for word boundary (b)
  https://www.modsecurity.org/tracker/browse/CORERULES-62


## Version 2.0.8 - 2010-08-27


Improvements:
* Updated the PHPIDS filters
* Updated the SQL Injection filters to detect boolean attacks (1<2, foo == bar, etc..)
* Updated the SQL Injection filters to account for different quotes
* Added UTF-8 encoding validation support to the modsecurity_crs_10_config.conf file
* Added Rule ID 950109 to detect multiple URL encodings
* Added two experimental rules to detect anomalous use of special characters

Bug Fixes:
* Fixed Encoding Detection RegEx (950107 and 950108)
* Fixed rules-updater.pl script to better handle whitespace
  https://www.modsecurity.org/tracker/browse/MODSEC-167
* Fixed missing pass action bug in modsecurity_crs_21_protocol_anomalies.conf
  https://www.modsecurity.org/tracker/browse/CORERULES-55
* Fixed the anomaly scoring in the modsecurity_crs_41_phpids_filters.conf file
  https://www.modsecurity.org/tracker/browse/CORERULES-54
* Updated XSS rule id 958001 to improve the .cookie regex to reduce false positives
  https://www.modsecurity.org/tracker/browse/CORERULES-29


## Version 2.0.7 - 2010-06-04


Improvements:
* Added CSRF Protection Ruleset which will use Content Injection to add javascript to
  specific outbound data and then validate the csrf token on subsequent requests.
* Added new Application Defect Ruleset which will identify/fix missing HTTPOnly cookie
  flags
* Added Experimental XSS/Missing Output Escaping Ruleset which looks for user supplied
  data being echoed back to user unchanged.
* Added rules-updater.pl script and configuration file to allow users to automatically
  download CRS rules from the CRS rules repository.
* Added new SQLi keyword for ciel() and reverse() functions.
* Updated the PHPIDS filters


Bug Fixes:
* Fixed false positives for Request Header Name matching in the 30 file by
  adding boundary characters.
* Added missing pass actions to @pmFromFile prequalifier rules
* Added backslash to SQLi regex
  https://www.modsecurity.org/tracker/browse/CORERULES-41
* Fixed hard coded anomaly score in PHPIDS filter file
  https://www.modsecurity.org/tracker/browse/CORERULES-45
* Fixed restricted_extension false positive by adding boundary characters


## Version 2.0.6 - 2010-02-26


Bug Fixes:
* Added missing transformation functions to SQLi rules.
  https://www.modsecurity.org/tracker/browse/CORERULES-32
* Fixed duplicate rule IDs.
  https://www.modsecurity.org/tracker/browse/CORERULES-33
* Fixed typo in @pmFromFile in the Comment SPAM rules
  https://www.modsecurity.org/tracker/browse/CORERULES-34
* Added macro expansion to Restricted Headers rule
  https://www.modsecurity.org/tracker/browse/CORERULES-35
* Fixed misspelled SecMarker
  https://www.modsecurity.org/tracker/browse/CORERULES-36
* Fixed missing chain action in Content-Type header check
  https://www.modsecurity.org/tracker/browse/CORERULES-37
* Update phpids filters to use pass action instead of block


## Version 2.0.5 - 2010-02-01


Improvements:
* Removed previous 10 config files as they may conflict with local customized Mod configs.
* Added a new 10 config file that allows the user to globally set TX variables to turn on/off
  PARANOID_MODE inspection, set anomaly score levels and http policies.
  Must have ModSecurity 2.5.12 to use the macro expansion in numeric operators.
* Added Rule Logic and Reference links to rules descriptions.
* Added Rule IDs to all rules.
* Added tag data mapping to new OWASP Top 10 and AppSensor Projects, WASC Threat Classification
* Removed Apache limit directives from the 23 file
* Added macro expansion to 23 file checks.
* Added @pmFromFile check to 35 bad robots file
* Added malicious UA strings to 35 bad robots check
* Created an experimental rules file
* Updated HTTP Parameter Pollution (HPP) rule logic to concat data into a TX variable for inspection
* Removed TX inspections for generic attacks and reverted to standard ARGS inspection
  https://www.modsecurity.org/tracker/browse/MODSEC-120
* Updated the variable list for standard inspections (ARGS|ARGS_NAMES|XML:/*) and moved the other
  variables to the PARANOID list (REQUEST_URI|REQUEST_BODY|REQUEST_HEADERS|TX:HPP_DATA)
* Moved converted ET Snort rules to the /optional_rules directory
* Created a new Header Tagging ruleset (optional_rules) that will add matched rule data to the
  request headers.
* Updated Inbound blocking conf file to use macro expansion from the 10 config file settings
* Added separate anomaly scores for inbound, outbound and total to be evaluated for blocking.
* Updated the regex logic in the (1=1) rule to factor in quotes and other logical operators.
* Updated the SPAMMER RBL check rules logic to only check once per IP/Day.
* Added new outbound malware link detection rules.
* Added PHP "call_user_func" to blacklist
  Identified by SOGETI ESEC R&D

Bug Fixes:
* Removed Non-numeric Rule IDs
  https://www.modsecurity.org/tracker/browse/CORERULES-28
* Updated the variable list on SQLi rules.
* Fixed outbound @pmFromFile action from allow to skipAfter to allow for outbound anomaly scoring
  and blocking


## Version 2.0.4 - 2009-11-30


Improvements:
* Updated converted PHPIDS signatures (https://svn.php-ids.org/svn/trunk/lib/IDS/default_filter.xml)
* Updated PHPIDS rules logic to first search for payloads in ARGS and then if there is no match found
  then search more generically in request_body|request_uri_raw
* Updated PHPIDS rules logic to only set TX variables and to not log.  This allows for more clean
  exceptions in the 48 file which can then expire/delete false positive TX matches and adjust the
  anomaly scores.  These rules will then inspect for any TX variables in phase:5 and create appropriate
  alerts for any variable matches that exist.

Bug Fixes:
* Added Anomaly Score check to the 60 correlation file to recheck the anomaly score at the end of
  phase:4 which would allow for blocking based on information leakage issues.


## Version 2.0.3 - 2009-11-05


Improvements:
* Updated converted PHPIDS signatures (https://svn.php-ids.org/svn/trunk/lib/IDS/default_filter.xml)
* Create a new PHPIDS Converter rules file (https://svn.php-ids.org/svn/trunk/lib/IDS/Converter.php)
* Added new rules to identify multipart/form-data bypass attempts
* Increased anomaly scoring (+100) for REQBODY_PROCESSOR_ERROR alerts

Bug Fixes:
* Added t:urlDecodeUni transformation function to phpids rules to fix both false positives/negatives
  https://www.modsecurity.org/tracker/browse/CORERULES-17
* Added new variable locations to the phpids filters
  https://www.modsecurity.org/tracker/browse/CORERULES-19
* Use of transformation functions can cause false negatives - added multiMatch action to phpids rules
  https://www.modsecurity.org/tracker/browse/CORERULES-20
* Fixed multipart parsing evasion issues by adding strict parsing rules
  https://www.modsecurity.org/tracker/browse/CORERULES-21
* Fixed typo in xss rules (missing |)
  https://www.modsecurity.org/tracker/browse/CORERULES-22
* Fixed regex text in IE8 XSS filters (changed to lowercase)
  https://www.modsecurity.org/tracker/browse/CORERULES-23


## Version 2.0.2 - 2009-09-11


Improvements:
* Added converted PHPIDS signatures (https://svn.php-ids.org/svn/trunk/lib/IDS/default_filter.xml)
  https://www.modsecurity.org/tracker/browse/CORERULES-13

Bug Fixes:
* Rule 958297 - Fixed Comment SPAM UA false positive that triggered only on mozilla.
  https://www.modsecurity.org/tracker/browse/CORERULES-15


## Version 2.0.1 - 2009-08-07


Improvements:
* Updated the transformation functions used in the XSS/SQLi rules to improve performance
  https://www.modsecurity.org/tracker/browse/CORERULES-10

* Updated the variable/target list in the XSS rules
  https://www.modsecurity.org/tracker/browse/CORERULES-11

* Added XSS Filters from IE8
  https://www.modsecurity.org/tracker/browse/CORERULES-12

Bug Fixes:
* Rule 958297 - Fixed unescaped double-quote issue in Comment SPAM UA rule.
  https://www.modsecurity.org/tracker/browse/CORERULES-9


## Version 2.0.0 - 2009-07-29


New Rules & Features:
* Fine Grained Policy
    The rules have been split to having one signature per rule instead of having
    all signatures combined into one optimized regular expression.
    This should allow you to modify/disable events based on specific patterns
    instead of having to deal with the whole rule.
* Converted Snort Rules
    Emerging Threat web attack rules have been converted.
    http://www.emergingthreats.net/
* Anomaly Scoring Mode Option
    The rules have been updated to include anomaly scoring variables which allow
    you to evaluate the score at the end of phase:2 and phase:5 and decide on what
    logging and disruptive actions to take based on the score.
* Correlated Events
    There are rules in phase:5 that will provide some correlation between inbound
    events and outbound events and will provide a result of successful atttack or
    attempted attack.
* Updated Severity Ratings
    The severity ratings in the rules have been updated to the following:
    - 0: Emergency - is generated from correlation where there is an inbound attack and
         an outbound leakage.
    - 1: Alert - is generated from correlation where there is an inbound attack and an
         outbound application level error.
    - 2: Critical - is the highest severity level possible without correlation.  It is
         normally generated by the web attack rules (40 level files).
    - 3: Error - is generated mostly from outbound leakabe rules (50 level files).
    - 4: Warning - is generated by malicious client rules (35 level files).
    - 5: Notice - is generated by the Protocol policy and anomaly files.
    - 6: Info - is generated by the search engine clients (55 marketing file).
* Updated Comment SPAM Protections
    Updated rules to include RBL lookups and client fingerprinting concepts from
    Bad Behavior (www.bad-behavior.ioerror.us)
* Creation of Global Collection
    Automatically create a Global collection in the *10* config file.  Other rules
    can then access it.
* Use of Block Action
    Updated the rules to use the "block" action.  This allows the Admin to globally
    set the desired block action once with SecDefaultAction in the *10* config file
    rather than having to edit the disruptive actions in all of the rules or for
    the need to have multiple versions of the rules (blocking vs. non-blocking).
* "Possible HTTP Parameter Pollution Attack: Multiple Parameters with the same Name."
   http://tacticalwebappsec.blogspot.com/2009/05/http-parameter-pollution.html
* Added new generic RFI detection rules.
   http://tacticalwebappsec.blogspot.com/2009/06/generic-remote-file-inclusion-attack.html
* "Possibly malicious iframe tag in output" (Rules 981001,981002)
    Planting invisible iframes in a site can be used by attackers to point users
    from the victim site to their malicious site. This is actually as if the
    user was visiting the attacker's site himself, causing the user's browser to
    process the content in the attacker's site.

New Events:
* Rule 960019 - Expect Header Not Allowed.
* Rule 960020 - Pragma Header Requires Cache-Control Header
* Rule 958290 - Invalid Character in Request - Browsers should not send the (#) character
                as it is reserved for use as a fragment identifier within the html page.
* Rule 958291 - Range: field exists and begins with 0.
* Rule 958292 - Invalid Request Header Found.
* Rule 958293 - Lowercase Via Request Header Found.
* Rule 958294 - Common SPAM Proxies found in Via Request Header.
* Rule 958295 - Multiple/Conflicting Connection Header Data Found.
* Rule 958296 - Request Indicates a SPAM client accessed the Site.
* Rule 958297 - Common SPAM/Email Harvester crawler.
* Rule 958298 - Common SPAM/Email Harvester crawler

Bug Fixes:
* Rule 950107 - Split the rule into 2 separate rules to factor in the
                Content-Type when inspecting the REQUEST_BODY variable.
* Rule 960017 - Bug fix for when having port in the host header.
* Rule 960014 - Bug fix to correlate the SERVER_NAME variable.
* Rule 950801 - Increased the logic so that the rule will only run if the web site
                uses UTF-8 Encoding.
* Rules 999210,999211 - Bug fix to move ctl actions to last rule, add OPTIONS and
                        allow the IPv6 loopback address
* Rule 950117 - Updated the RFI logic to factor in both a trailing "?" in the ARG
                and to identify offsite hosts by comparing the ARG URI to the Host
                header.  Due to this rule now being stronger, moved it from optional
                tight security rule to *40* generic attacks file.

Other Fixes:
* Added more HTTP Protocol violations to *20* file.
* Set the SecDefaultAction in the *10* config file to log/pass (This was the
  default setting, however this sets it explicitly.
* Added SecResponseBodyLimitAction ProcessPartial to the *10* config file.  This
  was added so that when running the SecRuleEngine in DetectionOnly mode, it will
  not deny response bodies that go over the size restrictions.
* Changed SecServerSignature to "Apache/1.3.28"
* Fixed the use of SkipAfter and SecMarkers to make it consistent.  Now have
  BEGIN and END SecMarkers for rule groups to more accurately allow moving to
  proper locations.
* Fixed the @pm/@pmFromFile pre-qualifier logic to allow for operator inversion.
  This removes the need for some SecAction/SkipAfter rules.
* Updated rule formatting to easily show rule containers (SecMarkers, pre-qualifier
  rules and chained rules).


## Version 1.6.1 - 2008-04-22


* Fixed a bug where phases and transformations where not specified explicitly
    in rules. The issue affected a significant number of rules, and we strongly
    recommend to upgrade.


## Version 1.6.0 - 2008-02-19


New Rulesets & Features:
* 42 - Tight Security
    This ruleset contains currently 2 rules which are considered highly prone
    to FPs. They take care of Path Traversal attacks, and RFI attacks. This
    ruleset is included in the optional_rulesets dir
* 42 - Comment Spam
    Comment Spam is used by the spammers to increase their rating in search
    engines by posting links to their site in other sites that allow posting
    of comments and messages. The rules in this ruleset will work against that.
    (Requires ModSecurity 2.5)
* Tags
    A single type of attack is often detected by multiple rules. The new alert
    classification tags solve this issue by providing an alternative alert type
    indication and can serve for filtering and analysis of audit logs.
    The classification tags are hierarchical with slashes separating levels.
    Usually there are two levels with the top level describing the alert group
    and the lower level denoting the alert type itself, for example:
    WEB_ATTACK/SQL_INJECTION.

False Positives Fixes:
* Rule 960903 - Moved to phase 4 instead of 5 to avoid FPs
* Rule 950107 - Will look for invalid url decoding in variables that are not
                automatically url decoded

Additional rules logic:
* Using the new "logdata" action for logging the matched signature in rules
* When logging an event once, init the collection only if the alert needs to log
* Using the new operator @pm as a qualifier before large rules to enhance
    performance (Requires ModSecurity 2.5)
* SQL injection - A smarter regexp is used to detect 1=1,2=2,etc.. and not
    only 1=1. (Thanks to Marc Stern for the idea)
* New XSS signatures - iframe & flash XSS



## Version 1.5.1 - 2007-12-06


False Positives Fixes:
* Protocol Anomalies (file 21) - exception for Apache SSL pinger (Request: GET /)

New Events:
* 960019 - Detect HTTP/0.9 Requests
  HTTP/0.9 request are not common these days. This rule will log by default,
  and block in the blocking version of file 21

Other Fixes:
* File 40, Rules 950004,950005 - Repaired the correction for the double
  url decoding problem
* File 55 contained empty regular expressions. Fixed.


## Version 1.5 - 2007-11-23


New Rulesets:
* 23 - Request Limits
    "Judging by appearances". This rulesets contains rules blocking based on
    the size of the request, for example, a request with too many arguments
    will be denied.

Default policy changes:
* XML protection off by default
* BLOCKING dir renamed to optional_rules
* Ruleset 55 (marketing) is now optional (added to the optional_rules dir)
* Ruleset 21 - The exception for apache internal monitor will not log anymore

New Events:
* 960912 - Invalid request body
  Malformed content will not be parsed by modsecurity, but still there might
  be applications that will parse it, ignoring the errors.
* 960913 - Invalid Request
  Will trigger a security event when request was rejected by apache with
  code 400, without going through ModSecurity rules.

Additional rules logic:
* 950001 - New signature: delete from
* 950007 - New signature: waitfor delay

False Positives Fixes:
* 950006 - Will not be looking for /cc pattern in User-Agent header
* 950002 - "Internet Explorer" signature removed
* Double decoding bug used to cause FPs. Some of the parameters are already
  url-decoded by apache. This caused FPs when the rule performed another
  url-decoding transformation. The rules have been split so that parameters
  already decoded by apache will not be decoded by the rules anymore.
* 960911 - Expression is much more permissive now
* 950801 - Commented out entirely. NOTE: If your system uses UTF8 encoding,
           then you should uncomment this rule (in file 20)


version 1.4.3 - 2007-07-21


New Events:
* 950012 - HTTP Request Smuggling
  For more info on this attack:
  http://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf
* 960912 - Invalid request body
  Malformed content will not be parsed by modsecurity, but still there might
  be applications that will parse it, ignoring the errors.
* 960913 - Invalid Request
  Will trigger a security event when request was rejected by apache with
  code 400, without going through ModSecurity rules.

False Positives Fixes:
* 950107 - Will allow a % sign in the middle of a string as well
* 960911 - A more accurate expression based on the rfc:
            http://www.ietf.org/rfc/rfc2396.txt
* 950015 - Will not look for http/ pattern in the request headers

Additional rules logic:
* Since Apache applies scope directives only after ModSecurity phase 1
  this directives cannot be used to exclude phase 1 rules. Therefore
  we moved all inspection rules to phase 2.



version 1.4 build 2 - 2007-05-17


New Feature:
* Search for signatures in XML content
    XML Content will be parsed and ispected for signatures

New Events:
* 950116 - Unicode Full/Half Width Abuse Attack Attempt
    Full-width unicode can by used to bypass content inspection. Such encoding will be forbidden
    http://www.kb.cert.org/vuls/id/739224
* 960911 - Invalid HTTP request line
    Enforce request line to be valid, i.e.: <METHOD> <path> <HTTP version>
* 960904 - Request Missing Content-Type (when there is content)
    When a request contains content, the content-type must be specified. If not, the content will not be inspected
* 970018 - IIS installed in default location (any drive)
    Log once if IIS in installed in the /Inetpub directory (on any drive, not only C)
* 950019 - Email Injection
    Web forms used for sending mail (such as "tell a friend") are often manipulated by spammers for sending anonymous emails

Regular expressions fixes:
* Further optimization of some regular expressions (using the non-greediness operator)
    The non-greediness operator, <?>, prevents excessive backtracking

FP fixes:
* Rule 950107 - Will allow a parameter to end in a % sign from now on


version 1.4 - 2007-05-02


New Events:
* 970021 - WebLogic information disclosure
    Matching of "<title>JSP compile error</title>" in the response body, will trigger this rule, with severity 4 (Warning)
* 950015,950910,950911 - HTTP Response Splitting
    Looking for HTTP Response Splitting patterns as described in Amit Klein's excellent white paper:
    http://www.packetstormsecurity.org/papers/general/whitepaper_httpresponse.pdf
ModSecurity does not support compressed content at the moment. Thus, the following rules have been added:
* 960902 - Content-Encoding in request not supported
    Any incoming compressed request will be denied
* 960903 - Content-Encoding in response not supported
    An outgoing compressed response will be logged to alert, but ONLY ONCE.

False Positives Fixes:
* Removed <.exe>,<.shtml> from restricted extensions
* Will not be looking for SQL Injection signatures <root@>,<coalesce> in the Via request header
* Excluded Referer header from SQL injection, XSS and command injection rules
* Excluded X-OS-Prefs header from command injection rule
* Will be looking for command injection signatures in
  REQUEST_COOKIES|REQUEST_COOKIES_NAMES instead of REQUEST_HEADERS:Cookie.
* Allowing charset specification in the <application/x-www-form-urlencoded> Content-Type

Additional rules logic:
* Corrected match of OPTIONS method in event 960015
* Changed location for event 960014 (proxy access) to REQUEST_URI_RAW
* Moved all rules apart from method inspection from phase 1 to phase 2 -
    This will enable viewing content if such a rule triggers as well as setting
    exceptions using Apache scope tags.
* Added match for double quote in addition to single quote for <or x=x> signature (SQL Injection)
* Added 1=1 signature (SQL Injection)


version 1.3.2 build 4 2007-01-17


Fixed apache 2.4 dummy requests exclusion
Added persistent PDF UXSS detection rule


## Version 1.3.2 build 3 2007-01-10


Fixed regular expression in rule 960010 (file #30) to allow multipart form data
content


## Version 1.3.2 - 2006-12-27


New events:
* 960037  Directory is restricted by policy
* 960038  HTTP header is restricted by policy

Regular expressions fixes:
* Regular expressions with @ at end of beginning (for example "@import)
* Regular expressions with un-escaped "."
* Command Injections now always require certain characters both before and after the command. Important since many are common English words (finger, mail)
* The command injection wget is not searched in the UA header as it has different meaning there.
* LDAP Fixed to reduce FPs:
  + More accurate regular expressions
  + high bit characters not accepted between signature tokens.
* Do not detect <?xml as a PHP tag in both PHP injection and PHP source leakage
* Removed Java from automation UA
* When validating encoding, added regexp based chained rule that accepts both %xx and %uxxxxx encoding bypassing a limitation of "@validateUrlEncoding"

Additional rules logic:
* Checks for empty headers in addition to missing ones  (Host, Accept and User-Agent)
* OPTIONS method does not require an accept header.
* Apache keep alive request exception.
* PROPFIND and OPTIONS can be used without content-encoding (like HEAD and GET)
* Validate byte range checks by default only that no NULL char exists.
* Added CSS to allowed extensions in strict rule sets.
* Changed default action in file #50 to pass instead of deny.
* Moved IP host header from protocol violations to protocol anomalies.

Modified descriptions:
* 950107: URL Encoding Abuse Attack Attempt
* 950801: UTF8 Encoding Abuse Attack Attempt
* Added matched pattern in many events using capture and %{TX.0}
* Added ctl:auditLogParts=+E for outbound events and attacks to collect response.


## Version 1.2 - 2006-11-19


Changes:
+ Move all events to the range of events allocated to Thinking Stone, now Breach
by prefixing all event IDs with "9".
+ Reverse severities to follow the Syslog format used by ModSecurity, now 1 is
the highest and 5 the lowest.

Bug fixes:
+ Removed quotes from list of mime types inspected on exit (directive
SecResponseBodyMimeType)
+ Corrected "cd .." signature. Now the periods are escaped.
+ Too many FPs with events 950903 & 950905. Commented them out until fixed.


## Version 1.1 - 2006-10-18


Initial version
