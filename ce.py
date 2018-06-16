import os
import glob
from misc.libs import helper

# Pfade zu den notwendigen Dateien
ce_dir = 'ce/'
me_dir = 'me/'

# ce-Ordner erstellen, falls noch nicht vorhanden
if not os.path.exists(ce_dir):
    os.mkdir(ce_dir)

# Ordner leeren, um nicht irgendwo zufällig etwas anzuhängen
files = os.listdir(ce_dir)
for file in files:
    os.remove(os.path.join(ce_dir, file))

# dann alle me-Files aus dem me-Ordner holen
me_files = glob.glob1(me_dir, '*.me')

# jetzt die me-files nehmen und die Potenzmenge der anderen me-files abziehen
for me_file in me_files:
    # für noise brauchen wir kein CE-File
    if os.path.basename(me_file) == 'noise.me':
        continue

    # jetzt werfen wir aus der Liste der me-Files noch das raus, für das aktuell die CE berechnet werden
    files_to_compare = me_files.copy()
    files_to_compare.remove(me_file)

    # jetzt zwei sets für die zu vergleichenden Dateien anlegen und dann die Differenzmenge bilden
    set_me = set()
    with open(os.path.join(me_dir, me_file), 'r') as file:
        lines = file.readlines()
        for line in lines:
            line_elements = line.split('\t')
            if len(line_elements) > 2:  # wir brauchen die Anzahl aus dem me-file nicht, die steht an dritter Stelle
                # wenn die Spur nicht 3 mal vorkam, kann sie schon nicht charakteristisch sein
                # (kann man natürlich noch generisch machen)
                try:
                    if int(line_elements[2]) < 3:
                        continue
                except ValueError:  # da könnte ja auch zufällig mal Quatsch stehen
                    continue
                line = line_elements[0] + '\t' + line_elements[1]
            set_me.add(line.strip())

    for name in files_to_compare:
        set_compare = set()
        with open(os.path.join(me_dir, name), 'r') as file:
            lines = file.readlines()
            for line in lines:
                line_elements = line.split('\t')
                if len(line_elements) > 2:
                    line = line_elements[0] + '\t' + line_elements[1]
                set_compare.add(line.strip())
            set_me -= set_compare  # hier wird die Differenzmenge gebildet

     # und noch die CE in die Datei schreiben... Fertig
    ce_file_name = os.path.splitext(me_file)[0] + '.ce'
    print('Generating ce-file: ' + ce_file_name)
    with open(os.path.join(ce_dir, ce_file_name), 'w') as ce_file:
        for erg_line in sorted(set_me):
            ce_file.write(erg_line + '\n')


