import stateg_engine as stengine
from   pathlib import Path

"""
Syntax in the terminal:
'python stateg.py ../input/md/ ../input/templates/template.html --update_index --ignore_files'
"""

if __name__ == "__main__":
    
    # Get args
    target, template_path, ignore_files, update_index = stengine.get_args()

    # Get list of md files and filter them
    posix_list: list[Path] = list(target.glob('*.md')) 
    posix_list = stengine.filter_files(posix_list) if ignore_files else posix_list

    # Make output dir    
    output_dir: Path = stengine.mkdir_output(target)
    
    # Generate output paths
    output_file_paths = stengine.generate_output_paths(output_dir, posix_list)

    # Write html files and return a dict of categories and their path
    categories: dict[str,Path] = stengine.write_out_html(posix_list, output_file_paths, template_path)
    
    # Update the index
    if update_index: stengine.update_index_file(categories, template_path, output_dir)
