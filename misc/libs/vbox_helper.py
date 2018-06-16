"""
This module provides some helping functions for VBox-Control
"""

import subprocess
import sys
import os


def machine_exits(machine_name):
    """
    Returns true, if machine exists, otherwise exits the script.
    :param machine_name: Machine, that should be found
    :return: True, if Machine with machine_name exists
    """
    try:
        completed_process = subprocess.run(["VBoxManage", "showvminfo", machine_name],
                                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        completed_process.check_returncode()
        return True

    except subprocess.CalledProcessError:
        return False


def get_hdd_id(machine_name, last_snapshot=False, snapshot_name='current_state'):
    """
    Returns the hdd uuid of the given machine name and whether the last_snapshot, current_state
    or the given snapshot name
    :param machine_name: machine name of which the UUID is asked
    :param last_snapshot: if True, the UUID of the last snapshot is returned, if False the one from snapchot name
    :param snapshot_name: name of the snapshot, that HDD UUD is asked (not used if last_snapshot is True)
    :return: name of the searched HDD UUID regarding to last_snapshot and snapshot_name
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    # bei last_snapshot holen wir uns den aktuellen Snapshot-Namen
    if last_snapshot:
        snapshot_name = get_current_snapshot_name(machine_name)
    # wird kein snapshot_name angegeben, so nehmen wir die UUID des aktuellen Zustands
    if snapshot_name == 'current_state':
        completed_process = subprocess.run(["VBoxManage", "showvminfo", "--machinereadable", machine_name],
                                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            completed_process.check_returncode()
        except subprocess.CalledProcessError as err:
            print('Fehler beim Ermitteln der aktuellen HDD-ID von {}. Script wird fortgeführt.'.format(machine_name))
            return None
        vm_info = completed_process.stdout

        for line in (str(vm_info)).replace('"', '').splitlines():
            try:
                key, value = line.split('=')
            except ValueError:
                continue
            if key == 'SATA-ImageUUID-0-0':
                return value
        return None
    # wenn ein snapshot-Name angegeben ist, dann die HDD UUID dieses snapshots holen
    else:
        completed_process = subprocess.run(["VBoxManage", "snapshot", machine_name, "showvminfo", snapshot_name],
                                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            completed_process.check_returncode()
        except subprocess.CalledProcessError as err:
            print('Fehler beim Ermitteln der HDD-ID von {} im Snapshot {}. '
                  'Script wird fortgeführt.'.format(machine_name, snapshot_name))
            return None
        vm_info = completed_process.stdout

        for line in (str(vm_info)).splitlines():
            values = line.split(':', 1)
            if 'SATA (0, 0)' in values[0]:
                uuid = values[1].rsplit(':', 1)
                return uuid[1].lstrip().replace(')', '')
        return None


def start_vm(machine_name):
    """
    Starts the VM with the given name
    :param machine_name: Machine name to start
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    if not is_running(machine_name):
        try:
            subprocess.run(["VBoxManage", "startvm", machine_name], universal_newlines=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
        except subprocess.CalledProcessError as err:
            sys.exit('VM {} kann nicht gestartet werden. Vorgang wird abgebrochen. Evtl. fehlen Administrator-Rechte.'
                     'Script wird beendet.\n\nVBoxError:\n{}'.format(machine_name, err.stderr))


def save_state(machine_name):
    """
    Puts VM into savestate
    :param machine_name: Name of the machine
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    try:
        subprocess.run(["VBoxManage", "controlvm", machine_name, "savestate"],
                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
    except subprocess.CalledProcessError as err:
        sys.exit('Fehler beim Speichern (savestate)von {}. Script wird beendet.\n\n'
                 'VBoxError:\n{}'.format(machine_name, err.stderr))


def poweroff(machine_name):
    """
    Powers off machine with given name
    :param machine_name: Machine name of the machine to poweroff
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    try:
        subprocess.run(["VBoxManage", "controlvm", machine_name, "poweroff"],
                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
    except subprocess.CalledProcessError as err:
        sys.exit('Fehler beim Ausschalten von {}. Script wird beendet.\n\n'
                 'VBoxError:\n{}'.format(machine_name, err.stderr))


def take_snapshot(machine_name, snapshot_name):
    """
    Takes snapshot of given machhine name with given name for the snapshot
    :param machine_name: Machine, that will be snapshotted
    :param snapshot_name: Name of the snapshot
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    if snapshot_exists(machine_name, snapshot_name):
        delete_snapshot(machine_name, snapshot_name)
    try:
        subprocess.run(["VBoxManage", "snapshot", machine_name, "take", snapshot_name],
                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
    except subprocess.CalledProcessError as err:
        sys.exit('Fehler beim Erstellen des Snapshots {} auf {}. Script wird beendet.\n\n'
                 'VBoxError:\n{}'.format(snapshot_name, machine_name, err.stderr))


def restore_snapshot(machine_name, snapshot_name):
    """
    restore machine with machine_name to given snapshot
    :param machine_name: Machine to restore to given snapshot name
    :param snapshot_name: Snapshot to restore
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    if snapshot_exists(machine_name, snapshot_name):
        try:
            subprocess.run(["VBoxManage", "snapshot", machine_name, "restore", snapshot_name],
                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
        except subprocess.CalledProcessError as err:
            sys.exit('Fehler beim Wiederherstellen des Snapshots {} auf {}. Script wird beendet.\n\n'
                     'VBoxError:\n{}'.format(snapshot_name, machine_name, err.stderr))


def clone_medium(hdd_id, outfile_name, file_format="RAW"):
    """
    Clones given HDD into the given output file with given format
    :param hdd_id: UUID of the HDD to clone
    :param outfile_name: name of the outfile
    :param file_format: optional, RAW is standard
    :return: None
    """
    if not os.path.exists(os.path.dirname(outfile_name)):
        os.makedirs(os.path.dirname(outfile_name))
    try:
        subprocess.run(["VBoxManage", "clonemedium", hdd_id, "--format", file_format, outfile_name],
                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
    except subprocess.CalledProcessError:
        sys.exit('Fehler beim klonen der HDD mit "{}".\n\nScript wird beendet.'.format(hdd_id))


def get_current_snapshot_name(machine_name):
    """
    Returns the current snapshot name of the given machine
    :param machine_name: Machine that current snapshot is asked for
    :return: Name of the current snapshot or None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    completed_process = subprocess.run(["VBoxManage", "showvminfo", "--machinereadable", machine_name],
                                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        completed_process.check_returncode()
    except subprocess.CalledProcessError:
        print('Fehler bei Suche nach aktuellem Snapshot auf {}. Script wird fortgesetzt.'.format(machine_name))
        return None
    vm_info = completed_process.stdout

    for line in (str(vm_info)).replace('"', '').splitlines():
        try:
            key, value = line.split('=')
        except ValueError:
            continue
        if key == 'CurrentSnapshotName':
            return value
    return None


def snapshot_exists(machine_name, snapshot_name):
    """
    Returns True, if the snapshot_name is a snapshot of the given machine name
    :param machine_name: Machine to search snapshot name
    :param snapshot_name: Snapshot name that is searched
    :return: True if snapshot exists at Machine, False otherwise
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    completed_process = subprocess.run(["VBoxManage", "snapshot", machine_name, "list", "--machinereadable"],
                                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        completed_process.check_returncode()
    except subprocess.CalledProcessError:
        print('Fehler bei Suche nach Snapshot {} auf {}. Script wird fortgesetzt.'.format(snapshot_name, machine_name))
        return False

    vm_info = completed_process.stdout

    for line in (str(vm_info)).replace('"', '').splitlines():
        try:
            key, value = line.split('=')
        except ValueError:
            continue
        if value == snapshot_name:
            return True
    return False


def delete_snapshot(machine_name, snapshot_name):
    """
    Deletes the snapshot 'snapshot_name' if existing
    :param machine_name: Machine name thats snapshot will be deleted
    :param snapshot_name: Snapshot that will be deleted
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    if snapshot_exists(machine_name, snapshot_name):
        try:
            subprocess.run(["VBoxManage", "snapshot", machine_name, "delete", snapshot_name],
                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
        except subprocess.CalledProcessError:
            print('Fehler beim Löschen des Snapshots {} von {}. Script wird fortgesetzt.'.format(snapshot_name,
                                                                                                 machine_name))


def run_command(machine_name, path, username, password):
    """
    RUns the given command via VBoxManage guestcontrol run in given machine name
    :param machine_name: Machine, in that the command should be run
    :param path: absolute path to the executable on the guest system
    :param username: name of the user, that must exist on the system
    :param password: password of the user username
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    if is_running(machine_name):
        try:
            subprocess.run(["VBoxManage", "guestcontrol", machine_name, "run", "--username", username, "--password",
                            password, "--exe", path, "--wait-stdout", "--wait-stderr"],
                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
        except subprocess.CalledProcessError:
            print('Fehler beim Ausführen von {} auf {}. Script wird fortgeführt.'.format(path, machine_name))
            return None


def restore_init_snapshot(machine_name):
    """
    Restores given machine to snapshot 'init', if exists
    :param machine_name: Machine to restore to init
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    state = get_state(machine_name)
    if state == 'poweroff' or state == 'saved':
        if snapshot_exists(machine_name, 'init'):
            restore_snapshot(machine_name, 'init')
        elif snapshot_exists(machine_name, 'Init'):
            restore_snapshot(machine_name, 'Init')


def add_shared_folder(machine_name, share_name, path):
    """
    Adds a shared folder with share_name at path to the machine machine_name with automount
    :param machine_name: Machine name to add a shared folder to
    :param share_name: Name of the share
    :param path: Path to hosts folder to be the shared folder
    :return: True if folder was added, None otherwise
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    for folder in get_shared_folders(machine_name):
        if str(folder) == share_name:
            return None
    state = get_state(machine_name)
    if state == 'poweroff' or state == 'saved':
        try:
            subprocess.run(['VBoxManage', 'sharedfolder', 'add', machine_name, '--name', share_name, '--hostpath', path,
                            '--automount'], universal_newlines=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).check_returncode()
            return True
        except subprocess.CalledProcessError:
            print('Fehler beim Hinzufügen des Shared Folders {}({}). Script wird fortgeführt'.format(share_name, path))
            return None
    return None


def remove_shared_folder(machine_name, share_name):
    """
    Removes the shared folder with given name from given machine
    :param machine_name: Machine, of which the shared folder will be removed
    :param share_name: Share name to remove from machine
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    state = get_state(machine_name)
    if state == 'poweroff' or state == 'saved':
        try:
            subprocess.run(['VBoxManage', 'sharedfolder', 'remove', machine_name, '--name', share_name],
                           universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
        except subprocess.CalledProcessError as err:
            print('Shared Folder konnte nicht entfernt werden. Script wird fortgeführt.\n\n'
                  'VBoxError:\n{}'.format(err.stderr))
            return None


def remove_all_shared_folders(machine_name):
    """
    Removes all shared folders from machine with given name
    :param machine_name: Name of the machine to remove all shared folders from
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    state = get_state(machine_name)
    if state == 'poweroff' or state == 'saved':
        for folder in get_shared_folders(machine_name):
            remove_shared_folder(machine_name, folder)


def run_idifference2(machine_name, raw_name, diff_name):
    """
    Runs idifference2.py in Linux VM machine_name to comare init.raw and raw_name and write the result to diff_name
    :param machine_name: Name of the Linux Machine where idifference2.py is runable
    :param raw_name: Name of the raw-file that will be compared to init.raw
    :param diff_name: Name of the *.diff-file that will get the results
    :return: None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    try:
        subprocess.run(
            ["VBoxManage", "guestcontrol", machine_name, "run", "--username", "fiwalk", "--password", "fiwalk",
             "--exe", "/bin/sh", "--wait-stdout", "--wait-stderr", "--putenv",
             "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games",
             "--verbose", "--unquoted-args", "--", "sh/arg0", "-c",
             "/usr/bin/python3.4 /home/fiwalk/dfxml-master/python/idifference2.py /media/sf_share/init.raw \
             /media/sf_share/" + raw_name + "> /media/sf_share/" + diff_name],
            universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).check_returncode()
    except subprocess.CalledProcessError as err:
        print('Idifference2 mit Fehler abgebrochen. Script wird fortgeführt.\n\nVBoxError:\n'
              '{}'.format(err.stderr))
        return None


def get_state(machine_name):
    """
    Returns the state of the machine with given name
    :param machine_name: Name of the machine thats state is asked
    :return: state of the given name or None
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    completed_process = subprocess.run(["VBoxManage", "showvminfo", machine_name, "--machinereadable"],
                                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        completed_process.check_returncode()
    except subprocess.CalledProcessError:
        return None

    vm_info = completed_process.stdout

    for line in (str(vm_info)).replace('"', '').splitlines():
        try:
            key, value = line.split('=')
        except ValueError:
            continue
        if key == 'VMState':
            return value
    return None


def is_running(machine_name):
    """
    returns True if machine is in running-state
    :param machine_name: Name of the machine
    :return: Ture if machine is in running state, False otherwise
    """
    return get_state(machine_name) == 'running'


def get_shared_folders(machine_name):
    """
    Returns a list of all mounted shared folders
    :param machine_name: Name of the machine, whos shared folders are searched
    :return: List of shared folders or empty list
    """
    if not machine_exits(machine_name):
        sys.exit('Die Maschine "{}" existiert nicht! Script wird beendet!'.format(machine_name))
    completed_process = subprocess.run(["VBoxManage", "showvminfo", "--machinereadable", machine_name],
                                       universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    shared_folders = []
    try:
        completed_process.check_returncode()
    except subprocess.CalledProcessError:
        return shared_folders

    vm_info = completed_process.stdout

    for line in (str(vm_info)).replace('"', '').splitlines():
        try:
            key, value = line.split('=')
            if 'SharedFolderName' in key:
                shared_folders.append(value)
        except ValueError:
            continue
    return shared_folders
