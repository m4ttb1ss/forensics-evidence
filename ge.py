import argparse
import os
from misc.libs import vbox_helper
import time
from misc.libs import helper
import sys
import shutil
import glob

# argparse parst den Pfad zum Ordner der init.raw gem. Aufgabenstellung
parser = argparse.ArgumentParser()
parser.add_argument("path", help="Pfad zum Abbild init.raw")
args = parser.parse_args()
path_to_init = os.path.normpath(str(args.path))

idiff_folder = os.path.normpath('idiff')

# aus der names.cfg die beiden Namen für die VMs auslesen
machine_name_win = helper.get_win_machine_name()
machine_name_linux = helper.get_linux_machine_name()

# sollte einer der beiden Werte nicht da sein, dann abbrechen, sollte mit dem Pfad zur init etwas nicht stimmen, auch
if not machine_name_win:
    sys.exit("Error: kein Name für die Windows-VM in names.cfg angegeben")
if not machine_name_linux:
    sys.exit("Error: kein Name für die Linux-VM in names.cfg angegeben")
if not os.path.exists(path_to_init):
    sys.exit("Error: Pfad {} zur init.raw existiert nicht".format(path_to_init))
if not os.path.exists(os.path.join(path_to_init, 'init.raw')):
    sys.exit("Error: init.raw existiert nicht an {}".format(path_to_init))
if not vbox_helper.machine_exits(machine_name_win):
    sys.exit('Maschine "{}" existiert nicht. Script wird abgebrochen.'.format(machine_name_win))
if not vbox_helper.machine_exits(machine_name_linux):
    sys.exit('Maschine "{}" existiert nicht. Script wird abgebrochen.'.format(machine_name_linux))

print('Path to init: {}'.format(path_to_init))

helper.set_config_value('path', 'path_to_shared_folder', path_to_init)

# idiff-Ordner erstellen
if not os.path.exists(idiff_folder):
    os.mkdir(idiff_folder)

# evtl. vorhandene Diffs aus dem Freigabeordner löschen
diffs_in_init_folder = glob.glob1(path_to_init, "*.diff")
for file in diffs_in_init_folder:
    os.remove(os.path.join(path_to_init, file))

# die Linux-VM vorbereiten
print('\nDie Linux-VM vorbereiten')
print('Shared Folder "{}" mit init.raw als "share" einhaengen......'.format(path_to_init))
if not vbox_helper.add_shared_folder(machine_name_linux, 'share', path_to_init):
    print('Shared Folder {} will not be mounted cause it already is or machine is not stopped or saved'.format('share'))
print('Linux-VM starten\n')
vbox_helper.start_vm(machine_name_linux)  # schonmal die Maschine starten, die brauchen wir ja dann

actions = ('a', 'b', 'c', 'd', 'e')
# jetzt alle Aktionen drei Mal ausführen
for action in actions:
    for i in range(1, 4):
        raw_name = '{}.{}.raw'.format(action, i)
        raw_absolute_path = os.path.join(path_to_init, raw_name)
        diff_name = '{}.{}.diff'.format(action, i)
        snapshot_name = '{}_{}'.format(action, i)
        print('Raw name: {}'.format(raw_name))
        print('Snapshot name: {}'.format(snapshot_name))
        print('Diff name: {}'.format(diff_name))

        # init-snapshot wiederherstellen
        print('Init-Snapshot wiederherstellen')
        vbox_helper.restore_init_snapshot(machine_name_win)

        print("Starte Durchgang {} für Aktion {}".format(i, action))
        print("Starte VM {}".format(machine_name_win))
        vbox_helper.start_vm(machine_name_win)

        vbox_helper.run_command(machine_name_win, 'C:/ST/{}.exe'.format(action), 'win7', 'win7')
        time.sleep(2)
        vbox_helper.run_command(machine_name_win, 'C:/ST/sync.exe', 'win7', 'win7')

        print("aktuellen Zustand speichern")
        vbox_helper.save_state(machine_name_win)
        time.sleep(10)

        print("Snapshot {} erstellen".format(snapshot_name))
        vbox_helper.take_snapshot(machine_name_win, snapshot_name)

        time.sleep(5)
        # wir klonen die HDD des letzten Snapshots, nicht des aktuellen Zustands, auch wenn der gleich sein dürfte
        hdd_id = vbox_helper.get_hdd_id(machine_name_win, True)
        print("HD klonen")
        vbox_helper.clone_medium(hdd_id, raw_absolute_path)

        print('Diff für {} in Bearbeitung'.format(diff_name))
        vbox_helper.run_idifference2(machine_name_linux, raw_name, diff_name)

        # die raw-Datei kann jetzt weg, Speicher ist manchmal kostbar
        os.remove(raw_absolute_path)

        if os.path.exists(os.path.join(idiff_folder, diff_name)):
            os.remove(os.path.join(idiff_folder, diff_name))
        print('{} nach idiff/ verschieben\n'.format(diff_name))
        shutil.move(os.path.join(path_to_init, diff_name), idiff_folder)

# jetzt erstellen wir noch die diffs für noise
print('\nnoise-diffs erstellen')
noise_files = glob.glob1(path_to_init, 'noise.*')
for noise_file in noise_files:
    diff_name = '{}.diff'.format(os.path.splitext(noise_file)[0])
    print('Diff für {} in Bearbeitung'.format(noise_file))
    vbox_helper.run_idifference2(machine_name_linux, noise_file, diff_name)
    print('{} nach idiff/ verschieben\n'.format(diff_name))

    # ... und verschieben diese auch in den diff-Ordner
    if os.path.exists(os.path.join(idiff_folder, diff_name)):
        os.remove(os.path.join(idiff_folder, diff_name))
    shutil.move(os.path.join(path_to_init, diff_name), idiff_folder)
    # die noise.raw kann jetzt auch gelöscht werden
    os.remove(os.path.join(path_to_init, noise_file))

# Linux-VM noch ausschalten
if vbox_helper.is_running(machine_name_linux):
    print('{} wird in savestate versetzt'.format(machine_name_linux))
    vbox_helper.save_state(machine_name_linux)

# Freigabe-Ordner wieder entfernen
print('Freigaben von {} entfernen'.format(machine_name_linux))
vbox_helper.remove_all_shared_folders(machine_name_linux)

# Und zurück in init
print('Init-Snapshot wiederherstellen')
vbox_helper.restore_init_snapshot(machine_name_win)

print("---------------- Fertig ---------------------")




