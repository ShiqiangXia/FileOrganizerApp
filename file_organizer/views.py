# -*- coding: utf-8 -*-
# file_organizer/views.py

"""This module provides the File organizer main window."""
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import humanize

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QFileDialog

from .ui.window import Ui_Window

RECENT_DAYS = 30
most_recent = datetime.now() - timedelta(days=RECENT_DAYS)

def create_dir(current_dir, name):
    path = current_dir.absolute().as_posix() + '/' + name
    p = Path(path)
    try:
        p.mkdir()
    except FileExistsError:
        print('Folder %s already exists!'%name)
    return(path)

class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()
        self._folder_path = None
        self._folder_dir = None

        self._file_list = []

        self._num_files = 0
        self._num_folders = 0
        self._folder_size = 0
        self._num_recent_files = 0

        self._move_dirs_path = []
        self._move_dirs_name = []
        self._action_list = []
        self._target_path = []

        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        self.setupUi(self)

    def _connectSignalsSlots(self):
        self.openBtn.clicked.connect(self.open_folder)
        self.startBtn.clicked.connect(self.start_organize_file)

    def open_folder(self):
        if self.dirEdit.text():
            initDir = self.dirEdit.text()
        else:
            initDir = str(Path.home())

        self._folder_path = QFileDialog.getExistingDirectory(
            self, "Select a folder", initDir)

        self.dirEdit.setText(self._folder_path)
        self._folder_dir = Path(self._folder_path)

        # get file list
        for entry in self._folder_dir.iterdir():
            if entry.is_file():
                self._num_files += 1
                self._file_list.append(entry)
                mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                if mtime > most_recent:
                    self._num_recent_files += 1
            else:
                self._num_folders += 1

        # get folder size
        for f in self._folder_dir.glob('**/*'):
            self._folder_size += f.stat().st_size
        natural_size = humanize.naturalsize(self._folder_size)

        self.infoText.setPlainText(
            f'{self._num_files} files, {self._num_folders} folders,\n'
            + f'size: {natural_size}')

    
    def start_organize_file(self):

        # create trash folder
        trash_path = create_dir(self._folder_dir, 'trash_bin')
        count = 1
        self.infoText.setPlainText(f'File {count}/{self._num_files}')

        while self._file_list:
            entry = self._file_list.pop()
            file_name = entry.name
            file_path = entry.absolute().as_posix()
            self.fileNameLabel.setText(file_name)



        
       
