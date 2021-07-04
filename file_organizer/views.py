# -*- coding: utf-8 -*-
# file_organizer/views.py

"""This module provides the File organizer main window."""
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from send2trash import send2trash
import shutil
import os
import platform
import humanize

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QInputDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.Qt import Qt

from .ui.window import Ui_Window

RECENT_DAYS = 30
most_recent = datetime.now() - timedelta(days=RECENT_DAYS)
IMAGE_ROOT_PATH = '/Users/shiqiangxia/Desktop/file_organizer_project/file_organizer/ui/images/'


class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()
        self._appStatus = 0
        self._folder_path = None
        self._folder_dir = None

        self._file_list = []

        self._num_files = 0
        self._num_folders = 0
        self._folder_size = 0
        self._num_recent_files = 0
        self._file_id = 0

        self._trash_path = None
        self._action_list = []
        self._target_path = []

        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        self.setupUi(self)
        self.infoText.setPlainText(
            'Please [Open] a folder to start a new organizing task.')
        # set example icon
        image_path = IMAGE_ROOT_PATH + 'txt.png'
        pixmap = QPixmap(image_path)
        self.picView.setPixmap(pixmap)
        # preivew button only for Mac
        if platform.system() == 'Darwin':
            self.previewBtn.setEnabled(True)
        else:
            self.previewBtn.setEnabled(False)
    
    def _connectSignalsSlots(self):
        self.openBtn.clicked.connect(self.open_folder)
        self.startBtn.clicked.connect(self.start_organize_file)
        self.previewBtn.clicked.connect(self.preview_file)
        self.skipBtn.clicked.connect(self.skip_file)
        self.skipLeftBtn.clicked.connect(self.skip_file_left)
        self.deleteBtn.clicked.connect(self.delete_file)
        self.undoBtn.clicked.connect(self.undo_file)
        self.doneBtn.clicked.connect(self.done_organize)
        self.moveFolderList.itemDoubleClicked.connect(
            self.move_to_selected_folder)
        self.renameBtn.clicked.connect(self.rename_file)

    # ------ some help functions -----------
    def create_dir(self, current_dir, name):
        path = current_dir.absolute().as_posix() + '/' + name
        p = Path(path)
        try:
            p.mkdir()
        except FileExistsError:
            print('Folder %s already exists!'%name)
        return(path)

    def get_icon(self, extension):
        if extension in ['.jpg', '.png', '.pdf', '.txt', '.doc', '.xlsx', '.pptx', '.py']:
            icon_name = extension[1:]+'.png'
        elif extension in ['.gif', '.tiff', '.bmp', '.svg', '.eps', '.jpeg', '.heic', '.heif']:
            icon_name = 'image.png'
        elif extension in ['.mp3', '.wav', '.wma']:
            icon_name = 'music.png'
        elif extension in ['.mp4', '.mov', '.avi', '.wmv', '.m4v', '.mpg', '.mpeg', '.webm']:
            icon_name = 'video.png'
        elif extension in ['.7z', '.zip', '.rar', '.tar', '.gz']:
            icon_name = 'zip.png'
        elif extension in ['.c', '.cpp', '.java', '.h', '.html', '.php', '.hpp', '.cxx', '.c++', '.hxx', '.h++']:
            icon_name = 'code.png'
        elif extension in ['.dmg', '.exe', '.DS_Store']:
            icon_name = 'setting.png'
        else:
            icon_name = 'file.png'
        return(icon_name)

    def print_file_info(self):
        entry = self._file_list[self._file_id]
        file_name = entry.name
        count = self._file_id + 1
        file_size = humanize.naturalsize(entry.stat().st_size)
        self.infoText.setPlainText(
            f'Start organizing....\nPress F1 to preview (Mac only)\nFile {count}/{self._num_files},'
            + f' Size: {file_size}')
        self.fileNameLabel.setText(file_name)

        # set file picture
        extension = entry.suffix
        icon_name = self.get_icon(extension)
        image_path = IMAGE_ROOT_PATH + icon_name
        pixmap = QPixmap(image_path)
        self.picView.setPixmap(pixmap)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F1:
            self.preview_file()

    def move_file(self, file_path, target_path):
        temp_path = shutil.move(file_path, target_path)
        self._target_path.append(temp_path)

    def pop_from_file_list(self):
        entry = self._file_list.pop(self._file_id)
        self._num_files -= 1
        if self._file_id >= self._num_files:
            self._file_id -= 1
        return(entry)

    # ------ Actions -----------
    def open_folder(self):
        if self._appStatus == 0:
            # status 0: open a folder
            if self.dirEdit.text():
                initDir = self.dirEdit.text()
            else:
                initDir = str(Path.home())

            self._folder_path = QFileDialog.getExistingDirectory(
                self, "Select a folder", initDir)

            self.dirEdit.setText(self._folder_path)
            self._folder_dir = Path(self._folder_path)
            self._appStatus = 1

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
                + f'Size: {natural_size}\n'+'Click [Start] to start organizing...')
        else:
            QMessageBox.warning(self, 'Warning',
                                'Click [Done] to complete current task first')

    def start_organize_file(self):
        if self._appStatus == 1:
            # status 1: start to organize files
            # create trash bin folder
            self._trash_path = self.create_dir(self._folder_dir, 'trash_bin')
            # print the file info
            self.print_file_info()
            self._appStatus = 2
        elif self._appStatus == 0:
            QMessageBox.warning(self, 'Warning',
                                'Click [Open] to open a folder first')
        else:
            QMessageBox.warning(self, 'Warning',
                                'Click [Done] to complete current task first')

    def preview_file(self):
        if self._appStatus == 2:
            # preview the current file
            entry = self._file_list[self._file_id]
            file_path = entry.absolute().as_posix()
            cmd = "qlmanage -p " + file_path
            os.popen(cmd).read()
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')

    def skip_file(self):
        if self._appStatus == 2:
            # skip the current file and move right 
            self._action_list.append('skip')
            self._file_id += 1
            if self._file_id>=self._num_files:
                self._file_id = 0
            self.print_file_info()
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')

    def skip_file_left(self):
        if self._appStatus == 2:
            # skip the current file and move left 
            self._action_list.append('skip_left')
            self._file_id -= 1
            if self._file_id < 0:
                self._file_id = self._num_files - 1
            self.print_file_info()
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')

    def delete_file(self):
        if self._appStatus == 2:
            entry = self.pop_from_file_list()
            file_path = entry.absolute().as_posix()
            self.move_file(file_path, self._trash_path)
            self._action_list.append('delete')
            self.print_file_info()
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')
  
    def undo_file(self):
        if self._appStatus == 2:
            # check if undo is possible
            if self._action_list:
                # undo the last action
                action = self._action_list.pop()
                if (action == 'delete') or (action == 'move'):
                    temp_path = self._target_path.pop()
                    new_path = shutil.move(temp_path, self._folder_dir)
                    self._file_list.insert(self._file_id, Path(new_path))
                    self._num_files += 1
                elif (action == 'skip'):
                    self._file_id -= 1
                    if self._file_id < 0:
                        self._file_id = self._num_files - 1
                elif (action == 'skip_left'):
                    self._file_id += 1
                    if self._file_id >= self._num_files:
                        self._file_id = 0

            else:
                QMessageBox.warning(self, 'Warning', 'No more undo action!')

            self.print_file_info()
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')
       
    def done_organize(self):
        if self._appStatus == 2:
            # move trash_bin to real trash folder
            send2trash(self._trash_path)
            self.infoText.setPlainText('Done!\nPlease [Open] a folder to start a new organizing task.')
            self.dirEdit.setText('')
            self._appStatus = 0
        elif self._appStatus == 1:
            self.infoText.setPlainText('Done!\nPlease [Open] a folder to start a new organizing task.')
            self.dirEdit.setText('')
            self._appStatus = 0
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')
    
    def move_to_selected_folder(self, item):
        if self._appStatus == 2:
        
            if item.text() == '+ Add folder (double click)':
                # add folder to move list
                # get folder name
                folder_name, ok  = QInputDialog.getText(
                    self, 'Input folder name', 'Folder name:')
                if ok:
                    entry = self.pop_from_file_list()
                    file_path = entry.absolute().as_posix()
                    # create folder
                    folder_path = self.create_dir(self._folder_dir, folder_name)
                    # move file to folder
                    self.move_file(file_path, folder_path)
                    self._action_list.append('move')
                    # add folder to moveFolder List
                    item = QListWidgetItem(folder_name)
                    icon = QIcon()
                    icon.addPixmap(QPixmap(IMAGE_ROOT_PATH+'folder.png'), QIcon.Selected, QIcon.Off)
                    item.setIcon(icon)
                    self.moveFolderList.addItem(item)
            else:
                # move file to selected folder
                entry = self.pop_from_file_list()
                file_path = entry.absolute().as_posix()
                folder_name = item.text()
                folder_path = self._folder_path + '/' + folder_name
                self.move_file(file_path, folder_path)
                self._action_list.append('move')
            
            self.print_file_info()
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')
        
    def rename_file(self):
        if self._appStatus == 2:
            if self.renameEdit.text():
                new_name = self.renameEdit.text()
                new_path = self._folder_path + '/' + new_name
                entry = self._file_list[self._file_id]
                file_dir = Path(new_path)
                entry.rename(file_dir)
                self._file_list[self._file_id] = file_dir
                self.print_file_info()
                self.renameEdit.setText('')
            else:
                QMessageBox.warning(self, 'Warning', 'Please input new name first!')
        else:
            QMessageBox.warning(self, 'Warning',
                                'Start a task first. ')