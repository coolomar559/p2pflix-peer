#!/usr/bin/env python3

from functools import partial
from pathlib import Path

from backend import deregister_file_by_hash, discrepancy_resolution, get_file_list, get_peer_status, get_tracker_list
import backend.add_file as add_file_module
import backend.get_file as get_file_module
from backend.ui_worker import ProgressWorker, SeederThread, UIWorker
from PyQt5 import QtCore, QtWidgets, uic


UI_FILE_NAME = "./ui/p2pflix-ui.ui"
SYNC_DIALOGUE_NAME = "./ui/sync-dialogue.ui"
ERROR_TITLE = "Error!"


# represents the internal model for the ui
# does some ui functions
class Model:
    def __init__(self):
        self.seeder_subprocess = None
        self.total_chunk_count = 0
        self.current_chunk_count = 0
        self.current_file_name = ""
        self.seeder_thread = None


# --- UI stuff that does need multithreading ---


# refreshes the file list on the ui
# this function is a hook for buttons
# real work is done is refresh()
def refresh_hook():
    print("Refresh hook")
    ui.file_list_table.setRowCount(0)

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
    worker = UIWorker(get_file, file_hash, file_name)
    worker.signals.result.connect(get_file_ui_handler)
    worker.signals.error.connect(error_handler)
    ui_thread_pool.start(worker)
    return


# downloads a file from another peer
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
    worker.signals.error.connect(get_file_error_handler)
    worker.signals.progress.connect(download_progress_ui_handler)
    ui_thread_pool.start(worker)
    return


# hides the download ui when there's an error downloading a file
def get_file_error_handler(error_msg):
    error_handler(error_msg)
    ui.download_container.setEnabled(False)
    ui.download_container.setVisible(False)
    return


# handles the ui elements for the progress bar
def download_progress_ui_handler(progress):
    if(not progress):
        return

    model.current_chunk_count += 1

    progress_percent = int((model.current_chunk_count/model.total_chunk_count)*100)
    ui.download_bar.setValue(progress_percent)
    return


# handles the ui elements for finishting a download
def download_ui_handler(download_result):
    show_popup("Download Complete!", "{} finished downloading.".format(download_result["name"]))
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


# Starts or stops the seeder depending on whether or not it's running
def seeding_hook(checked):
    print("seeding hook")

    # We don't want to actually toggle the button
    ui.actionSeeding.setChecked(not checked)

    # If the seeder is not None, we must have started it, so stop it
    if model.seeder_thread is not None:
        model.seeder_thread.stop()
        return

    # Otherwise set up some signals and initialize the seeder
    thread = SeederThread()
    thread.signals.listen.connect(seeding_listen_ui_handler)
    thread.signals.error.connect(seeding_error_handler)
    thread.signals.shutdown.connect(seeding_shutdown_ui_handler)
    model.seeder_thread = thread
    model.seeder_thread.start()
    return


# Handle the seeder listen event
def seeding_listen_ui_handler():
    ui.actionSeeding.setChecked(True)
    return


# Handle errors from the seeder
def seeding_error_handler(error_msg):
    error_handler(error_msg)
    ui.actionSeeding.setChecked(False)
    model.seeder_thread = None
    return


# Handle the seeder shutting down
def seeding_shutdown_ui_handler():
    ui.actionSeeding.setChecked(False)
    model.seeder_thread = None
    return


# pops up an error happened messagebox
def error_handler(error_string):
    show_popup(ERROR_TITLE, error_string)


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
        show_popup(ERROR_TITLE, "You must select a tracker ip.")
        return

    new_ip = selected_item.text()
    print("Chose ip {}".format(new_ip))

    update_response = get_tracker_list.update_primary_tracker(new_ip)
    if(not update_response["success"]):
        show_popup(ERROR_TITLE, update_response["error"])
        return

    refresh_hook()
    peer_status_hook()

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
        show_popup(ERROR_TITLE, "Failed to add ip")
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


# handles syncing the peer and tracker
def sync_hook():
    sync_dialogue.show()


# handles pressing cancel button
def sync_cancel_hook():
    sync_dialogue.hide()
    refresh_hook()
    peer_status_hook()
    sync_reset()


# handles pressing ok button
def sync_ok_hook():
    sync_dialogue.sync_message_text.setText("Now syncing. Please wait...")
    sync_dialogue.sync_ok_button.hide()
    sync_dialogue.sync_cancel_button.hide()
    sync_dialogue.setWindowTitle("Tracker Sync In Progress")

    # double process events because of qt jank
    QtWidgets.QApplication.processEvents()
    QtWidgets.QApplication.processEvents()

    result = discrepancy_resolution.resolve()

    if not result["success"]:
        error_handler(result["error"])

    sync_cancel_hook()


# sets the sync back to normal
def sync_reset():
    sync_dialogue.sync_message_text.setText("Are you sure? This may delete some files you are seeding.")
    sync_dialogue.sync_ok_button.show()
    sync_dialogue.sync_cancel_button.show()
    sync_dialogue.setWindowTitle("Confirm Tracker Sync")

    # double process events because of qt jank
    QtWidgets.QApplication.processEvents()
    QtWidgets.QApplication.processEvents()


# initializes the sync dialogue box
def setup_sync_dialogue(sync_dialogue):
    sync_dialogue.sync_ok_button.clicked.connect(sync_ok_hook)
    sync_dialogue.sync_cancel_button.clicked.connect(sync_cancel_hook)


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
    ui.actionSeeding.triggered.connect(seeding_hook)
    ui.actionTracker_Sync.triggered.connect(sync_hook)

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


# Helper function for showing a popup window with some information
# Blocks UI interaction until the popup is closed
def show_popup(title, message):
    box = QtWidgets.QMessageBox()
    box.setWindowTitle(title)
    box.setText(message)
    box.exec()


# Initialize the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi(Path(__file__).parent.joinpath(UI_FILE_NAME))
sync_dialogue = uic.loadUi(Path(__file__).parent.joinpath(SYNC_DIALOGUE_NAME))

model = Model()

# start threadpool
ui_thread_pool = QtCore.QThreadPool()

setup_ui(ui)
setup_sync_dialogue(sync_dialogue)

ui.show()
app.exec()
