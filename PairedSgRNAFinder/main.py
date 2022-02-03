import sys
import sgFinder as sf
from PyQt5.QtWidgets import  QMainWindow, QApplication, QTableWidgetItem
import pandas as pd

from gui import Ui_MainWindow
from requests import get
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
        self.pushButton_GetPairs.clicked.connect(self.getPairs)
        self.pushButton_Clear.clicked.connect(self.clear)
        self.pushButton_SaveExcel.clicked.connect(self.saveExcel)
        self.pushButton_SaveCsv.clicked.connect(self.saveCsv)

    def updateLyric(self):
        lyric = getLyric()
        try:
            text = lyric[0] + "\n\n" + "《" + lyric[1] + "》" + " " + lyric[2]
            self.label_Lyric.setText(text)
        except:
            pass

    def getInfo(self):
        self.pam1 = self.lineEdit_PAM.text()
        self.pam2 = self.lineEdit_PAM_2.text()
        self.sequence = self.textEdit_Sequence.toPlainText()
        self.spacerLength1 = self.lineEdit_SpacerLength.text()
        self.spacerLength2 = self.lineEdit_SpacerLength_2.text()
        self.distanceCP1 = self.lineEdit_DistanceCP.text()
        self.distanceCP2 = self.lineEdit_DistanceCP_2.text()


        if self.radioButton_PS.isChecked():
            self.diretion1 = 1
        else:
            self.diretion1 = 0

        if self.radioButton_PS_2.isChecked():
            self.diretion2 = 1
        else:
            self.diretion2 = 0
        self.updateLyric()

    def getPairs(self):
        self.tableWidget_Result.clearContents()
        self.getInfo()
        

        if self.checkBox_cutStrand.isChecked():
            #切割位点在同一链
            sameStrand = 1
        else:
            sameStrand = 0

        dna1 = sf.DNA(self.sequence)
        dna2 = sf.DNA(self.sequence)

        sgRNA1List = dna1.getNonRepeatSg(self.pam1,self.diretion1,self.spacerLength1)
        sgRNA2List = dna2.getNonRepeatSg(self.pam2,self.diretion2,self.spacerLength2)


        def getLocation(sgList,direction,pamLength,distanceCP):
            cutSites = {}
            distanceCP = int(distanceCP)
            pamLength = int(pamLength)
            for i in sgList:
                sg = i
                strand = sgList[i][1][0][1]
                locationSpan = sgList[i][1][0][0]
                #print(locationSpan)

                if direction:#PAM-Spacer
                    cutSite = int(locationSpan[0]) + pamLength + distanceCP
                else:
                    cutSite = int(locationSpan[1]) - pamLength - distanceCP

                cutSites[i] = [cutSite, strand]

            #print(cutSites)
            return cutSites

        sgRNA1CutList = getLocation(sgRNA1List, self.diretion1, len(self.pam1), self.distanceCP1)
        sgRNA2CutList = getLocation(sgRNA2List, self.diretion2, len(self.pam2), self.distanceCP2)

        pairs = {}
        counter = 0
        for i in sgRNA1CutList:

            sg1 = i
            cutSite1 = sgRNA1CutList[i][0]
            strand1 = sgRNA1CutList[i][1]

            for j in sgRNA2CutList:
                sg2 = j
                cutSite2 = sgRNA2CutList[j][0]
                strand2 = sgRNA2CutList[j][1]

                if sameStrand:
                    if strand1 == strand2:
                        distance = abs(cutSite1 - cutSite2)
                    else:
                        distance = False
                else:
                    if strand1 == strand2:
                        distance = False
                    else:
                        distance = abs(cutSite1 - (len(self.sequence) - cutSite2))

                minDistance = int(self.lineEdit_CutDistance_Min.text())
                maxDistance = int(self.lineEdit_CutDistance_Max.text())
                if distance and (minDistance < distance < maxDistance):
                    row = counter * 2
                    counter = counter + 1
                    self.tableWidget_Result.setRowCount(counter*2)
                    name = self.lineEdit_PrimerName.text() + "_" + str(counter) + "_"

                    pairs[name + "F"] = [sg1, distance]
                    self.tableWidget_Result.setItem(row, 0, QTableWidgetItem(name+"F"))
                    self.tableWidget_Result.setItem(row, 1, QTableWidgetItem(sg1))
                    self.tableWidget_Result.setItem(row, 2, QTableWidgetItem(str(distance)))


                    pairs[name + "R"] = [sg2, distance]
                    row = row + 1
                    self.tableWidget_Result.setItem(row, 0, QTableWidgetItem(name + "R"))
                    self.tableWidget_Result.setItem(row, 1, QTableWidgetItem(sg2))
                    self.tableWidget_Result.setItem(row, 2, QTableWidgetItem(str(distance)))

        self.tableWidget_Result.resizeColumnToContents(0)
        self.tableWidget_Result.resizeColumnToContents(1)
        self.result = pd.DataFrame.from_dict(pairs, orient = 'index')
        print(self.result.head())

    def clear(self):
        self.updateLyric()
        self.lineEdit_PrimerName.clear()
        self.textEdit_Sequence.clear()
        self.lineEdit_FileName.clear()
        self.tableWidget_Result.clearContents()

    def saveExcel(self):
        self.updateLyric()
        try:
            FileName = self.lineEdit_FileName.text() + ".xlsx"
            self.result.to_excel(FileName)
            self.lineEdit_FileName.setText("Done! ")
        except Exception as e:
            self.lineEdit_FileName.setText(str(e))

    def saveCsv(self):
        self.updateLyric()
        try:
            csvContent = self.result[[0]]
            FileName = self.lineEdit_FileName.text() + ".csv"
            csvContent.to_csv(FileName)
            self.lineEdit_FileName.setText("Done! ")
        except Exception as e:
            self.lineEdit_FileName.setText(str(e))













        #print(sgRNA2List)



if __name__ == "__main__":
    print('Fuck the world')
    print("loading")
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec())