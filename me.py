import os
import glob

pe_dir = 'pe/'
me_dir = 'me/'

# pe-Ordner erstellen, wenn noch nicht vorhanden
if not os.path.exists(me_dir):
    os.mkdir(me_dir)

# Ordner leeren
files = os.listdir(me_dir)
for file in files:
    os.remove(os.path.join(me_dir, file))

files = os.listdir(pe_dir)
# jetzt mal ganz generisch alle Datei-Präfixe suchen (man könnte hier auch einfach a-e vorgeben)
file_prefixes = []
for file in files:
    prefix = file.split('.')[0]
    if prefix not in file_prefixes:
        file_prefixes.append(prefix)

# leeres Dictionary für einzelne Inhalte der Dateien mit Anzahl
me_contents = {}
for file_prefix in file_prefixes:
    me_file_name = os.path.join(me_dir, file_prefix) + '.me'
    # jetzt noch die jeweils zusammengehörigen (spricht mit dem selben Buchstaben beginnenden) Files suchen
    regex = '{}.*pe'.format(file_prefix)
    files_to_merge = glob.glob1(pe_dir, regex)
    me_contents.clear()
    with open(me_file_name, 'w') as me_file:
        print('Generating me-File: {}.me'.format(file_prefix))
        for file in files_to_merge:
            with open(os.path.join(pe_dir, file), 'r') as pe_file:
                for line in pe_file.readlines():
                    temp_line = line.rstrip()  # hier noch die Steuerzeichen entfernen, könnten sonst stören
                    # wenn die Zeile noch nicht im Dictionary ist, dann mit Wert 1 hinzufügen
                    if temp_line not in me_contents:
                        me_contents[temp_line] = 1
                    # wenn schon vorhanden, dann Anzahl um eins erhöhen
                    else:
                        me_contents[temp_line] = me_contents[temp_line] + 1

        # und noch alles aus dem Dictionary in die *.me-Datei schreiben
        for entry in sorted(me_contents):
            me_file.write('{}\t{}\n'.format(entry, me_contents[entry]))



