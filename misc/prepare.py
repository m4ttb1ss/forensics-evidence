import argparse
from libs import vbox_helper
import time
from libs import helper
import os
import sys

# Anzahl der gewünschten noise-Durchläufe über Schalter abfragen
parser = argparse.ArgumentParser()
parser.add_argument("path", help='Pfad, in das die Datei init.raw gelegt werden soll')
parser.add_argument("-c", "--count", help="Anzahl der Durchläufe, in denen Hintergrundrauschen erzeugt werden soll ("
                                          "Standard: 3)", type=int, dest='count', choices=[1, 2, 3])
args = parser.parse_args()
machine_name = helper.get_win_machine_name()
path_to_shared_folder = os.path.normpath(args.path)

if not os.path.exists(path_to_shared_folder):
    sys.exit("Error: Pfad {} existiert nicht".format(path_to_shared_folder))
if not machine_name:
    sys.exit("Error: kein Name für die Windows-VM in names.cfg angegeben")
if not vbox_helper.machine_exits(machine_name):
    sys.exit('Maschine "{}" existiert nicht. Script wird abgebrochen.'.format(machine_name))

if args.count:
    number_of_loops = args.count
else:
    number_of_loops = 3

# Anzahl Schleifen je nach Übergabeparameter
for i in range(1, number_of_loops+1):
    if number_of_loops == 1:
        raw_name = 'noise.raw'
        snapshot_name = "noise"
    else:
        raw_name = "noise.{}.raw".format(i)
        snapshot_name = "noise_{}".format(i)
    raw_full_path = os.path.join(path_to_shared_folder, raw_name)

    print("\n{}. Durchgang rauschen".format(i))
    if vbox_helper.snapshot_exists(machine_name, 'init') or vbox_helper.snapshot_exists(machine_name, 'Init'):
        print("Init-Snapshot wiederherstellen")
        vbox_helper.restore_init_snapshot(machine_name)

    print("Starte VM {}".format(machine_name))
    vbox_helper.start_vm(machine_name)
    print("5 Minuten warten")
    time.sleep(300)

    print("aktuellen Zustand speichern")
    vbox_helper.save_state(machine_name)
    time.sleep(10)

    print("Snapshot {} erstellen".format(snapshot_name))
    vbox_helper.take_snapshot(machine_name, snapshot_name)

    # wir klonen die HDD des letzten Snapshots, nicht des aktuellen Zustands, auch wenn der gleich sein dürfte
    hdd_id = vbox_helper.get_hdd_id(machine_name, True)
    print("HD klonen")
    vbox_helper.clone_medium(hdd_id, raw_full_path)

print("------------- Fertig -----------\n")

