# ---- STL ----

# --- PL ---
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox

class TerrainViewerMainUI(QMainWindow):
    def InitUI(self) -> None:
        MenuBar = self.menuBar()

        StatusBar = self.statusBar()
        StatusBar.showMessage("Ready.")

        SaveAct = QAction('&Save', self)
        SaveAct.setShortcut('Ctrl+S')
        SaveAct.triggered.connect(self.MainProcess.OnClickedSave)

        ExitAct = QAction('&Exit', self)
        ExitAct.setShortcut('Ctrl+Q')
        ExitAct.triggered.connect(self.MainProcess.OnClickedExit)

        FileMenu = MenuBar.addMenu('&File')
        FileMenu.addAction(SaveAct)
        FileMenu.addAction(ExitAct)

        HelpAct = QAction('Help', self)
        HelpAct.triggered.connect(self.ClickedHelp)

        HelpMenu = MenuBar.addMenu('&Help')
        HelpMenu.addAction(HelpAct)
        
        self.setGeometry(0, 0, 1000, 400)
        self.setWindowTitle("TerrainViewer")
        self.show()

    def ClickedHelp(self):
        QMessageBox.information(
            self,
            "Help", 
            """
                こちらのReadmeをご覧ください。<br>
                <a href="https://github.com/pto8913/TerrainViewer">pto8913.github</a>
            """,
            QMessageBox.Ok
        )