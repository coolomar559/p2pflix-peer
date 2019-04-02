#!/usr/bin/env python3

from functools import partial
from pathlib import Path
# import time

import add_file as add_file_module
import deregister_file_by_hash
import get_file as get_file_module
import get_file_list
import get_peer_status
import get_tracker_list
from PyQt5 import QtWidgets, uic

UI_FILE_NAME = "./ui/p2pflix-ui.ui"
ERROR_TITLE = "Error!"


# represents the internal model for the ui
# does some ui functions
class Model:
    def __init__(self):
        self.tracker_list = []
        self.file_list_dict = {
            "success": False,
            "error": "No file list yet",
        }
        self.my_file_list_dict = {
            "success": False,
            "error": "No peer status yet",
        }
        self.seeder_subprocess = None

    # gets the tracker list and updates the model
    # this probably doesn't need multithreading
    def get_tracker_list(self):
        self.tracker_list = get_tracker_list.get_local_tracker_list()
        return self.tracker_list

    # gets the file list from the tracker and updates the model
    def get_file_list(self):
        self.file_list_dict = get_file_list.get_file_list()
        return self.file_list_dict

    # gets the peer status (hosted files, seq numbers) from the tracker and updates the model
    def get_my_peer_status(self):
        self.my_file_list_dict = get_peer_status.get_status()
        return self.my_file_list_dict

    # starts the seeding subprocess
    # TODO: seed
    def start_seeding(self):
        print("started seeding")

    # stops the seeding subprocess
    # TODO: stop seed
    def stop_seeding(self):
        print("stopped seeding")


# --- UI stuff that does need multithreading ---


# refreshes the file list on the ui
# this function is a hook for buttons
# real work is done is refresh()
# TODO: thread refresh()
def refresh_hook():
    print("Refresh hook")
    refresh()
    return


# refreshes the file list on the ui
# this should be given to a thread
def refresh():
    table = ui.file_list_table
    name_column = 0
    active_peer_column = 1
    action_column = 2

    # gets the file list from the tracker
    file_list_dict = model.get_file_list()
    if(not file_list_dict["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, file_list_dict["error"])
        return

    file_list = file_list_dict["files"]

    # clears then populates the file list table
    table.setRowCount(0)
    for file in file_list:
        download_button = QtWidgets.QPushButton()
        download_button.setText("Download")
        download_button.clicked.connect(partial(get_file_hook, file["hash"], file["name"]))

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, name_column, QtWidgets.QTableWidgetItem(file["name"]))
        table.setItem(row_position, active_peer_column, QtWidgets.QTableWidgetItem(str(file["active_peers"])))
        table.setCellWidget(row_position, action_column, download_button)


# refreshes the my file list on the ui
# this function is a hook for buttons
# real work is done is peer_status()
# TODO: thread peer_status()
def peer_status_hook():
    print("Peer status hook")
    peer_status()
    return


# refreshes the my file list on the ui
# this should be given to a thread
def peer_status():
    table = ui.my_file_list_table
    name_column = 0
    action_column = 1

    # gets the peer status from the tracker
    peer_status_dict = model.get_my_peer_status()
    if(not peer_status_dict["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, peer_status_dict["error"])
        return

    file_list = peer_status_dict["files"]

    # clears then populates the my files table
    table.setRowCount(0)
    for file in file_list:
        remove_button = QtWidgets.QPushButton()
        remove_button.setText("Remove")
        remove_button.clicked.connect(partial(deregister_file_hook, file["hash"]))

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, name_column, QtWidgets.QTableWidgetItem(file["name"]))
        table.setCellWidget(row_position, action_column, remove_button)

    return


# downloads a file from another peer
# this function is a hook for buttons
# real work is done in get_file()
# TODO: thread get_file
def get_file_hook(file_hash, file_name):
    print("Get file hook - file hash {}".format(file_hash))
    get_file(file_hash, file_name)
    return


# downloads a file from another peer
# this should be given to a thread
# TODO: implement the download bar properly
def get_file(file_hash, file_name):
    # TODO: fix this
    file_metadata = get_file_module.get_file_info(file_hash)

    progress_bar = ui.download_bar
    label = ui.download_label

    ui.download_container.setVisible(True)
    ui.download_container.setEnabled(True)
    label.setText("Downloading {}".format(file_name))
    progress_bar.setValue(0)

    track_progress(Path("./"), progress_bar, 10)

    get_file_module.download(file_metadata)  # make a thread do this

    # await/kill track progress
    QtWidgets.QMessageBox.about(None, "Download Complete!", "{} finished downloading.".format(file_name))

    ui.download_container.setEnabled(False)
    ui.download_container.setVisible(False)

    return


# handles incrementing the progress bar
# TODO: have this work based on files in the directory
def track_progress(directory, progress_bar, chunk_count):
    progress = 0
    while(progress < 100):
        # time.sleep(1)
        progress += 0.00001
        progress_bar.setValue(progress)


# deregisters you as a host for a file
# this is just a hook for buttons
# real work is done in deregister_file()
# TODO: thread deregister_file()
def deregister_file_hook(file_hash):
    print("Deregister file hook - file hash {}".format(file_hash))
    deregister_file(file_hash)
    return


# deregisters you as a host for a file
# this should be given to a thread
def deregister_file(file_hash):
    response = deregister_file_by_hash.deregister_file(file_hash)

    if(not response["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, response["error"])
    else:
        peer_status_hook()  # reload when done

    return


# adds a file to the tracker
# this is just a hook for buttons
# real work done in add_file
# TODO: thread add_file
def add_file_hook():
    print("Add file hook")
    file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Choose file to add", str(Path("./")))[0]
    print("Chose to add {}".format(file_name))
    if(file_name != ""):
        add_file(file_name)
    return
    # reload when done


# adds a file to the tracker
# this should be given to a thread
def add_file(file_name):
    response = add_file_module.add_file_r(file_name)

    if(not response["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, response["error"])
    else:
        refresh_hook()  # reload when done
        peer_status_hook()

    return


# --- UI stuff that doesn't need multithreading ---


# switches to the choose tracker view in the ui
# loads the tracker list from the config file
# does not need multithreading
def choose_tracker():
    print("call choose_tracker_here")

    tracker_list = model.get_tracker_list()

    ui.tracker_list.clear()
    ui.tracker_list.addItems(tracker_list)

    choose_tracker_index = 1
    ui.ui_stack.setCurrentIndex(choose_tracker_index)

    return


# selects a tracker and adds it to the list
# this probably doesn't need multithreading
def choose_tracker_ok():
    selected_item = ui.tracker_list.currentItem()

    if(selected_item is None):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, "You must select a tracker ip.")
        return

    new_ip = selected_item.text()
    print("chose ip {}".format(new_ip))

    update_response = get_tracker_list.update_primary_tracker(new_ip)
    if(not update_response["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, update_response["error"])
        return

    main_window_index = 0
    ui.ui_stack.setCurrentIndex(main_window_index)

    return


# cancels choose tracker changes and returns to the main ui
def choose_tracker_cancel():
    main_window_index = 0
    ui.ui_stack.setCurrentIndex(main_window_index)


# Adds a tracker from the manually enter screen
# does not need multithreading
# TODO: get tracker's tracker list
def choose_tracker_add():
    new_ip = ui.tracker_ip_box.text()
    print("add ip {} to list".format(new_ip))

    # need error stuff here
    if(not get_tracker_list.add_tracker_ip_local(new_ip)):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, "Failed to add ip")
        return

    ui.tracker_ip_box.clear()

    tracker_list = model.get_tracker_list()
    ui.tracker_list.clear()
    ui.tracker_list.addItems(tracker_list)

    return


# handles tab changing to and from main ui tabs
def tab_change(tab_index):
    files_tab_index = 0

    if(tab_index == files_tab_index):
        ui.refresh_my_file_button.hide()
        ui.refresh_file_button.show()
        ui.file_list_table.horizontalHeader().show()
    else:
        ui.refresh_file_button.hide()
        ui.refresh_my_file_button.show()
        ui.my_file_list_table.horizontalHeader().show()

    return


# hangle toggling the seeding button
def toggle_seeding(checked):
    if(checked):
        model.start_seeding()
        ui.actionSeeding.setText("Stop Seeding")
    else:
        model.stop_seeding()
        ui.actionSeeding.setText("Start Seeding")

    return


# initializes the ui hooks
def setup_ui(ui):
    # Refresh buttons setup
    ui.refresh_file_button.clicked.connect(refresh_hook)
    ui.refresh_my_file_button.clicked.connect(peer_status_hook)
    ui.refresh_my_file_button.hide()

    # Tab setup
    ui.tabs.currentChanged.connect(tab_change)

    # Table setups
    ui.file_list_table.setColumnWidth(0, 550)
    ui.file_list_table.setColumnWidth(1, 100)
    ui.my_file_list_table.setColumnWidth(0, 650)

    # Toolbar action setup
    ui.actionAdd_File.triggered.connect(add_file_hook)
    ui.actionChoose_Tracker.triggered.connect(choose_tracker)
    ui.actionSeeding.toggled.connect(toggle_seeding)

    # Choose tracker ui setup
    ui.choose_tracker_ok.clicked.connect(choose_tracker_ok)
    ui.choose_tracker_cancel.clicked.connect(choose_tracker_cancel)
    ui.choose_tracker_add.clicked.connect(choose_tracker_add)

    # Download bar setup
    ui.download_container.setVisible(False)
    ui.download_container.setEnabled(False)

    # deliberately being called without threads to initialize
    refresh()
    peer_status()

    return


# Initialize the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi(Path(__file__).parent.joinpath(UI_FILE_NAME))

model = Model()

setup_ui(ui)

ui.show()
app.exec()
