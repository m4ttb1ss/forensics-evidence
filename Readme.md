Dieses Readme-File beschreibt den Aufbau der Dateien im Ordner sowie gibt Informationen zum Ausführen
der einzelnen Scriptdateien.

Folgende Konfiguration wurde verwendet:
Host: Windows 10 Pro, 64bit, AMD A10, 16GB RAM
Virtual Box 5.2.6 r120293
VM Windows 7: Guest Additions 5.2.6
Änderungen zur Ausgangs-OVA: PAE/NX aktiviert
VM Linux: Guest Additions unverändert
Änderungen zur Ausgangs-OVA: PAE/NX aktiviert

Ordnerstruktur:
- ce/
    - {a,b,c,d,e}.ce - Ergebnisse der CE-Phase
- idiff/
    - {a,b,c,d,e,noise}.{1|2|3}.diff - Ergebnisse der GE-Phase
- me/
    - {a,b,c,d,e,noise}.me - Ergebnisse der ME-Phase
- misc/
    - libs/
        - helper.py - Modul mit einigen allgemeinen Hilfsfunktionen
        - vbox_helper.py - Modul mit einigen Hilfsfunktionen zur Steuerung von Virtual Box
    - diff_d_e.csv - Ereignismenge von d ohne Ereignismenge von e bei der Ereignismethode
    - diff_e_cmd.csv - Ereignismenge von e ohne Ereignismenge der Ausführung von cmd.exe bei der Ereignismethode
    - diff_e_d.csv - Ereignismenge von e ohne Ereignismenge von d bei der Ereignismethode
    - md5_hashes.txt - MD5-Hashes aller .py-, .diff-, .pe-, .me- und .ce-Dateien in diesem Ordner
    - names.cfg - Config-Datei mit Namen der VM und Pfad zum Freigabe-Ordner
    - prepare.py - Modul zum Erzeugen der noise-Rawdateien
- pe/
    - {a,b,c,d,e,noise}.{1|2|3}.pe - Ergebnisse der PE-Phase
- Readme - dieses Readme-File

ACHTUNG: zur Vermeidung von evtl. auftretenden Fehlern sollten alle Scripte mit Admin-Rechten (unter Windows)
oder mit root-Rechten (unter Linux) ausgeführt werden; unter MacOS kann ich für nix garantieren ;-)
Folgende Schritte sind zu durchlaufen:
0. In die Datei misc/names.cfg in der Sektion [names] die Namen für die beiden VMs eintragen
- Windows-VM unter dem Schlüssel win_machine_name=
- Linux-VM unter dem Schlüssel linux_machine_name=
0.1 Pfad zu vboxmanage in die Path-Variable eintragen
1. misc/prepare.py mit dem Ausgabepfad für die noise.*.raw-Dateien als erstem Parameter ausführen,
mit dem Schalter -c kann die Anzahl der Durchläufe von 1-3
angegeben werden, Standard ist 3, Bsp.: prepare.py D:\VM_share -c 2
2. Die Windows-VM entweder in den gewünschten Ausgangssnapshot versetzen oder den Ausgangssnapshot
"Init" oder "init" nennen (dieser wird dann automatisch wiederhergestellt)
3. Linux-VM in gewünschten snapshot bringen (Snapshot-Name egal)
4. ge.py mit absolutem Pfad zur init.raw starten (egal ob mit oder ohne slash am Ende),
Beispiel: ge.py D:\VM_share
4.1. Nach gesamtem Durchlauf stehen die Ergebnisse im Ordner idiff (vorher existente werden gelöscht)
5. pe.py ausführen, pe-Ordner wird automatisch erstellt, evtl. alte Files werden gelöscht
5.1 Ergebnisse der PE-Phase landen im pe-Ordner
6. me.py ausführen, me-Ordner wird automatisch erstellt, evtl. alte Files werden gelöscht
6.1 Ergebnisse der ME-Phase landen im me-Ordner
7. ce.py ausführen, ce-Ordner wird automatisch erstellt, evtl. alte Files werden gelöscht
7.1 Ergebnisse der CE-Phase landen im ce-Ordner


