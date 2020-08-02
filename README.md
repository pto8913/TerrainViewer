# 目次
・[紹介](#terrainviewer)<br>
・[使用モジュール](#使用モジュール)<br>
・[セットアップ](#セットアップ)<br>
・[使い方](#使い方)<br>
・[データをウィンドウを開いてから追加する](#データをウィンドウを開いてから追加する)<br>
・[動かない](#動かない)<br>

# TerrainViewer
国土地理院のデータから地形図を生成し、画像を保存できるデスクトップアプリです。

![intro](https://github.com/pto8913/TerrainViewer/blob/images/Intro.png)<br>

本当はexe化しようと思ったのですが、exe化すると開けなくなったのでやめました。ごめんなさい。<br>

# 使用モジュール
・PyQt5.13.0 <br>
[riverbankcomputing](https://riverbankcomputing.com/software/pyqt/download5)
・matplotlib3.3.0<br>
[matplotlib.org](https://matplotlib.org/)

# セットアップ
![downloadzip](https://github.com/pto8913/TerrainViewer/blob/images/Zip1.png)
1. ダウンロードしたzipファイルを展開します。(cloneした場合は必要ありません)<br>
2. [国土地理院 数値標高モデル](https://fgd.gsi.go.jp/download/menu.php)からデータをダウンロードしてきます。<br>
3. データが入ったzipを展開します。<br>
4．展開したデータをそのまま、`TerrainViewer-master`フォルダの下に移動します。<br>
※なお、アプリを開いた後からでも追加できるので、4は必須ではありません。<br>
![setup2](https://github.com/pto8913/TerrainViewer/blob/images/Zip4.png)<br>
これで、準備が完了しました。<br>

[目次に戻る](#目次)<br>

# 使い方
1. コマンドラインを開く。<br>
**これは自分の環境で確認したことですが、.pyファイルをダブルクリックすれば実行できるっぽいです。できた場合は6まで読み飛ばしてください。** <br> 
<details>
  <summary>コマンドラインの開き方、win10の場合</summary>
  
  ## 一つ目
  ![open cmd1](https://github.com/pto8913/TerrainViewer/blob/images/cmd1-1.png)<br>
  1. `winキー`を押しながら`Rキー`を押します。<br>
  2. 画面上に現れたウィンドウに、`cmd`と入力します。<br>
  3. `ok`を押してください。<br>
  
  ## 二つ目
  ![open cmd2](https://github.com/pto8913/TerrainViewer/blob/images/cmd2-1.png)<br>
  1. スタートを開きます。<br>
  2. スタートを開いた状態で、`cmd`と入力します。<br>
  3. コマンドプロンプトを開いてください。<br>
  ![open cmd2-2](https://github.com/pto8913/TerrainViewer/blob/images/cmd2-2.png)<br>

</details>

2. コマンドラインに`cd ディレクトリへのパス`を入力して、`TerrainViewer-master`フォルダ下に移動します。<br>
3. コマンドラインに`TerrainViewer.py`をドラッグアンドドロップしてください。<br>
![Howtouse3](https://github.com/pto8913/TerrainViewer/blob/images/Howtouse3.png)<br>
4. エンターキーを押して下さい。<br>
5. `TerrainViewer`というウィンドウが開かれます。<br>
![Howtouse5](https://github.com/pto8913/TerrainViewer/blob/images/Howtouse5.png)<br>
6. 地形図を生成したいアイテムがある、フォルダの名前をダブルクリックします。<br>
7. 地形図を生成したいアイテムをクリックして選択します。<br>
![Howtouse7](https://github.com/pto8913/TerrainViewer/blob/images/Howtouse7.png)<br>
8. `Create Terrain`をクリックします。<br>
9. コーヒーを飲んで一休みします。<br>
10. 飲み終わらないうちに、処理が終わり、`Result Images`というタブが追加されます。<br>
そこに処理の結果が保存されています。<br>
![Howtouse10](https://github.com/pto8913/TerrainViewer/blob/images/Howtouse10.png)<br>
11. それらをダブルクリックすると、地形図が表示されます。<br>
![Howtouse10](https://github.com/pto8913/TerrainViewer/blob/images/Howtouse11.png)<br>
12. 面白い地形図を探しましょう!<br>

[目次に戻る](#目次)<br>

# データをウィンドウを開いてから追加する
国土地理院からダウンロードしてきたデータを、ウィンドウを開いた状態で行いたい場合、<br>
ダウンロードしてきたzip形式のフォルダを展開します。 <br>
展開されたフォルダをそのままウィンドウに、ドラッグアンドドロップしてください。<br>  
![Houtouse5.5](https://github.com/pto8913/TerrainViewer/blob/images/Howtouse5.5.png)<br>

[目次に戻る](#目次)<br>

# 動かない
## pythonのダウンロード
そもそも、python3をインストールしていない場合、[公式サイト](https://www.python.org/downloads/)からダウンロードして、インストールを済ませてください。<br>
[Pythonのダウンロードとインストール | Python入門](https://www.javadrive.jp/python/install/index1.html)

## pythonのパスを通す
[環境変数PATHを設定する | Python入門 - Let'sプログラミング](https://www.javadrive.jp/python/install/index3.html)

## モジュールがない
[Pythonのパッケージ管理システムpipの使い方 | note.nkmk.me](https://note.nkmk.me/python-pip-usage/)
