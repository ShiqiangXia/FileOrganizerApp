# -*- coding: utf-8 -*-
# file_organizer/views.py

"""This module provides the File organizer main window."""
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from send2trash import send2trash
import shutil
import humanize

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QInputDialog

from .ui.window import Ui_Window

RECENT_DAYS = 30
most_recent = datetime.now() - timedelta(days=RECENT_DAYS)



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
        self._file_id = 0

        self._trash_path = None
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
        self.skipBtn.clicked.connect(self.skip_file)
        self.deleteBtn.clicked.connect(self.delete_file)
        self.undoBtn.clicked.connect(self.undo_file)
        self.doneBtn.clicked.connect(self.done_organize)
        self.moveFolderList.itemDoubleClicked.connect(
            self.move_to_selected_folder)

    def create_dir(self, current_dir, name):
        path = current_dir.absolute().as_posix() + '/' + name
        p = Path(path)
        try:
            p.mkdir()
        except FileExistsError:
            print('Folder %s already exists!'%name)
        return(path)

    def print_file_info(self):

        entry = self._file_list[self._file_id]
        file_name = entry.name
        count = self._file_id + 1
        file_size = humanize.naturalsize(entry.stat().st_size)
        self.infoText.setPlainText(
            f'Start organizing....\nFile {count}/{self._num_files},'
            + f' Size: {file_size}')
        self.fileNameLabel.setText(file_name)
        # set file picture
        # TO DO

    def move_file(self, file_path, target_path):
        temp_path = shutil.move(file_path, target_path)
        self._target_path.append(temp_path)

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

        # create trash bin folder
        self._trash_path = self.create_dir(self._folder_dir, 'trash_bin')
        # print the file info
        self.print_file_info()
        
        # set status to 'organizing'

    def skip_file(self):
        if self._file_id < self._num_files:
            entry = self._file_list[self._file_id]
            self._file_id += 1

            file_path = entry.absolute().as_posix()
            self._target_path.append(file_path)
            self._action_list.append('skip')

            self.print_file_info()
        
    
    def delete_file(self):
        if self._file_id < self._num_files:
            entry = self._file_list[self._file_id]
            self._file_id += 1

            file_path = entry.absolute().as_posix()
            self.move_file(file_path, self._trash_path)
            self._action_list.append('delete')

            self.print_file_info()
  
    def undo_file(self):
        # check if undo is possible
        if self._action_list:
            # undo the last action
            action = self._action_list.pop()
            temp_path = self._target_path.pop()
            self._file_id -= 1
            print('undo: ' + action)
            print('temp_path: ' + temp_path)
            if (action == 'delete') or (action == 'move'):
                shutil.move(temp_path, self._folder_dir)
        else:
            QMessageBox.warning(self, 'Warning', 'No more undo action!')

        self.print_file_info()
       
    def done_organize(self):
        # move trash_bin to real trash folder
        send2trash(self._trash_path)
        # trash_dir = Path(self._trash_path)
        # # for f in trash_dir.iterdir():
        # #     send2trash(f.absolute().as_posix())
        # trash_dir.rmdir()

        # set status to 'done'
    
    def move_to_selected_folder(self, item):
        print(item.text())

        if item.text() == '+ Add folder':
            # add folder to move list
            # get folder name
            folder_name, ok  = QInputDialog.getText(
                self, 'Input folder name', 'Folder name:')
            if ok:
                entry = self._file_list[self._file_id]
                self._file_id += 1
                file_path = entry.absolute().as_posix()
                # create folder
                folder_path = self.create_dir(self._folder_dir, folder_name)
                # move file to folder
                self.move_file(file_path, folder_path)
                self._action_list.append('move')
                # add folder to moveFolder List
                self.moveFolderList.addItem(folder_name)
        else:
            # move file to selected folder
            entry = self._file_list[self._file_id]
            self._file_id += 1
            file_path = entry.absolute().as_posix()
            folder_name = item.text()
            folder_path = self._folder_path + '/' + folder_name
            self.move_file(file_path, folder_path)
            self._action_list.append('move')
        
        self.print_file_info()
        
        
        