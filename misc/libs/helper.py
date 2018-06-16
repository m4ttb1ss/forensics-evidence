import os
import difflib
import configparser


def get_win_machine_name():
    """
    Checks for misc/names.cfg and returns the value of win_machine_name if existing
    :return: value of win_machine_name in names.cfg
    """
    if os.path.exists('misc/names.cfg'):
        config_path = 'misc/names.cfg'
    elif os.path.exists('names.cfg'):
        config_path = 'names.cfg'
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.get('names', 'win_machine_name', fallback='win7-x86')


def get_linux_machine_name():
    """
    Checks for misc/names.cfg and returns the value of linux_machine_name if existing
    :return: Value of linux_machine_name in names.cfg
    """
    if os.path.exists('misc/names.cfg'):
        config_path = 'misc/names.cfg'
    elif os.path.exists('names.cfg'):
        config_path = 'names.cfg'
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.get('names', 'linux_machine_name', fallback='ST_fiwalk')


def get_path_to_shared_folder():
    """
    Checks for misc/names.cfg and returns the value of path_to_shared_folder if existing
    :return: Path to shared folder of names.cfg
    """
    if os.path.exists('misc/names.cfg'):
        config_path = 'misc/names.cfg'
    elif os.path.exists('names.cfg'):
        config_path = 'names.cfg'
    config = configparser.ConfigParser()
    config.read(config_path)
    path_to_shared_folder = config.get('path', 'path_to_shared_folder', fallback='')

    # if not path_to_shared_folder[-1] == '/':
      # path_to_shared_folder += '/'
    return path_to_shared_folder


def set_config_value(section, key, value):
    config = configparser.ConfigParser()
    config.read('misc/names.cfg')
    if not config.has_section(section):
        config.add_section(section)
    config[section][key] = value
    with open('misc/names.cfg', 'w') as config_file:
        config.write(config_file)


def get_config_value(section, key):
    config = configparser.ConfigParser()
    config.read('misc/names.cfg')
    if config.has_section(section):
        if config.has_option(key):
            return config.get(section, key)
    return None


def compare_two_files(file1, file2, separator=None, columns=1):
    """
    Compares to files with number of given columns seperated by seperator
    and returns the unique lines of file 1
    :param file1: File thats unique lines are searched
    :param file2: File thats lines will be compared to File 1
    :param separator: Character that separates columns in both files
    :param columns: Number of columns if not the whole line should be in comparison
    :return: List of unique lines in File 1
    """
    list1 = []
    list2 = []
    with open(file1, 'r') as f1:
        lines = f1.readlines()
        if not separator:
            list1 = lines
        else:
            # jetzt wird die Zeile auf die gewünschte Anzahl an Spalten gekürzt
            for line in lines:
                line_members = line.split(separator)
                cut_line = str(line_members[0]).strip()
                for i in range(1, columns):
                    cut_line = cut_line + '\t' + str(line_members[i]).strip()
                    list1.append(cut_line)
    with open(file2, 'r') as f2:
        lines = f2.readlines()
        if not separator:
            list2 = lines
        else:
            for line in lines:
                line_members = line.split(separator)
                cut_line = str(line_members[0])
                for i in range(1, columns):
                    cut_line = cut_line + '\t' + str(line_members[i])
                    list2.append(cut_line)
    # Vergleichsfunktion aus difflib
    diff = difflib.Differ()
    result = list(diff.compare(list1, list2))

    return_list = []
    for entry in result:
        # - am Beginn der Zeile bedeutet, dass dieser Eintrag nur in list1 vorkommt, genau die wollen wir hier haben
        if entry[0] == '-':
            return_list.append(entry[2:])
    return return_list

