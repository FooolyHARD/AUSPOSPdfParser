import argparse
import os
import re

from termcolor import colored
from PyPDF2 import PdfReader


def convert_pdf_to_txt(filepath, page):
    converter = PdfReader(filepath)
    pages = converter.pages[page].extract_text()
    return pages

#AA convertation
def AA_file_extract(filepath, resfilename):
    if not os.path.isfile(resfilename + '.txt'):
        f = open(resfilename + '.txt', 'w')
    else:
        f = open(resfilename + '.txt', 'a')
    #extracting user stations
    raw_user_stations = []
    user_stations = []
    user_page = convert_pdf_to_txt(filepath, 1)
    user_page = user_page.partition("2 Processing Summary")[0].partition("AUSPOS")[0]
    parsed = parseregex(user_page, 0)
    for station in parsed:
        raw_user_stations.append(station)
    for station in raw_user_stations:
        if station != " NONE ":
            _station = station.replace("\n", "")
            user_stations.append(_station)
    print(user_stations)
    #extracting 3.1
    three_dot_one_dates = []
    three_dot_one_page_one = convert_pdf_to_txt(filepath, 2)
    three_dot_one_page_two = convert_pdf_to_txt(filepath, 3)
    three_dot_one_page = three_dot_one_page_one + three_dot_one_page_two
    three_dot_one_page = three_dot_one_page.partition("3.2 Geodetic")[0].partition("3.1 Cartesian")[2]
    parsed = parseregex(three_dot_one_page, 1)
    for i in range (len(user_stations)):
        three_dot_one_dates.append(parsed[i])
    print(three_dot_one_dates)
    #extracting 3.2
    three_dot_two_info = []
    three_dot_two_page_one = convert_pdf_to_txt(filepath, 2)
    three_dot_two_page_two = convert_pdf_to_txt(filepath, 4)
    three_dot_two_page = three_dot_two_page_one+three_dot_two_page_two
    parsed = parseregex(three_dot_two_page, 2)
    for i in range (len(user_stations)):
        three_dot_two_info.append(parsed[i])
    print(three_dot_two_info)
    for station in user_stations:
        f.write(station)
    f.write("\n")
    for i in range (len(user_stations)):
        f.write(three_dot_one_dates[i] + ' ' + three_dot_two_info[i] + "\n")

def AA_folder_exctract(folder, resfilename):
    f = open(resfilename + '.txt', 'w')
    directory = folder
    for filename in os.listdir(directory):
        print(filename)
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            AA_file_extract(folder+"/"+filename, resfilename)

def BB_file_extract(filepath, resfilename):
    if not os.path.isfile(resfilename + '.txt'):
        f = open(resfilename + '.txt', 'w')
    else:
        f = open(resfilename + '.txt', 'a')
    #extracting dates
    # extracting 3.1
    three_dot_one_dates = []
    three_dot_one_page_one = convert_pdf_to_txt(filepath, 2)
    three_dot_one_page_two = convert_pdf_to_txt(filepath, 3)
    three_dot_one_page = three_dot_one_page_one + three_dot_one_page_two
    three_dot_one_page = three_dot_one_page.partition("3.2 Geodetic")[0].partition("3.1 Cartesian")[2]
    parsed = parseregex(three_dot_one_page, 1)
    for i in range(len(parsed)):
        three_dot_one_dates.append(parsed[i])
    # extracting 3.2
    three_dot_two_info = []
    three_dot_two_page_one = convert_pdf_to_txt(filepath, 2)
    three_dot_two_page_two = convert_pdf_to_txt(filepath, 3)
    three_dot_two_page_three = convert_pdf_to_txt(filepath, 4)
    three_dot_two_page = three_dot_two_page_one + three_dot_two_page_two + three_dot_two_page_three
    parsed = parseregex(three_dot_two_page, 2)
    for i in range(len(parsed)):
        three_dot_two_info.append(parsed[i])
    for i in range(len(three_dot_two_info)):
        f.write(three_dot_one_dates[i] + ' ' + three_dot_two_info[i] + "\n")

def BB_folder_extract(folder, resfilename):
    f = open(resfilename + '.txt', 'w')
    directory = folder
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            BB_file_extract(folder + "/" + filename, resfilename)

def parseregex(s, num):
    regex = [r'\s[A-Z0-9]{4}\s', r'\d\d/\d\d/\d\d\d\d',
             r'\w{4}\s\-?\d*\s\-?\d*\s\-?\d*\.\d*\s\-?\d*\s\-?\d*\s\-?\d*\.\d*\s\-?\d*\.\d*\s\-?\d*\.\d*',
             r'\d{2}\/\d{2}\/\d{4}']  # \w+\s\d+\s\d+\s\d+.\d+\s\d+\s\d+\s\d+.\d+\s\d+.\d+\s\d+.\d+.\s?\d+
    # 1 - Stations, 2 - 3.1AA, 3 - 3.2AA, 4 - 3.1BB, 5 - 3.2BB
    substring_one = re.sub(r'[^A-Za-z0-9\s/\.\-]+', '', s)
    substring_two = re.sub(r'\s*\.\s*', '.', substring_one)
    # print(substring_two)
    matches = re.findall(regex[num], substring_two)
    matches = [match for match in matches if match != (" N0NE " or " NONE ")]
    # print(matches)
    return matches
def main():
    print(colored("Вы хотите обработать несколько файлов или один? (введите 1 (для одного файла) или 2 (для папки):", "green"))
    count = str(input())
    while (True):
        if count == "1":
            print(colored("Введите путь к файлу (относительный):", "green"))
            filepath = str(input())
            print(colored("Введите название файла, в который будут выгружены результаты (без разширения):"))
            resfilename = str(input())
            print(colored("Выберите вариант обработки (AA или BB):", "green"))
            option = str(input())
            if option == "AA":
                try:
                    AA_file_extract(filepath, resfilename)
                    print(colored("Goodbye!", "blue"))
                    break
                except Exception as e:
                    print(colored("Произошла непредвиденная ошибка", "red"))
                    print(e)
            elif option == "BB":
                try:
                    BB_file_extract(filepath, resfilename)
                    print(colored("Goodbye!", "blue"))
                    break
                except Exception as e:
                    print(colored("Произошла непредвиденная ошибка", "red"))
                    print(e)
        elif count == "2":
            print(colored("Введите путь к папке (относительный):", "green"))
            folderpath = str(input())
            print(colored("Введите название файла, в который будут выгружены результаты (без разширения):"))
            resfilename = str(input())
            print(colored("Выберите вариант обработки (AA или BB):", "green"))
            option = str(input())
            if option == "AA":
                try:
                    AA_folder_exctract(folderpath, resfilename)
                    print(colored("Goodbye!", "blue"))
                    break
                except Exception as e:
                    print(colored("Произошла непредвиденная ошибка", "red"))
                    print(e)
            elif option == "BB":
                try:
                    BB_folder_extract(folderpath, resfilename)
                    print(colored("Goodbye!", "blue"))
                    break
                except Exception as e:
                    print(colored("Произошла непредвиденная ошибка", "red"))
                    print(e)

if __name__ == "__main__":
    main()