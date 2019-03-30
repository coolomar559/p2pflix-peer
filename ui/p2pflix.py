from functools import partial
from pathlib import Path
import time

from PyQt5 import QtWidgets, uic

UI_FILE_NAME = "p2pflix-ui.ui"
ERROR_TITLE = "Error!"


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

    def get_tracker_list(self):
        self.tracker_list = test_tracker_list
        return self.tracker_list

    def get_file_list(self):
        self.file_list_dict = test_file_dict
        return self.file_list_dict

    def get_my_peer_status(self):
        self.my_file_list_dict = test_my_file_dict
        return self.my_file_list_dict

    def start_seeding(self):
        print("started seeding")

    def stop_seeding(self):
        print("stopped seeding")


test_file_dict = {
    "success": True,
    "files": [
        {
            "id": 1,
            "name": "avengers_XVID.mp4",
            "hash": "ajkhjksdksffs",
            "active_peers": 10,
        },
        {
            "id": 2,
            "name": "avengers_2_XVID.mp4",
            "hash": "ajkhjkasdasdsdksffs",
            "active_peers": 2,
        },
        {
            "id": 3,
            "name": "bush_doing_9-11_XVID.mp4",
            "hash": "ajjhgkjkhjksdksffs",
            "active_peers": 3,
        },
        {
            "id": 4,
            "name": "YEEEEEEEEEEEEEEEEEEEEEEEEEEEEET.mp4",
            "hash": "ajadagggkhjksdksffs",
            "active_peers": 100,
        },
    ],
}

test_my_file_dict = {
    "success": True,
    "files": [
        {
            "id": 1,
            "name": "shut_up_your_mouse_obama.flac",
            "hash": "hahahaheeeheeeheeeeee",
        },
        {
            "id": 2,
            "name": "shut_up_your_mouse_2_electric_boogaloo.flac",
            "hash": "here_come_dat_boi",
        },
    ],
    "expected_seq_number": 0,
    "ka_expected_seq_number": 0,
}

test_tracker_list = [
    "53.180.128.225",
    "154.23.221.244",
    "30.136.157.9",
    "82.107.143.217",
    "201.29.142.114",
    "144.59.12.133",
    "162.155.32.59",
    "49.68.33.160",
]

test_tracker_list_2 = []


def refresh():
    print("refreshing file list")
    table = ui.file_list_table
    name_column = 0
    active_peer_column = 1
    action_column = 2

    file_list_dict = model.get_file_list()
    if(not file_list_dict["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, file_list_dict["error"])
        return

    file_list = file_list_dict["files"]

    table.setRowCount(0)
    for file in file_list:
        download_button = QtWidgets.QPushButton()
        download_button.setText("Download")
        download_button.clicked.connect(partial(get_file, file["hash"], file["name"]))

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, name_column, QtWidgets.QTableWidgetItem(file["name"]))
        table.setItem(row_position, active_peer_column, QtWidgets.QTableWidgetItem(str(file["active_peers"])))
        table.setCellWidget(row_position, action_column, download_button)


def peer_status():
    print("peer status")
    table = ui.my_file_list_table
    name_column = 0
    action_column = 1

    peer_status_dict = model.get_my_peer_status()
    if(not peer_status_dict["success"]):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, peer_status_dict["error"])
        return

    file_list = peer_status_dict["files"]

    table.setRowCount(0)
    for file in file_list:
        remove_button = QtWidgets.QPushButton()
        remove_button.setText("Remove")
        remove_button.clicked.connect(partial(deregister_file, file["hash"]))

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, name_column, QtWidgets.QTableWidgetItem(file["name"]))
        table.setCellWidget(row_position, action_column, remove_button)


def get_file(file_hash, file_name):
    print("Getting file with hash {}".format(file_hash))
    progress_bar = ui.download_bar
    label = ui.download_label

    ui.download_container.setVisible(True)
    ui.download_container.setEnabled(True)
    label.setText("Downloading {}".format(file_name))
    progress_bar.setValue(0)

    progress = 0
    while(progress < 100):
        #time.sleep(1)
        progress += 0.000001
        progress_bar.setValue(progress)

    QtWidgets.QMessageBox.about(None, "Download Complete!", "{} finished downloading.".format(file_name))

    ui.download_container.setEnabled(False)
    ui.download_container.setVisible(False)


def deregister_file(file_hash):
    print("Deregister file with hash {}".format(file_hash))
    # reload when done


def add_file():
    print("call add file here")
    file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Choose file to add", str(Path("./")))[0]
    print(file_name)
    # reload when done


def choose_tracker():
    print("call choose_tracker_here")

    tracker_list = model.get_tracker_list()

    ui.tracker_list.clear()
    ui.tracker_list.addItems(tracker_list)

    choose_tracker_index = 1
    ui.ui_stack.setCurrentIndex(choose_tracker_index)


def choose_tracker_ok():
    selected_item = ui.tracker_list.currentItem()

    if(selected_item is None):
        QtWidgets.QMessageBox.about(None, ERROR_TITLE, "You must select a tracker ip.")
        return

    new_ip = selected_item.text()
    print("chose ip {}".format(new_ip))

    main_window_index = 0
    ui.ui_stack.setCurrentIndex(main_window_index)


def choose_tracker_cancel():
    main_window_index = 0
    ui.ui_stack.setCurrentIndex(main_window_index)


def choose_tracker_add():
    new_ip = ui.tracker_ip_box.text()
    print("add ip {} to list".format(new_ip))

    ui.tracker_ip_box.clear()

    tracker_list = test_tracker_list
    ui.tracker_list.clear()
    ui.tracker_list.addItems(tracker_list)


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


def toggle_seeding(checked):
    if(checked):
        model.start_seeding()
        ui.actionSeeding.setText("Stop Seeding")
    else:
        model.stop_seeding()
        ui.actionSeeding.setText("Start Seeding")


def setup_ui(ui):
    # Refresh buttons setup
    ui.refresh_file_button.clicked.connect(refresh)
    ui.refresh_my_file_button.clicked.connect(peer_status)
    ui.refresh_my_file_button.hide()

    # Tab setup
    ui.tabs.currentChanged.connect(tab_change)

    # Table setups
    ui.file_list_table.setColumnWidth(0, 550)
    ui.file_list_table.setColumnWidth(1, 100)
    ui.my_file_list_table.setColumnWidth(0, 650)

    # Toolbar action setup
    ui.actionAdd_File.triggered.connect(add_file)
    ui.actionChoose_Tracker.triggered.connect(choose_tracker)
    ui.actionSeeding.toggled.connect(toggle_seeding)

    # Choose tracker ui setup
    ui.choose_tracker_ok.clicked.connect(choose_tracker_ok)
    ui.choose_tracker_cancel.clicked.connect(choose_tracker_cancel)
    ui.choose_tracker_add.clicked.connect(choose_tracker_add)

    # Download bar setup
    ui.download_container.setVisible(False)
    ui.download_container.setEnabled(False)

    refresh()
    peer_status()


# Initialize the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi(Path(__file__).parent.joinpath(UI_FILE_NAME))

model = Model()

setup_ui(ui)

ui.show()
app.exec()
