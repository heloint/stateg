import argparse

from colorama import Fore,Style
from pathlib import Path

import markdown
from markdown.core import Markdown

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Template

def get_args() -> tuple[Path, Path, bool, bool]:
  """Parses the arguments from the command line and returns them as 'Path'.
     Returns: - target:        The directory from where Stateg will get the markdown files.
              - template_path: The path of the template, what You'd like to fill.
              - ignore_files:  It's a boolean. If it's True Stateg will ask for further information about which files are
                               wanted to be ignored."""
  
  parser = argparse.ArgumentParser(prog = 'stateg', description = """Converts markdown files into HTML.
                                   The output directory (as "html") will created in the same parent directory of the 'target' path.""")

  parser.add_argument('target',        metavar='target',        type= str, help= 'The target directory which contains the markdown file(s).')
  parser.add_argument('template_path', metavar='template_path', type= str, help= 'Path of the HTML template to work with.')
  parser.add_argument('--ignore_files', action='store_true',               help= "When it's True, Stateg will ask which files are to be ignored.")
  parser.add_argument('--update_index', action='store_true',               help= """When it's True, Stateg will update the Hypertext References ('href') 
                                                                                    and names of the navigation bar in the 'index.html' file, using the 'index_template'.""")
  args = parser.parse_args()
  
  target:       Path = Path(args.target)
  template_path:Path = Path(args.template_path)
  ignore_files: bool = args.ignore_files
  update_index: bool = args.update_index
  
  return target, template_path, ignore_files, update_index



def mkdir_output(target: Path) -> Path:
  """Creates the output directory for the generated HTML files.
     Input:  -> Target path.
     Output: -> Made 'html' dir path."""
    
  output_dir: Path = Path(f"{'/'.join(str(target).split('/')[:-1])}/html")    
  output_dir.mkdir(exist_ok = True)
    
  return output_dir
 

def filter_files(posix_list: list[Path]) -> list[Path]:
  """ Input   ->  'posix_list', which is basically a list of paths of 
                  all the markdown files in the 'target' dir.
             
              ->  'user_input', later in the while loop of the function, 
                  Stateg will ask the user to choose those files which are to be ignored.
      Output: ->  'filtered_path', from the 'posix_list' removed all the user choosen paths.
  """  
  
  # Converts list[Path] -> dict[str,Path]
  posix_dict: dict[str,Path] = {str(x).split("/")[-1]:x for x in posix_list}
  
  # Displays the avaible options for the user.
  for key,value in posix_dict.items():
    if value.is_dir():
      print(f"{Fore.BLUE: AnsiFore }{key}{Style.RESET_ALL}")
    else:
      print(f"{Fore.GREEN}{key}{Style.RESET_ALL}")
  
  # Tries to get the file names to be ignored from the user.
  # If the input is invalid and 'KeyError' is raised,  then keeps the user in a loop.
  end:  bool = False  
  while end != True:
    try:
      user_input :         str = input("\nWrite the name of those files You want to ignore(separated with whitespace):\n")
      user_str_list: list[str] = user_input.split(" ")
      ignore_list:  list[Path] = [posix_dict[string] for string in user_str_list]
      end = True
    except KeyError:
      print("\nERROR: Invalid file/dir name!\n")

  # Filters out the initial posix_list.
  filtered_paths: list[Path] = [x for x in posix_list if x not in ignore_list]

  return filtered_paths
	
def fill_template(template_path: Path, content: dict) -> str:
    """ Reads the template and fills it with the contents.
        - template_path: A directory path relative to main_module_name.
        - template_filename: Template file to fill.
        - contents: Contents to put in the template.
        Keeping the template_path and filename separate allows template inheritance.
        Autoescapes by default.
        Returns the result as a string."""
    
    # Splits 'template_path' into directory and filename.
    template_dir:     Path = Path("/".join(str(template_path).split("/")[:-1]))
    template_filename: str = str(template_path).split("/")[-1]
    
    env:        Environment = Environment( loader=FileSystemLoader(template_dir), 
                                           autoescape=select_autoescape() )
    template:   Template    = env.get_template(template_filename)
    filled_str: str         = template.render(content)

    return filled_str 

