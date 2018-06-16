import glob
import os
import re
from enum import Enum, auto


class DiffType(Enum):
    """
    Enumeration, die mögliche Sektionen des idiff-Files darstellt
    """
    NEW = auto()
    DELETED = auto()
    RENAMED = auto()
    MODIFIED = auto()
    CHANGED_PROPS = auto()


idiff_dir = 'idiff/'
pe_dir = 'pe/'
timestamps = {'a', 'm', 'c', 'cr'}

# pe-Ordner erstellen, wenn noch nicht vorhanden
if not os.path.exists(pe_dir):
    os.mkdir(pe_dir)

# Ordner leeren
files = os.listdir(pe_dir)
for file in files:
    os.remove('{}{}'.format(pe_dir, str(file)))

# im idiff-Ordner alle diff-files suchen (man weiß ja nie, was noch drinnen liegt)
diff_files = glob.glob1(idiff_dir, '*.diff')

# jetzt werden alle diff-Files durchlaufen, aus dem diff-Filename ergibt sich dann der pe-Filename
for file in diff_files:
    diff_file_name = os.path.join(idiff_dir, file)
    new_file_name = '{}.pe'.format(os.path.join(pe_dir, os.path.splitext(file)[0]))  # nur der Teil ohne Dateiendung
    section = -1
    print('Generating pe-File: {}.pe'.format(os.path.splitext(file)[0]))
    # und jetzt werden nach und nach die Sektionen ausgelesen und die timestamps gesetzt
    with open(new_file_name, 'w') as new_file:
        with open(diff_file_name, 'r') as diff_file:
            for line in diff_file.readlines():
                temp_line = line.rstrip()  # Steuerzeichen und whitespaces am Ende entfernen
                if temp_line:  # nur Zeilen betrachten, in denen auch etwas steht
                    # mit regex nach den Sektionen schauen
                    if re.match(r"^New files.*", temp_line):
                        section = DiffType.NEW
                        continue
                    elif re.match(r"^Deleted files.*", temp_line):
                        section = DiffType.DELETED
                        continue
                    elif re.match(r"^Renamed files.*", temp_line):
                        section = DiffType.RENAMED
                        continue
                    elif re.match(r"^Files with modified contents.*", temp_line):
                        section = DiffType.MODIFIED
                        continue
                    elif re.match(r"^Files with changed properties.*", temp_line):
                        section = DiffType.CHANGED_PROPS
                        continue
                    # die Trennlinie einfach übespringen
                    elif re.match(r"^={5,}.*", temp_line):
                        continue

                    # new files, alle Zeitstempel erzeugen, an Tab.-Positionen 2 steht der Dateiname
                    if section == DiffType.NEW:
                        entry = temp_line.split('\t')
                        for t in timestamps:
                            new_file.write('{}\t{}\n'.format(entry[1], t))
                    # deleted files, Zeitstempel 'd' erzeugen, an Tab.-Positionen 2 steht der Dateiname
                    elif section == DiffType.DELETED:
                        entry = temp_line.split('\t')
                        new_file.write('{}\t{}\n'.format(entry[1], 'd'))
                    # Renamed files und Files with modified content, beide Sektionen gleich aufgebaut
                    elif section == DiffType.RENAMED or section == DiffType.MODIFIED:
                        # Einträge durch Tabs getrennt, wenn timestamp, dann 2. Position, wieder mit regex suchen
                        # und danach den Filenamen und den timestamp mit \t getrennt in das neue File schreiben
                        entry = temp_line.split('\t')
                        if re.match(r"^mtime.*", entry[1]):
                            new_file.write('{}\t{}\n'.format(entry[0], 'm'))
                        elif re.match(r"^atime.*", entry[1]):
                            new_file.write('{}\t{}\n'.format(entry[0], 'a'))
                        elif re.match(r"^ctime.*", entry[1]):
                            new_file.write('{}\t{}\n'.format(entry[0], 'c'))
                        elif re.match(r"^crtime.*", entry[1]):
                            new_file.write('{}\t{}\n'.format(entry[0], 'cr'))
                        else:
                            continue
                    else:
                        continue
                else:
                    continue








