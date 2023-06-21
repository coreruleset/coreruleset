# Generate dictionaries for PHP functions

1. Use `pipenv install` for get all the python dependencies. (see https://docs.pipenv.org/ for installing pipenv).
2. Enable the new environment by doing `pipenv shell`.
2. Set and export your GITHUB_TOKEN so you don't get rate limited by GitHub.
3. Use gen.sh to generate the dictionary files. The script will download the latest version of the PHP source code and
generate the dictionary files from it. It will search the function on Github to count the number of uses. *Important*:
