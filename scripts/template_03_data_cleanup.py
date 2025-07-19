"""
cleanup.py
Skript zum Bereinigen temporärer Dateien.
Hier werden temporäre Dateien gelöscht.
"""

import os

def cleanup_temp_files():
    temp_dir = 'temp'
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print('Temporäre Dateien gelöscht.')
    else:
        print('Kein temporäres Verzeichnis gefunden.')

if __name__ == '__main__':
    cleanup_temp_files()
