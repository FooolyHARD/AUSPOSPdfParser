import argparse
import os.path
import re
import subprocess
from io import BytesIO
from config import token
from termcolor import colored
from pdftolatex.pdf import *
import telebot
from time import time

bot = telebot.TeleBot(token)

user_data = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне PDF файл, и я верну текстовый документ.")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id,
                     "Вот список доступных команд: /send - отправить боту один файл \n/send_alot - отправить боту несколько файлов")


@bot.message_handler(commands=["send"])
def handle_send(message):
    # Добавление пользователя в словарь данных
    user_data[message.chat.id] = {'option': '', 'num_files': 1}
    # Отправка диалогового окна с вариантами обработки
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('AA', 'BB')
    bot.send_message(message.chat.id, "Выберите вариант обработки:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['AA', 'BB'] and message.chat.id in user_data)
def handle_option(message):
    # Сохранение выбранного варианта обработки
    user_data[message.chat.id]['option'] = message.text

    # Отправка диалогового окна с вопросом о количестве файлов
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Введите количество файлов:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.chat.id in user_data and message.text.isdigit())
def handle_num_files(message):
    try:
        # Попытка получить количество файлов из сообщения
        num_files = int(message.text)

        # Сохранение количества файлов в данных пользователя
        user_data[message.chat.id]['num_files'] = num_files

        # Отправка подтверждения
        bot.send_message(message.chat.id, f"Будет обработано {num_files} файлов. Отправьте мне PDF файл(ы).")

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное количество файлов (целое число).")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        clear('remove_locals.sh')
        user_data[message.chat.id]['num_files'] -= 1
        # Получаем информацию о файле
        file_info = bot.get_file(message.document.file_id)
        file_path = file_info.file_path

        # Загружаем файл в байтовом формате
        file_data = bot.download_file(file_path)

        option = user_data[message.chat.id]['option']
        num_files = user_data[message.chat.id]['num_files']

        # Сохраняем файл в локальный каталог
        bot.send_message(message.chat.id, "Ожидайте...")
        pdf_path = 'temp.pdf'
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(file_data)
        # Конвертируем PDF в текст
        parse_files(pdf_path, option, 1)
        os.remove(pdf_path)

        print(num_files)
        if num_files > 0:
            bot.send_message(message.chat.id, "Следующий")
        else:
            f = open('tmp.txt')
            bot.send_document(message.chat.id, f)
            # Отправляем текстовый результат пользователю
            bot.send_message(message.chat.id, "Готово!")
            os.remove('tmp.txt')

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


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
    subprocess.call(['bash', './' + script])


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


def BBProcess_forFile(filename, resname):
    if not os.path.isfile(resname + '.txt'):
        output = open(resname + '.txt', 'w')
    else:
        output = open(resname + '.txt', 'a')
    file = open(str(filename), 'r');
    string = file.readlines()
    for str_line in string:
        three_dot_one_line = ' 3.1 '
        if three_dot_one_line in str_line:
            three_dot_one_index = string.index(str_line)
            print(colored("Индекс строки 3.1 {0}".format(three_dot_one_index), 'green'))
            break
    three_dot_one = parseregex(string[three_dot_one_index], 3)
    parsed_dates = three_dot_one
    for str_line in string:
        three_dot_two_line = 'Station Latitude'
        if three_dot_two_line in str_line:
            three_dot_two_index = string.index(str_line)
            print(colored("Индекс строки 3.2 {0}".format(three_dot_two_index), 'blue'))
            break
    three_dot_two = parseregex(string[three_dot_two_index], 2)
    parsed_coordinates = three_dot_two
    print(len(parsed_dates))
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


def parse(dir_or_file, variant):
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
                AAProcess_forFile(filename + '.tex', 'AA_res_for_files')
                print(colored("Досвидания!", 'green'))
                break
            if choice == "BB":
                filename = str(filepath).replace('.pdf', '')
                convert(filepath)
                BBProcess_forFile(filename + '.tex', 'BB_res_for_files')
                print(colored("Досвидания!", 'green'))
                break
            else:
                break


def return_from_file(filepath):
    file = open(filepath)
    lines = []
    for line in file:
        print(line)
        lines.append(line)
    return lines


def parse_one(filepath):
    clear('remove_locals.sh')
    filename = str(filepath).replace('.pdf', '')
    convert(filepath)
    AAProcess_forFile(filename + '.tex', 'tmp')
    print(colored("Досвидания!", 'green'))
    return return_from_file("tmp.txt")


def parse_files(filepath, option, num_files):
    clear('remove_locals.sh')
    for i in range(num_files):
        filename = str(filepath).replace('.pdf', '')
        convert(filepath)
        if option == "AA":
            AAProcess_forFile(filename + '.tex', 'tmp')
            print(colored("Досвитания!", 'green'))
        if option == "BB":
            BBProcess_forFile(filename + '.tex', 'tmp')
            print(colored('Доствидания!', 'green'))


while (True):
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(3)
        print(e)