def convert_md_to_html(markdown_string: str) -> str:
    """Input:  Markdown string
       Output: HTML string"""

    md:   Markdown = markdown.Markdown(extensions = ['meta']) 
    html: str      = md.convert(markdown_string)

    return html


# - 'type: ignore' needed since MyPy complains, but it is correct.
def strip_metadata(markdown_string: str) -> dict[str, str]:
    """Input:  Markdown string
       Output: Dict with all the metada. Keys and values are strings."""

    # Store metadata in md calling .convert()
    md: Markdown = markdown.Markdown(extensions = ['meta']) 
    _:  str      = md.convert(markdown_string)

    # Read metadata
    raw_metadata: dict[str, list[str]] = md.Meta #type: ignore

    # Convert all values from list[str] to str.
    joined_metadata: dict[str, str] = {key: ",".join(values) for key, values in raw_metadata.items()}
    
    return joined_metadata


def generate_output_paths(output_dir: Path, posix_list: list[Path]) -> list[Path]:
    """Changes the extensions of the file names and creates their new output path."""
    
    temp_dir_ls:        list[str] = [str(posix).split("/")[-1] for posix in posix_list]
    file_names:         list[str] = [str(x.replace(".md",".html")) for x in temp_dir_ls]
    output_file_paths: list[Path] = [Path(f"{output_dir}/{name}") for name in file_names]

    return output_file_paths

def write_out_html(posix_list: list[Path], output_file_paths: list[Path], template_path: Path) -> dict[str,Path]:
        """ Input:  -> 'posix_list'        : Markdown file paths.
                    -> 'output_file_paths' : Previously generated paths, to where Stateg saves the HTMLs.
                    -> 'template_path'     : The HTML template the user desires to use.
            Output: -> 'titles'            : A list[str] with the title names. Used later to update the nav.bar of index.html.
            Funcionality: - Reads all the markdown files.
                          - Separetes metadatas and content.
                          - Converts them into HTML.
                          - Joins them in a dictionary.
                          - Renders the template with the dictionary.
                          - Writes the output files."""
                          
        # Loop through markdown path list and read their content.
        md_strings:  list[str] = [md.read_text() for md in posix_list]
        categories: dict[str,Path] = {}
    
	    # Loop through markdown strings and convert 'em to html.
        for i in range(len(md_strings)):
          md:  str = md_strings[i]
          html_str = convert_md_to_html(md)
          meta_dict = strip_metadata(md)
          
          # Gets the titles from meta_dict and adds them to 'categories: list[str]'.
          # Stateg will use it later to update the navigation bar of 'index.html'.
          for key,value in meta_dict.items():
            if key == 'category' and 'category' in meta_dict:
              categories[value] = output_file_paths[i].resolve() 
                                                                 

          # Join html and meta into a dictionary.
          meta_dict['content'] = html_str
          filling = {'input':meta_dict}
          
          # Fill the templates and write them out.
          content = fill_template(template_path, filling)    
          (output_file_paths[i]).write_text(content)
        
        return categories    
        
def update_index_file(categories: dict[str, Path], template_path: Path,output_dir: Path) -> None:
    """Input:  - categories:    dict[str,Path] -> A dict with the 'category' and each file path from the metadatas of the Markdown files.
               - template_path: Path           -> The path of the used templeta for the session.
               - output_dir:    Path           -> The path to where Stateg will save the output HTML files.
       Output:  """
  
    index_update_content: dict[str,dict[str,Path]] = {'references' : categories}
    index_path: Path = Path(f"{'/'.join(str(template_path).split('/')[:-1])}/index_template.html")

    filling_refs = fill_template(index_path, index_update_content)
    (output_dir/"index.html").write_text(filling_refs)
