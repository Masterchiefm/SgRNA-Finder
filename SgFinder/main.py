import sys
import sgFinder as sf

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem

import pandas as pd

from gui import Ui_MainWindow
from Lyric import Lyric as ly
from  requests import  get
import json

def getLyric():
    api = "https://v1.hitokoto.cn/?c=i"
    try:
        a = get(api,timeout=1)
        b = json.loads(a.text)
        c = [str(b["hitokoto"]), str(b["from"]), str(b["from_who"])]
        print(c)
        return c
    except:
        c = ['荒忽兮远望，观流水兮潺湲。', '九歌·湘夫人', '屈原']
        return c


class mainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(mainWindow,self).__init__()


        self.setupUi(self)
        self.pushButton_Clear.clicked.connect(self.clear)
        self.pushButton_GetRepeatSg.clicked.connect(self.getRepeatSgs)
        self.pushButton_GetNonRepearSg.clicked.connect(self.getNonRepeatSgs)
        self.pushButton_Save.clicked.connect(self.save)

    def getInfo(self):
        self.pam = self.lineEdit_PAM.text()
        self.sequence = self.textEdit_Sequence.toPlainText()
        self.spacerLength = self.lineEdit_SpacerLength.text()
        self.repeatNum = self.lineEdit_RepeatNum.text()

        if self.radioButton_PS.isChecked():
            self.diretion = 1
        else:
            self.diretion = 0
        self.updateLyric()




    def clear(self):
        self.textEdit_Sequence.setText("")
        self.lineEdit_FileName.setText("")
        self.tableWidget_Result.clearContents()
        self.updateLyric()

        #self.tableWidget_Result.setHorizontalHeaderLabels(['sgRNA', 'Repeat Num', 'Location(s)'])

        #self.tableWidget_Result.horizontalHeaderItem(0).setText("sgRNA")

    def updateLyric(self):
        lyric = getLyric()
        try:
            text = lyric[0] + "\n\n" + "《" + lyric[1] + "》" + " " + lyric[2]
            self.label_Lyric.setText(text)
        except:
            pass


    def getRepeatSgs(self):

        self.tableWidget_Result.clearContents()
        self.getInfo()
        dna = sf.DNA(self.sequence)
        repeatInfo = dna.getRepeatSg(self.pam,self.diretion,self.spacerLength,self.repeatNum)
        sgList = list(repeatInfo.keys())
        #print(sgList)
        sg = []
        repeat = []
        location = []
        row = 0

        for i in repeatInfo:
            self.tableWidget_Result.setRowCount(row+1)

            newItem = QTableWidgetItem(i)
            self.tableWidget_Result.setItem(row, 0, newItem)
            sg.append(i)

            newItem = QTableWidgetItem(str(repeatInfo[i][0]))

               # setData(Qt.ItemDataRole,int(repeatInfo[i][0]))
            self.tableWidget_Result.setItem(row, 1, newItem)
            repeat.append( repeatInfo[i][0])

            location_text = str( repeatInfo[i][1]).replace("[",'').replace(']','')
            newItem = QTableWidgetItem("Hidden")
            self.tableWidget_Result.setItem(row, 2, newItem)
            location.append(location_text)

            row = row + 1

        self.tableWidget_Result.resizeColumnToContents(0)
        self.tableWidget_Result.resizeColumnToContents(2)
        #self.tableWidget_Result.setSortingEnabled(1)
        #self.tableWidget_Result.sortByColumn(1,Qt.DescendingOrder)

        self.result = pd.DataFrame({'sgRNA': sg, "repeatNum": repeat, "Location": location})
        print(self.result.head())


    def getNonRepeatSgs(self):

        self.tableWidget_Result.clearContents()
        self.getInfo()
        dna = sf.DNA(self.sequence)
        infos = dna.getNonRepeatSg(self.pam,self.diretion,self.spacerLength,self.repeatNum)
        #print(self.diretion)
        sgList = list(infos.keys())
        #print(infos)
        sg = []
        repeat = []
        location = []

        row = 0
        for i in infos:
            self.tableWidget_Result.setRowCount(row+1)

            newItem = QTableWidgetItem(i)
            self.tableWidget_Result.setItem(row, 0, newItem)
            sg.append(i)

            newItem = QTableWidgetItem(str(infos[i][0]))
            self.tableWidget_Result.setItem(row, 1, newItem)
            repeat.append(infos[i][0])

            location_text = str(infos[i][1]).replace("[",'').replace(']','')
            newItem = QTableWidgetItem(location_text)
            self.tableWidget_Result.setItem(row, 2, newItem)
            location.append(location_text)

            row = row + 1
        self.tableWidget_Result.resizeColumnToContents(0)
        self.tableWidget_Result.resizeColumnToContents(2)
        self.result = pd.DataFrame({'sgRNA': sg, "repeatNum": repeat, "Location": location})
        print(self.result.head())

    def save(self):
        self.updateLyric()
        try:
            fileName = self.lineEdit_FileName.text().strip() + ".xlsx"
            self.result.to_excel(fileName)
            self.lineEdit_FileName.setText("Done!")
        except Exception as e:
            self.lineEdit_FileName.setText(str(e))




if __name__ == "__main__":
    print('Fuck the world')
    print("loading")
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec())