#!/usr/bin/env python3

from functools import partial
from pathlib import Path

from backend import deregister_file_by_hash, get_file_list, get_peer_status, get_tracker_list
import backend.add_file as add_file_module
import backend.get_file as get_file_module
from backend.ui_worker import ProgressWorker, UIWorker
from PyQt5 import QtCore, QtWidgets, uic


UI_FILE_NAME = "./ui/p2pflix-ui.ui"
ERROR_TITLE = "Error!"


# represents the internal model for the ui
# does some ui functions
class Model:
    def __init__(self):
        self.seeder_subprocess = None
        self.total_chunk_count = 0
        self.current_chunk_count = 0
        self.current_file_name = ""

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
def refresh_hook():
    print("Refresh hook")
    worker = UIWorker(refresh)
    worker.signals.result.connect(refresh_ui_handler)
    worker.signals.error.connect(error_handler)
    ui_thread_pool.start(worker)
    return


# refreshes the file list on the ui
# this should be given to a thread
def refresh():
    # gets the file list from the tracker
    return get_file_list.get_file_list()


# handles the ui elements of refresh
def refresh_ui_handler(file_dict):
    file_list = file_dict["files"]
    table = ui.file_list_table
    name_column = 0
    active_peer_column = 1
    action_column = 2

    # clears then populates the file list table
    table.setRowCount(0)
    for file in file_list:
        download_button = QtWidgets.QPushButton()
        download_button.setText("Download")
        download_button.clicked.connect(partial(get_file_hook, file["full_hash"], file["name"]))

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, name_column, QtWidgets.QTableWidgetItem(file["name"]))
        table.setItem(row_position, active_peer_column, QtWidgets.QTableWidgetItem(str(file["active_peers"])))
        table.setCellWidget(row_position, action_column, download_button)


# refreshes the my file list on the ui
# this function is a hook for buttons
# real work is done is peer_status()
def peer_status_hook():
    print("Peer status hook")
    worker = UIWorker(peer_status)
    worker.signals.result.connect(peer_status_ui_handler)
    worker.signals.error.connect(error_handler)
    ui_thread_pool.start(worker)
    return


# refreshes the my file list on the ui
# this should be given to a thread
def peer_status():
    # gets the peer status from the tracker
    return get_peer_status.get_status()


# handles the ui elements of peer_status
def peer_status_ui_handler(file_dict):
    file_list = file_dict["files"]
    table = ui.my_file_list_table
    name_column = 0
    action_column = 1

    # clears then populates the my files table
    table.setRowCount(0)
    for file in file_list:
        remove_button = QtWidgets.QPushButton()
        remove_button.setText("Remove")
        remove_button.clicked.connect(partial(deregister_file_hook, file["full_hash"]))

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, name_column, QtWidgets.QTableWidgetItem(file["name"]))
        table.setCellWidget(row_position, action_column, remove_button)


# downloads a file from another peer
# this function is a hook for buttons
# real work is done in get_file()
def get_file_hook(file_hash, file_name):
    print("Get file hook - file hash {}".format(file_hash))
    # thread = Thread(target=get_file, args=(file_hash, file_name), daemon=True)
    # thread.start()
    worker = UIWorker(get_file, file_hash, file_name)
    worker.signals.result.connect(get_file_ui_handler)
    worker.signals.error.connect(error_handler)
    ui_thread_pool.start(worker)
    return


# downloads a file from another peer
# this should be given to a thread
# TODO: implement the download bar properly
def get_file(file_hash, file_name):
    return get_file_module.get_file_info(file_hash)


