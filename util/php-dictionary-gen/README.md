Use gen.sh to generate the dictionary files. The script will download the latest version of the PHP source code and generate the dictionary files from it. It will search the function on Github to count the number of uses. *Important*: First set GITHUB_TOKEN in gen.sh, bot.py requires GITHUB_TOKEN env variable.

filter_dict.py requires the `dict` package. `sudo apt install dict` or `brew install dict`
