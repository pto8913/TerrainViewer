# --- STL ---
from pathlib import Path
import queue
import re
from typing import Dict, List, Tuple

# --- PL ---
import cv2
import numpy as np
import PIL

import matplotlib.pyplot as plt

# from matplotlib.colors import LightSource
# from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_qt5 import FigureCanvasQT as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QListWidget, QTabWidget, 
    QLabel, QProgressBar, QLineEdit, QWidget
)
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# --- MyL ---
from TerrainViewer.UI.TerrainViewerMainProcessUI import TerrainViewerMainProcessUI
from TerrainViewer.SubProcesses.__LoadItemDataThread import LoadedItemDataThread
from TerrainViewer.SubProcesses.ItemImageJoinableTileSearch import ItemImageJoinableTileSearch
from TerrainViewer.UI.SelectFileUI import SelectFileUI

SELECTFILE_TAB_NAME = "Select Files"
RESULTIMAGE_TAB_NAME = "Result Images"

class TerrainViewerMainProcess(TerrainViewerMainProcessUI):
    StatusMessageDelegate = pyqtSignal(str)

    def __init__(self) -> None:
        super(TerrainViewerMainProcess, self).__init__()

        # Drag and Drop
        self.setAcceptDrops(True)

        # self.ItemList と self.SelectFile と self.ResultImageList を持つウィジェット
        self.ItemListTabWidget = QTabWidget()

        # ファイルの名前を見る用のリスト
        self.ItemList = QListWidget()
        self.ItemList.setMinimumSize(200, 500)

        # アイテムをクリックすると、self.CurrentSelectDir が変更される。ダブルクリックされたときにも動く
        self.ItemList.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        # ファイルをダブルクリックすると、self.SelectFileが タブ2 に追加される
        self.ItemList.itemDoubleClicked.connect(self.OnItemDoubleClicked)
        
        # 変換結果の画像を見る用のリスト
        self.ResultImageNameList = QListWidget()
        self.ResultImageNameList.setMinimumSize(100, 500)

        self.ResultImageList = []
        
        # アイテムをクリックすると、そのアイテムのインデックスを取得する
        self.ResultImageNameList.itemSelectionChanged.connect(self.OnResultImageSelectionChanged)
        # アイテムをダブルクリックすると、キャンバスに画像が表示される。
        self.ResultImageNameList.itemDoubleClicked.connect(self.OnResultImageDoubleClicked)
        
        # 欲しいDEMファイルを選択してもらう用のウィジェット。このウィジェットでStartボタンを押すことでファイルの読み込みが始まる
        self.SelectFile = SelectFileUI(100)
        # ファイルの選択を止める。なお、地形図生成の処理もキャンセルされる
        self.SelectFile.CANCEL_SelectFileDelegate.connect(self.OnCloseSelectFileTab)
        # ファイルの読み込みなどの処理を始める
        self.SelectFile.BEGIN_CreateTerrainDelegate.connect(self.OnCreateTerrainThread)

        self.HeightScalar = QLineEdit("64")
        self.HeightScalar.setValidator(QIntValidator())
        self.HeightScalar.textEdited.connect(self.SetHeightScalar)
        self.HeightScalarValue = 32

        # ファイルがあるディレクトリへのパスを保持する
        self.ItemDirList = []

        self.CurrentDir = Path().cwd()
        self.CurrentSelectDir = ""
        
        self.Canvas = QLabel(u"ここに地形図が表示されます")
        self.Canvas.setScaledContents(True)
        self.Canvas.setMinimumSize(500, 400)

        self.LoadProgressBar = QProgressBar()

        # ファイルの読み込みをするスレッド
        self.LoadItemDataThread = QThread()
        self.LoadItemTasks = queue.Queue()
        self.LoadedItemDatas = {}

        # 繋げられるファイルをブロックごとに分けるスレッド
        self.ItemImageJoinableTileSearchThread = QThread()
        self.ItemImageJoinableTiles = []

        self.FolderPtn = re.compile(r"FG-GML-(.*)-(.*)-DEM(.*)")
        self.SetItemList()

        self.InitUI()

    def SetHeightScalar(self, In) -> None:
        if In:
            self.HeightScalarValue = int(In)

    # -------------- Init --------------
    def SetItemList(self) -> None:
        for ItemPath in [p for p in self.CurrentDir.glob("**/*") if re.search(self.FolderPtn, str(p))]:
            if not str(ItemPath.suffix):
                self.ItemDirList.append(str(ItemPath))
                self.ItemList.addItem(str(ItemPath.name))

    # -------------- select file -------------

    # self.SelectFileTab を閉じる。
    def OnCloseSelectFileTab(self) -> None:
        self.ItemListTabWidget.removeTab(1)

    # -------------- user action --------------

    # 選択中のアイテムの
    def OnItemSelectionChanged(self) -> None:
        Idx = self.ItemList.selectedIndexes()[0].row()
        self.CurrentSelectDir = Path(self.ItemDirList[Idx])

    def OnItemDoubleClicked(self, item) -> None:
        idx = self.GetTabIndexOfForQidget(SELECTFILE_TAB_NAME)
        # タブの中にすでにウィンドウがあればそれを削除
        if idx != -1:
            self.ItemListTabWidget.removeTab(idx)
        self.SelectFile.Reset()
        self.ItemListTabWidget.addTab(self.SelectFile, SELECTFILE_TAB_NAME)
        # 追加したウィンドウの位置をタブから取得
        idx = self.GetTabIndexOfForQidget(SELECTFILE_TAB_NAME)
        if idx == -1:
            idx = 1
        self.ItemListTabWidget.setCurrentIndex(idx)

    def OnResultImageSelectionChanged(self):
        self.ResultImageSelectedIdx = self.ResultImageNameList.selectedIndexes()[0].row()

    def OnResultImageDoubleClicked(self):
        self.CreateTerrainImage(self.ResultImageList[self.ResultImageSelectedIdx])

        # -------------- Drag and Drop --------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # FG-GML-*-*=DEN* 形式の名前のフォルダがドロップされたらリストに追加
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            ItemPath = Path(url.toLocalFile())
            if not str(ItemPath.suffix):
                __Match = re.search(self.FolderPtn, ItemPath)
                if __Match:
                    self.ItemDirList.append(str(ItemPath))
                    self.ItemList.addItem(str(ItemPath.name))

    # -------------- UI action --------------
    # ファイルの一行が読み込まれるたびにプログレスバーを更新
    def OnUpdateLoadProgressBar(self, LoadItemProgress: int) -> None:
        self.LoadProgressBar.setValue(LoadItemProgress)

    def GetTabIndexOfForQidget(self, TabName: str) -> None:
        page = self.ItemListTabWidget.findChild(QWidget, TabName)
        if page:
            return self.ItemListTabWidget.IndexOf(page)
        return -1

    def GetTabIndexOfForQListWidget(self, TabName: str) -> None:
        page = self.ItemListTabWidget.findChild(QListWidget, TabName)
        if page:
            return self.ItemListTabWidget.IndexOf(page)
        return -1

    # -------------- create terrain --------------
    def OnCreateTerrainThread(self, InFiles: Dict[str, bool]) -> None:        
        if InFiles == {}:
            return

        UserSelectedFiles = []
        bIsFindTask = False
        # ロードするタスクをキューに詰める
        for path in self.CurrentSelectDir.glob("**/*.xml"):
            path_temp = path.name.split("-")
            if path_temp[4] in InFiles:
                bIsFindTask = True
                UserSelectedFiles.append(path_temp[4])
                self.LoadItemTasks.put(path)
        
        if not bIsFindTask:
            self.SendUIMessage(
                "Error No.1", 
                """
                    The file you selected was not found.<br>
                    Please select another file. <br>
                    Check <a href="https://github.com/pto8913/TerrainViewer/wiki">here</a>
                """
            )
            self.LoadProgressBar.setParent(None)
        else:
            self.LoadedItemDatas = {}
            # 読み込みを始めたら、プログレスバーを表示する
            self.CanvasLayout.addWidget(self.LoadProgressBar)

            # 選択されたファイルを繋げられるようにブロックごとにまとめる
            self.BeginItemImageJoinableTileSearch(UserSelectedFiles)
            self.OnCallNextLoadItemDataTask()

    def CreateTerrainImage(self, Elev) -> None:
        self.ConvertndarrayToImage(Elev)

        w, h = self.FigureCanvas.get_width_height()
        self.ItemImage = QImage(
            self.FigureCanvas.buffer_rgba(), w, h, QImage.Format_ARGB32
        )
        self.Canvas.setPixmap(QPixmap(self.ItemImage))
    
    def ConvertndarrayToImage(self, In2darray: np.ndarray) -> None:
        plt.close()
        fig, ax = plt.subplots()
        # ls = LightSource(azdeg = 180, altdeg = 65)
        # color = ls.shade(self.ElevDatas, plt.get_cmap("rainbow_r"))
        # cs = ax.imshow(self.ElevDatas, plt.get_cmap("rainbow_r"))
        # color = ls.shade(self.ElevDatas, plt.get_cmap("gray"))
        cs = ax.imshow(In2darray, plt.get_cmap("gray"))
        # ax.imshow(color)

        # make_axes = make_axes_locatable(ax)
        # cax = make_axes.append_axes("right", size = "2%", pad = 0.05)
        # fig.colorbar(cs, cax)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
        
        self.FigureCanvas = FigureCanvas(fig)
        self.FigureCanvas.draw()
    
    # -------------- Load Select Item Data --------------
    def OnCallNextLoadItemDataTask(self) -> None:
        if self.LoadItemTasks.qsize() <= 0:
            self.FinishedLoadItemDataTask()
            return
        else:
            # プログレスバーを0％にする
            self.LoadProgressBar.setValue(0)
            self.ForceQuitLoadItemDataTaskThread()
            path = self.LoadItemTasks.get()
            self.StatusMessageDelegate.emit(f"Now Loading {path}")
            self.LoadItemData = LoadedItemDataThread(path)

            self.LoadItemData.ReturnLoadedItemDataDelegate.connect(self.OnGetLoadedItemData)
            self.LoadItemData.ReturnLoadLine.connect(self.OnUpdateLoadProgressBar)
            self.LoadItemData.moveToThread(self.LoadItemDataThread)
            self.LoadItemDataThread.started.connect(self.LoadItemData.BeginLoadItemData)
            
            self.LoadItemDataThread.start()
    
    def OnGetLoadedItemData(self, ItemNum: int, LoadedItemDatas) -> None:
        self.LoadedItemDatas[ItemNum] = LoadedItemDatas
        self.OnCallNextLoadItemDataTask()

    def ForceQuitLoadItemDataTaskThread(self) -> None:
        if self.LoadItemDataThread.isRunning():
            self.LoadItemDataThread.terminate()
            self.LoadItemDataThread.wait()
        
    # ブロックごとにまとめられたタイルを結合して、一枚の画像にする。 
    def FinishedLoadItemDataTask(self) -> None:
        DirName = str(self.CurrentSelectDir.name)

        for Tiles in self.ItemImageJoinableTiles:
            vTemp = np.array([])
            ResultName = ""
            for Tile in Tiles:
                ResultName += str(Tile)
                if not isinstance(Tile, np.ndarray):
                    t = self.LoadedItemDatas.get(Tile)
                    if t is None:
                        vTemp = self.MakeEmptyImage()
                    else:
                        vTemp = t.Reshape()
                else:
                    hTemp = np.array([])
                    for elem in Tile:
                        temp = self.MakeEmptyImage()
                        if elem != -1:
                            t = self.LoadedItemDatas.get(elem)
                            if t is None:
                                temp = self.MakeEmptyImage()
                            else:
                                temp = t.Reshape()

                        if not len(hTemp):
                            hTemp = temp
                        else:
                            hTemp = np.hstack((hTemp, temp))
                    if not len(vTemp):
                        vTemp = hTemp
                    else:
                        vTemp = np.vstack((hTemp, vTemp))

            items = self.ResultImageNameList.findItems(f"{DirName}-{ResultName}", Qt.MatchExactly)
            if len(items) == 0:
                vTemp *= self.HeightScalarValue
                vTemp += 32768
                vTemp = vTemp.astype(np.uint16)

                self.ResultImageNameList.addItem(f"{DirName}-{ResultName}")
                self.ResultImageList.append(vTemp)

            # cv2.imwrite(f"{self.CurrentDir}-cv2-{ResultName}.png", vTemp)

            # self.ConvertndarrayToImage(vTemp)
            # plt.savefig(f"{self.CurrentDir}-{ResultName[0]}.png")

        self.ItemListTabWidget.addTab(self.ResultImageNameList, RESULTIMAGE_TAB_NAME)
        idx = self.GetTabIndexOfForQListWidget(RESULTIMAGE_TAB_NAME)
        if idx == -1:
            idx = 2
        self.ItemListTabWidget.setCurrentIndex(idx)
        # プログレスバーを非表示にする
        self.StatusMessageDelegate.emit("Ready.")
        self.LoadProgressBar.setParent(None)   

    def MakeEmptyImage(self) -> np.ndarray:
        return np.full((150, 225), 0, np.float64)

    # -------------- Joinable Image Search --------------
    
    # 選択されたファイルを繋げられるようにブロックごとにまとめる
    def BeginItemImageJoinableTileSearch(self, InFiles: Dict[str, bool]) -> None:
        self.ForceQuitItemImageJoinableTileSearchThread()
        self.ItemImageJoinableTileSearch = ItemImageJoinableTileSearch(InFiles)
        self.ItemImageJoinableTileSearch.JoinableTilesDelegate.connect(self.OnGetJoinableTiles)
        self.ItemImageJoinableTileSearch.moveToThread(self.ItemImageJoinableTileSearchThread)
        self.ItemImageJoinableTileSearchThread.started.connect(self.ItemImageJoinableTileSearch.BeginSearch)
        self.ItemImageJoinableTileSearchThread.start()
    
    # 強制的にスレッドを終了する
    def ForceQuitItemImageJoinableTileSearchThread(self) -> None:
        if self.ItemImageJoinableTileSearchThread.isRunning():
            self.ItemImageJoinableTileSearchThread.terminate()
            self.ItemImageJoinableTileSearchThread.wait()

    # self.ItemImageJoinableTileSearchThread での結果を受け取る
    def OnGetJoinableTiles(self, InTiles: List[np.ndarray]) -> None:
        self.ItemImageJoinableTiles = InTiles