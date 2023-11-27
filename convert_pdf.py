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
    regex = [r'\s[A-Z0-9]{4}\s', r'\d\d/\d\d/\d\d\d\d', r'\w{4}\s+\d+\s+\d+\s+\d+\.\d+\s+\d+\s\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+'] #\w+\s\d+\s\d+\s\d+.\d+\s\d+\s\d+\s\d+.\d+\s\d+.\d+\s\d+.\d+.\s?\d+
    #1 - Stations, 2 - 3.1AA, 3 - 3.2AA
    substring_one = re.sub(r'[^A-Za-z0-9\s/\.\-]+', '', s)
    substring_two = re.sub(r'\s*\.\s*', '.', substring_one)
    substring_three = re.sub(r'O', '0', substring_two)
    #print(substring_two)
    matches = re.findall(regex[num], substring_three)
    matches = [match for match in matches if match != (" N0NE " or " NONE ")]
    #print(matches)
    return matches

def clear(script):
    subprocess.call(['sh', './'+script])

def AAProcess(filename):
    file = open(str(filename), 'r');
    output = open('res.txt', 'w')
    string = file.readlines()
    stations = parseregex(string[77], 0)
    output.write('User Stations:')
    output.write(str(stations) + '\n')
    three_dot_one = parseregex(string[129], 1)
    output.write('3.1AA:')
    parsed_dates = []
    for i in range(0, len(stations)):
        parsed_dates.append(three_dot_one[i])
    output.write(str(parsed_dates) + '\n')
    three_dot_two = parseregex(string[141], 2)
    output.write('3.2AA:')
    parsed_coordinates = []
    for i in range(0, len(stations)):
        parsed_coordinates.append(three_dot_two[i])
    output.write(str(parsed_coordinates))
    file.close()
def main():
    clear('remove_locals.sh')
    parser = argparse.ArgumentParser(description="Generate a .tex file from a .pdf file.")
    parser.add_argument('--filepath', type=str, help="Path to pdf to be converted")
    parser.add_argument('--folderpath', type=str, help="Path to folder containing pdfs to be converted. All pdfs in the folder will be converted")
    
    args = parser.parse_args()

    filepath = args.filepath
    folderpath = args.folderpath

    if folderpath:
        convert(folderpath)
    else:
        while True:
            print("Выберите вариант AA или BB:")
            choice = str(input())
            if choice == "AA":
                print("Выберите файл для обработки (путь относительно расположения convert_pdf.py):")
                filename = str(input())
                convert(filepath)
                AAProcess(filename+'.tex')
                break
            else:
                break


if __name__ == "__main__":
    main()