import sys

from PyQt6.QtWidgets import QApplication

from chapter6.ex127.stock_analysis import StockAnalysisApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockAnalysisApp()
    window.show()
    sys.exit(app.exec())  # Changed from exec_() to exec()