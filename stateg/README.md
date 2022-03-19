#StaTeG -> Static siTe Generator

## A simple command-line tool to convert Markdown files to HTML.
Compatible with versions from 3.9. (Older versions doesn't support too well the type hints.)

## Requirements:
The following python modules to be installed:
	- Markdown
	- Jinja2
	- Colorama
	- Pathlib
 
## Execution of Stateg:

Syntax with alias added to the user's shell. -> stateg [-h] [--ignore_files] [--update_index] target template_path

positional arguments:
  target          The target directory which contains the markdown file(s).
  template_path   Path of the HTML template to work with.

optional arguments:
  -h, --help      show this help message and exit
  --ignore_files  When it's True, Stateg will ask which files are to be ignored.
  --update_index  When it's True, Stateg will update the Hypertext References ('href') 
				  and names of the navigation bar in the 'index.html' file, using the 'index_template'.

The output directory of the html files are going to be created in the same parent directory of the 'target', as 'HTML'.
Syntax without alias added. -> python <path>/stateg.py stateg [-h] [--ignore_files] [--update_index] target template_path

## Add alias to bash or zsh shells.

1. Open with a text editor of choice ~/.zshrc (or in case of bash '~/.bashrc').
2. Look for a suitable space for the following line to be added.
3. Add "alias stateg='python <path of stateg dir>stateg.py'.
4. Once done save and close the file.
5. Make the alias available in your current session by run: "source ~/.zshrc (or ~/.bashrc)".

** The 'sources' and 'templates' directory contains some examples of .md and templates**
