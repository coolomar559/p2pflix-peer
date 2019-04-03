from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable


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
class WorkerSignals(QObject):
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


# Worker thread
#
# Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
#
# :param callback: The function callback to run on this worker thread. Supplied args and
#                     kwargs will be passed through to the runner.
# :type callback: function
# :param args: Arguments to pass to the callback function
# :param kwargs: Keywords to pass to the callback function
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
# Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
#
# :param callback: The function callback to run on this worker thread. Supplied args and
#                     kwargs will be passed through to the runner.
# :type callback: function
# :param args: Arguments to pass to the callback function
# :param kwargs: Keywords to pass to the callback function
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
