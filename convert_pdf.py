import argparse
import os.path
import re
import subprocess
from termcolor import colored
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
    texfile.generate_tex_file(filename + ".tex")


def parseregex(s, num):
    regex = [r'\s[A-Z0-9]{4}\s', r'\d\d/\d\d/\d\d\d\d',
             r'\w{4}\s+\d+\s+\d+\s+\d+\.\d+\s+\d+\s\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+',
             r'\d{2}\/\d{2}\/\d{4}']  # \w+\s\d+\s\d+\s\d+.\d+\s\d+\s\d+\s\d+.\d+\s\d+.\d+\s\d+.\d+.\s?\d+
    # 1 - Stations, 2 - 3.1AA, 3 - 3.2AA, 4 - 3.1BB, 5 - 3.2BB
    substring_one = re.sub(r'[^A-Za-z0-9\s/\.\-]+', '', s)
    substring_two = re.sub(r'\s*\.\s*', '.', substring_one)
    substring_three = re.sub(r'O', '0', substring_two)
    # print(substring_two)
    matches = re.findall(regex[num], substring_three)
    matches = [match for match in matches if match != (" N0NE " or " NONE ")]
    # print(matches)
    return matches


def clear(script):
    subprocess.call(['sh', './' + script])


def AAProcess_forFile(filename, resname):
    if not os.path.isfile(resname + '.txt'):
        output = open(resname + '.txt', 'w')
    else:
        output = open(resname + '.txt', 'a')
    file = open(str(filename), 'r')
    string = file.readlines()
    for str_line in string:
        stations_line = "Station (s) Submitted File"
        if stations_line in str_line:
            stations_index = string.index(str_line)
            print("Индекс строки станций {0}".format(stations_index))
            break
    stations = parseregex(string[stations_index], 0)
    output.write(str(stations) + '\n')
    for str_line in string:
        three_dot_one_line = " 3.1 "
        if three_dot_one_line in str_line:
            three_dot_one_index = string.index(str_line)
            print(colored("Индекс строки 3.1 {0}".format(three_dot_one_index), 'yellow'))
    three_dot_one = parseregex(string[three_dot_one_index], 1)
    parsed_dates = []
    for i in range(0, len(stations)):
        parsed_dates.append(three_dot_one[i])
    for str_line in string:
        three_dot_two_line = "Station Latitude"
        if three_dot_two_line in str_line:
            three_dot_two_index = string.index(str_line)
            print(colored("Индекс строки 3.2 {0}".format(three_dot_two_index), 'blue'))
    three_dot_two = parseregex(string[three_dot_two_index], 2)
    parsed_coordinates = []
    for i in range(0, len(stations)):
        parsed_coordinates.append(three_dot_two[i])
    for i in range(0, len(stations)):
        output.write(str(parsed_dates[i]) + ' ' + str(parsed_coordinates[i]) + "\n")
    file.close()


def AAProcess_forFolder(folder, res_name):
    output = open(res_name + '.txt', 'a')
    directory = folder
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            print(f)
            convert(filename)
            filename = str(filename).replace('.pdf', '')
            AAProcess_forFile(filename + '.tex', res_name)
            output.write("123")


def BBProcess_forFile(filename, resname):
    if not os.path.isfile(resname + '.txt'):
        output = open(resname + '.txt', 'w')
    else:
        output = open(resname + '.txt', 'a')
    file = open(str(filename), 'r');
    string = file.readlines()
    three_dot_one = parseregex(string[129], 3)
    parsed_dates = three_dot_one
    three_dot_two = parseregex(string[141], 2)
    parsed_coordinates = three_dot_two
    for i in range(0, len(parsed_dates)):
        output.write(str(parsed_dates[i]) + ' ' + str(parsed_coordinates[i]) + "\n")
    file.close()


def BBProcess_forFolder(folder, res_name):
    output = open(res_name + '.txt', 'a')
    directory = folder
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            print(f)
            convert(filename)
            filename = str(filename).replace('.pdf', '')
            BBProcess_forFile(filename + '.tex', res_name)
            output.write("123")

def main():
    clear('remove_locals.sh')
    parser = argparse.ArgumentParser(description="Generate a .tex file from a .pdf file.")
    parser.add_argument('--filepath', type=str, help="Path to pdf to be converted")
    parser.add_argument('--folderpath', type=str,
                        help="Path to folder containing pdfs to be converted. All pdfs in the folder will be converted")

    args = parser.parse_args()

    filepath = args.filepath
    folderpath = args.folderpath
    if folderpath:
        while True:
            print("Выберите вариант AA или BB:")
            choice = str(input())
            if choice == "AA":
                AAProcess_forFolder(folderpath, "res_AA_folder")
                print(colored("Досвидания!", 'green'))
                break
            elif choice == "BB":
                BBProcess_forFolder(folderpath, "res_BB_folder")
                print(colored("Досвидания!", 'green'))
                break
            else:
                break
    else:
        while True:
            print("Выберите вариант AA или BB:")
            choice = str(input())
            if choice == "AA":
                filename = str(filepath).replace('.pdf', '')
                convert(filepath)
                AAProcess_forFile(filename + '.tex', 'kek1')
                print(colored("Досвидания!", 'green'))
                break
            if choice == "BB":
                filename = str(filepath).replace('.pdf', '')
                convert(filepath)
                BBProcess_forFile(filename + '.tex', 'kek2')
                print(colored("Досвидания!", 'green'))
                break
            else:
                break


if __name__ == "__main__":
    main()
