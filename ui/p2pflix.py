from functools import partial
from pathlib import Path
import time

from PyQt5 import QtWidgets, uic

UI_FILE_NAME = "p2pflix-ui.ui"

test_file_list = [
        {
            "id": 1,    #integer
            "name": "avengers_XVID.mp4",   #string
            "hash": "ajkhjksdksffs", #base64 string
            "active_peers": 10 #integer
        },
        {
            "id": 2,    #integer
            "name": "avengers_2_XVID.mp4",   #string
            "hash": "ajkhjkasdasdsdksffs", #base64 string
            "active_peers": 2 #integer
        },
        {
            "id": 3,    #integer
            "name": "bush_doing_9-11_XVID.mp4",   #string
            "hash": "ajjhgkjkhjksdksffs", #base64 string
            "active_peers": 3 #integer
        },
        {
            "id": 4,    #integer
            "name": "YEEEEEEEEEEEEEEEEEEEEEEEEEEEEET.mp4",   #string
            "hash": "ajadagggkhjksdksffs", #base64 string
            "active_peers": 100 #integer
        },    
    ]

test_my_file_dict = {
    "success": True,
    "files": [
        {
            "id": 1,
            "name": "shut_up_your_mouse_obama.flac",
            "hash": "hahahaheeeheeeheeeeee",
        },
    ],
    "expected_seq_number": 0,
    "ka_expected_seq_number": 0,
}


def refresh():
    print("refreshing file list")
    table = ui.file_list_table
    name_column = 0
    active_peer_column = 1
    action_column = 2

    file_list = test_file_list

    table.setRowCount(0)
    for file in file_list:
        download_button = QtWidgets.QPushButton()
        download_button.setText("Download")
        download_button.clicked.connect(partial(get_file, file["hash"]))

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

    peer_status_dict = test_my_file_dict
    if(not peer_status_dict["success"]):
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


def get_file(file_hash):
    print("Getting info for file with hash {}".format(file_hash))


def deregister_file(file_hash):
    print("Deregister file with hash {}".format(file_hash))


def add_file():
    print("call add file here")
    file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Choose file to add", str(Path("./")))[0]
    print(file_name)


def choose_tracker():
    print("call choose_tracker_here")


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


def setup_ui(ui):
    ui.refresh_file_button.clicked.connect(refresh)
    ui.refresh_my_file_button.clicked.connect(peer_status)
    ui.refresh_my_file_button.hide()

    ui.tabs.currentChanged.connect(tab_change)

    ui.actionAdd_File.triggered.connect(add_file)
    ui.actionChoose_Tracker.triggered.connect(choose_tracker)


# Initialize the UI
app = QtWidgets.QApplication([])
ui = uic.loadUi(Path(__file__).parent.joinpath(UI_FILE_NAME))

setup_ui(ui)

ui.show()
app.exec()
