from backend.listen import Seeder
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable, QThread


# Defines the signals available from a running worker thread.
#
# Supported signals are:
#
# error
#     `tuple` (exctype, value, traceback.format_exc() )
#
# result
#     `object` data returned from processing, anything
#
# progress
#     `int` indicating % progress
#
# listen
#     To be used by the seeder to indicate listening setup
#
# shutdown
#     To be used by the seeder to incidate shutdown
class WorkerSignals(QObject):
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    listen = pyqtSignal()
    shutdown = pyqtSignal()


# Worker thread
#
# Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
class UIWorker(QRunnable):
    def __init__(self, function, *args):
        super(UIWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.function = function
        self.args = args
        self.signals = WorkerSignals()

    # Initialize the runner function with passed args
    @pyqtSlot()
    def run(self):
        # Retrieve args here; and fire processing using them
        result = self.function(*self.args)

        if(result["success"]):
            self.signals.result.emit(result)  # return an ok result
        else:
            self.signals.error.emit(result["error"])  # Return the error


# Progress Worker thread
#
# Inherits from QRunnable to handler worker thread setup, signals and wrap-up as well as
# providing a callback for updating progress.
class ProgressWorker(QRunnable):
    def __init__(self, function, *args):
        super(ProgressWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.function = function
        self.args = args
        self.signals = WorkerSignals()

    # Initialize the runner function with passed args
    @pyqtSlot()
    def run(self):
        # Retrieve args here; and fire processing using them
        result = self.function(self.signals.progress.emit, *self.args)

        if(result["success"]):
            self.signals.result.emit(result)  # return an ok result
        else:
            self.signals.error.emit(result["error"])  # Return the error


# Seeder Worker thread
# Handles setting up the seeder
class SeederThread(QThread):
    def __init__(self):
        super(SeederThread, self).__init__()

        self.signals = WorkerSignals()
        self.seeder = Seeder(self.signals.listen.emit, self.signals.error.emit, self.signals.shutdown.emit)

    # Start the seeder
    @pyqtSlot()
    def run(self):
        self.seeder.run()

    # Stop the seeder
    @pyqtSlot()
    def stop(self):
        self.seeder.stop()
