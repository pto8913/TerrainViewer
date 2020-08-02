# --- STL ---
import re
from pathlib import Path

# --- PL ---
from PyQt5.QtCore import QObject, pyqtSignal

# --- MyL ---
from TerrainViewer.Templates.Templates import LoadedItemData, Math

MINIMUM_ELEV = -100
INF = 1e9+7

class LoadedItemDataThread(QObject):
    ReturnLoadedItemDataDelegate = pyqtSignal(int, LoadedItemData)
    ReturnTotalLineDelegate = pyqtSignal(int)
    ReturnLoadLine = pyqtSignal(int)

    def __init__(self, InItemPath: str):
        super(LoadedItemDataThread, self).__init__()
    
        self.LoadedItemData = LoadedItemData()
        self.LoadedItemData.ItemPath = InItemPath
        self.ItemNum = int(Path(InItemPath).name.split("-")[4])

        # ファイルを読み込む際の正規表現たち
        self.ElevDataPtn = re.compile(r"(.*),(.*)")
        self.StartPointPtn = re.compile(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")

        self.MinimumElev = INF

        self.ItemPath = InItemPath

    def GetStartPoint(self) -> int:
        with open(self.ItemPath, encoding="utf-8") as f:
            __RevLines = f.readlines()[::-1]
            for Line in __RevLines:
                __Match = re.search(self.StartPointPtn, Line)
                if __Match:
                    x, y = int(__Match.groups()[0]), int(__Match.groups()[1])
                    return y * 225 + x


    def BeginLoadItemData(self) -> None:
        with open(self.ItemPath, encoding="utf-8") as f:
            ElevDataIdx = self.GetStartPoint()
            LoadLineCount = 0

            __Lines = f.readlines()
            TotalLine = len(__Lines)
            self.ReturnTotalLineDelegate.emit(TotalLine)
            for Line in __Lines:
                LoadLineCount += 1
                self.ReturnLoadLine.emit(LoadLineCount / TotalLine * 100)
                
                __Match = re.search(self.ElevDataPtn, Line)
                if __Match:
                    Elev = float(__Match.groups()[1])
                    if not isinstance(Elev, float):
                        Elev = MINIMUM_ELEV
                    else:
                        if Elev < self.MinimumElev:
                            if MINIMUM_ELEV < Elev:
                                self.MinimumElev = Elev
                    Elev = Math().clamp(Elev, MINIMUM_ELEV, 9999.0)
                    self.LoadedItemData.AddElev(ElevDataIdx, Elev)
                    ElevDataIdx += 1
        
        self.LoadedItemData.MinimumElev = self.MinimumElev
        self.LoadedItemData.ExchangeMinimumElev()
        self.ReturnLoadedItemDataDelegate.emit(self.ItemNum, self.LoadedItemData)