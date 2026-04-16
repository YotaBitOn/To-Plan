import sys
import warnings

from PySide6.QtWidgets import QApplication

warnings.filterwarnings("ignore", category=RuntimeWarning)
def main():

    app = QApplication(sys.argv)

    from logic.mainWindow import mw
    from logic.pop_up import popup

    mw.ui.show()
    app.exec()

if __name__ == '__main__':
    main()