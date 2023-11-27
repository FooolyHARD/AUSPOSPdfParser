import argparse
import re
import subprocess
from pdftolatex.pdf import *

def convert(filepath):
    """Convert pdf at filepath to .tex file"""
    if not os.path.isdir('localstore'):
        os.mkdir('localstore')

    if os.path.isdir(filepath):
        for f in os.listdir(filepath):
            convert(f)
    
    filename = get_file_name(filepath)
    pdf = PDF(filepath)
    texfile = TexFile(pdf)
    texfile.generate_tex_file(filename+".tex")

def parseregex(s, num):
    regex = [r'\ [A-Z][A-Z][A-Z][A-Z]\ ', r'\d\d/\d\d/\d\d\d\d', r'\w+ \d+ \d+ \d+.\d+ \d+ \d+ \d+.\d+ \d+.\d+ \d+.\d+'] #\w+\s\d+\s\d+\s\d+.\d+\s\d+\s\d+\s\d+.\d+\s\d+.\d+\s\d+.\d+.\s?\d+
    matches = re.findall(regex[num], s)
    matches = [match for match in matches if match != " NONE "]
    print(matches)
    return matches

def clear(script):
    subprocess.call(['sh', './'+script])

def main():   
    parser = argparse.ArgumentParser(description="Generate a .tex file from a .pdf file.")
    parser.add_argument('--filepath', type=str, help="Path to pdf to be converted")
    parser.add_argument('--folderpath', type=str, help="Path to folder containing pdfs to be converted. All pdfs in the folder will be converted")
    
    args = parser.parse_args()

    filepath = args.filepath
    folderpath = args.folderpath

    if folderpath:
        convert(folderpath)
    else:
        convert(filepath)

    file = open('7513_1699368017513-99999999BB.tex', 'r');
    output = open('res.txt', 'w')
    string = file.readlines()
    print(string[77])
    stations = parseregex(string[77], 0)
    output.write('User Stations:')
    output.write(str(stations)+'\n')
    three_dot_one = parseregex(string[129], 1)
    output.write('3.1AA:')
    parsed_dates = []
    for i in range (0, len(stations)):
        parsed_dates.append(three_dot_one[i])
    output.write(str(parsed_dates)+'\n')
    three_dot_two = parseregex(string[141], 2)
    output.write('3.2AA:')
    parsed_coordinates = []
    for i in range (0, len(stations)):
        parsed_coordinates.append(three_dot_two[i])
    output.write(str(parsed_coordinates))
    file.close()

if __name__ == "__main__":
    main()