# handles the ui elements for get_file
def get_file_ui_handler(file_metadata):
    # show ui
    progress_bar = ui.download_bar
    label = ui.download_label

    ui.download_container.setVisible(True)
    ui.download_container.setEnabled(True)
    label.setText("Downloading {}".format(file_metadata["name"]))
    progress_bar.setValue(0)

    model.current_chunk_count = 0
    model.total_chunk_count = len(file_metadata["chunks"])
    model.current_file_name = file_metadata["name"]

    # spin thread
    worker = ProgressWorker(get_file_module.download_file, file_metadata)
    worker.signals.result.connect(download_ui_handler)
    worker.signals.error.connect(error_handler)
    worker.signals.progress.connect(download_progress_ui_handler)
    ui_thread_pool.start(worker)
    return


def download_progress_ui_handler(progress):
    if(not progress):
        return

    model.current_chunk_count += 1

    progress_percent = int((model.current_chunk_count/model.total_chunk_count)*100)
    ui.download_bar.setValue(progress_percent)
    return


def download_ui_handler(_download_result):
    QtWidgets.QMessageBox.about(None, "Download Complete!", "{} finished downloading.".format(model.current_file_name))
    # hide container
    ui.download_container.setEnabled(False)
    ui.download_container.setVisible(False)
    return


# handles incrementing the progress bar
def track_progress(directory, progress_bar, chunk_count):
    directory.mkdir(parents=True, exist_ok=True)
    progress = 0
    files_in_directory = len(list(directory.iterdir()))
    while(files_in_directory < chunk_count):
        progress = int((files_in_directory/chunk_count)*100)
        progress_bar.setValue(progress)
        files_in_directory = len(list(directory.iterdir()))

    progress = int((files_in_directory/chunk_count)*100)
    progress_bar.setValue(progress)

    return


# deregisters you as a host for a file
# this is just a hook for buttons
# real work is done in deregister_file()
def deregister_file_hook(file_hash):
    print("Deregister file hook - file hash {}".format(file_hash))
    worker = UIWorker(deregister_file, file_hash)
    worker.signals.result.connect(deregister_file_ui_handler)
    worker.signals.error.connect(error_handler)
    ui_thread_pool.start(worker)
    return


# deregisters you as a host for a file
# this should be given to a thread
def deregister_file(file_hash):
    return deregister_file_by_hash.deregister_file(file_hash)


# handles the ui elements for deregister_file
def deregister_file_ui_handler():
    peer_status_hook()
    return


# adds a file to the tracker
# this is just a hook for buttons
# real work done in add_file
def add_file_hook():
    print("Add file hook")
    file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Choose file to add", str(Path("./")))[0]
    print("Chose to add {}".format(file_name))
    if(file_name != ""):
        worker = UIWorker(add_file, file_name)
        worker.signals.result.connect(add_file_ui_handler)
        worker.signals.error.connect(error_handler)
        ui_thread_pool.start(worker)
    return


# adds a file to the tracker
# this should be given to a thread
def add_file(file_name):
    return add_file_module.add_file_r(file_name)


# handles the ui elements for add_file
def add_file_ui_handler():
    refresh_hook()
    peer_status_hook()
    return


# pops up an error happened messagebox
def error_handler(error_string):
    QtWidgets.QMessageBox.about(None, ERROR_TITLE, error_string)


# --- UI stuff that doesn't need multithreading ---


# switches to the choose tracker view in the ui
# loads the tracker list from the config file
# does not need multithreading
def choose_tracker():
    print("Choose tracker")

    tracker_list = get_tracker_list.get_local_tracker_list()

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
    print("Chose ip {}".format(new_ip))

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
def choose_tracker_add():
    new_ip = ui.tracker_ip_box.text()
    print("Add ip {} to list".format(new_ip))

    # need error stuff here
    if(not get_tracker_list.add_tracker_ip_local(new_ip)):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, "Failed to add ip")
        return

    ui.tracker_ip_box.clear()

    tracker_list = get_tracker_list.get_local_tracker_list()
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
    refresh_hook()
    peer_status_hook()

    return


# Initialize the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi(Path(__file__).parent.joinpath(UI_FILE_NAME))

model = Model()

# start threadpool
ui_thread_pool = QtCore.QThreadPool()

setup_ui(ui)

ui.show()
app.exec()
