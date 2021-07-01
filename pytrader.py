import sys
from PyQt5.QtCore import *
from Kiwoom import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from widgetfile import *
from PyQt5 import QtCore, QtGui, QtWidgets
import time
from pandas_datareader import data
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mplfinance.original_flavor import candlestick2_ohlc
from datetime import datetime
import matplotlib.ticker as ticker
import os
import plotly.graph_objects as go
import tkinter as tk
from tkinter import ttk
from IPython.display import display
form_class = uic.loadUiType("pytrader.ui")[0]

start_date = datetime(2020,5,8)
end_date = datetime(2020,10,8)

dialog = tk.Tk()
dialog1 = tk.Tk()
dialog2 = tk.Tk()

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.trade_stocks_done = False

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        self.timer2 = QTimer(self)
        self.timer2.start(1000 *10)
        self.timer2.timeout.connect(self.timeout2)

        accouns_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")

        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox.addItems(accounts_list)

        self.lineEdit.textChanged.connect(self.code_changed)
        self.pushButton.clicked.connect(self.send_order)
        self.pushButton_2.clicked.connect(self.check_balance)
        self.pushButton_4.clicked.connect(self.show_graph)
        self.pushButton_5.clicked.connect(self.dialog_open)
        self.pushButton_6.clicked.connect(self.dialog_open1)
        self.pushButton_7.clicked.connect(self.dialog_open2)


       # 차트확인하기 버튼
        self.button = QPushButton('차트 확인',self)
        self.button.clicked.connect(self.chart)
       #self.button.clicked.connect(self.show_graph)
        self.button.setGeometry(105,239,75,23)
        self.chart = QDialog()
        self.canvas = FigureCanvas(Figure())


        self.load_buy_sell_list()

    def dialog_open(self):

        label = ttk.Label(dialog, text="현재 날짜를 기준으로 과거 거래 일 별로 시가, 고가, 저가, 종가, 거래량을 가져와 특정 거래일의 거래량이 평균 거래량보다 25% 초과시 매매하는 알고리즘")
        label.pack()
        dialog.title("급등주")
        #self.dialog.geometry("300x300")
        label.mainloop()

    # def change_test(self):
    #     change_label.configure(text="text change")
    #     change_button

    def dialog_open1(self):
        label1 = ttk.Label(dialog1,
                          text="상위 20개의 종목을 추천하여 매수할 수 있도록 하는 알고리즘")
        label1.pack()
        dialog.title("신마법공식")
        # self.dialog.geometry("300x300")
        label1.mainloop()

    def dialog_open2(self):

        label2 = ttk.Label(dialog2,
                          text="과거의 데이터를 가지고 와 알고리즘 스스로 반복해 공부하여 향후 해당 주가에 대한 예측을 하는 알고리즘")
        label2.pack()
        dialog.title("주가예측")
        # self.dialog.geometry("300x300")
        label2.mainloop()

    def show_graph(self):
        code = self.lineEdit.text()
        self.fig = plt.figure(figsize=(20, 10))
        df1 = data.DataReader(code + ".ks", "yahoo")
        ax = self.fig.add_subplot(111)
        df1['MA20'] = df1['Adj Close'].rolling(window=20).mean()
        df1['MA60'] = df1['Adj Close'].rolling(window=60).mean()
        self.graph_viewer.canvas.axes.plot(df1.index, df1['Adj Close'], label='Adj Close')
        self.graph_viewer.canvas.axes.plot(df1.index, df1['MA20'], label='MA20')
        self.graph_viewer.canvas.axes.plot(df1.index, df1['MA60'], label='MA60')

        data_name = '이동평균선'
        #self.graph_viewer.canvas.axes.plot(x_list, y_list, label=data_name)
        self.graph_viewer.canvas.axes.legend()
        self.graph_viewer.canvas.axes.set_xlabel('Date')
        self.graph_viewer.canvas.axes.set_ylabel('주가')
        self.graph_viewer.canvas.draw()


    def chart(self):
        self.chart.setGeometry(600, 200, 1200, 600)
        self.chart.setWindowTitle("PyChart Viewer v0.1")
        self.chart.setWindowIcon(QIcon('icon.png'))

        self.chart.lineEdit = QLineEdit()
        self.chart.button1 = QPushButton("차트그리기")
        self.chart.button1.clicked.connect(self.ButtonClicked)

        self.chart.button2 = QPushButton("유동성차트 확인")
        self.chart.button2.clicked.connect(self.ButtonClicked1)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.chart.button1)
        rightLayout.addWidget(self.chart.button2)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.chart.setLayout(layout)
        self.chart.show()

    def ButtonClicked1(self):
        code = self.lineEdit.text()
        df = data.DataReader(code + ".ks", "yahoo")
        candle = go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'])
        fig = go.Figure(data=candle)
        fig.show()

    def ButtonClicked(self):
        code = self.lineEdit.text()
        df = data.DataReader(code + ".ks", "yahoo")
        df['MA20'] = df['Adj Close'].rolling(window=20).mean()
        df['MA60'] = df['Adj Close'].rolling(window=60).mean()

        ax = self.fig.add_subplot(111)
        """ax.plot(df.index, df['Adj Close'], label='Adj Close')
        ax.plot(df.index, df['MA20'], label='MA20')
        ax.plot(df.index, df['MA60'], label='MA60')"""
        ax.legend(loc='upper right')
        candlestick2_ohlc(ax, df['Open'], df['High'],
                          df['Low'], df['Close'],
                          width=0.5, colorup='r', colordown='b')
        ax.set_title('KOSPI INDEX', fontsize=22)
        ax.set_xlabel('Date')
        ax.grid()
        plt.pause(0.001)
        self.canvas.draw()





    def closeEvent(self, event):

        self.deleteLater()

    def trade_stocks(self):
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        f = open("buy_list.txt", 'rt', encoding='utf-8')
        buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", 'rt', encoding='utf-8')
        sell_list = f.readlines()
        f.close()

        # account
        account = self.comboBox.currentText()

        # buy list
        for row_data in buy_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매수전':
                self.kiwoom.send_order("send_order_req", "0101", account, 1, code, num, price, hoga_lookup[hoga], "")

        # sell list
        for row_data in sell_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매도전':
                self.kiwoom.send_order("send_order_req", "0101", account, 2, code, num, price, hoga_lookup[hoga], "")

        # buy list
        for i, row_data in enumerate(buy_list):
            buy_list[i] = buy_list[i].replace("매수전", "주문완료")

        # file update
        f = open("buy_list.txt", 'w', encoding='utf-8')
        for row_data in buy_list:
            f.write(row_data)
        f.close()

        # sell list
        for i, row_data in enumerate(sell_list):
            sell_list[i] = sell_list[i].replace("매도전", "주문완료")

        # file update
        f = open("sell_list.txt", 'w', encoding='utf-8')
        for row_data in sell_list:
            f.write(row_data)
        f.close()

    def load_buy_sell_list(self):
        f = open("buy_list.txt", 'rt', encoding='utf-8')
        buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", 'rt', encoding='utf-8')
        sell_list = f.readlines()
        f.close()

        row_count = len(buy_list) + len(sell_list)
        self.tableWidget_4.setRowCount(row_count)

        # buy list
        for j in range(len(buy_list)):
            row_data = buy_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rsplit())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_4.setItem(j, i, item)

        # sell list
        for j in range(len(sell_list)):
            row_data = sell_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rstrip())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_4.setItem(len(buy_list) + j, i, item)

        self.tableWidget_4.resizeRowsToContents()

    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kiwoom.get_master_code_name(code)
        self.lineEdit_2.setText(name)

    def send_order(self):
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()
        code = self.lineEdit.text()
        hoga = self.comboBox_3.currentText()
        num = self.spinBox.value()
        price = self.spinBox_2.value()

        self.kiwoom.send_order("send_order_req", "0101", account, order_type_lookup[order_type], code, num, price, hoga_lookup[hoga], "")

    def timeout(self):
        market_start_time = QTime(9, 0, 0)
        current_time = QTime.currentTime()

        if current_time > market_start_time and self.trade_stocks_done is False:
            self.trade_stocks()
            self.trade_stocks_done = True

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

    def timeout2(self):
        if self.checkBox.isChecked():
            self.check_balance()

    def check_balance(self):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            time.sleep(0.05)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.tableWidget.setItem(0, i, item)

        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()

    def closeEvent(self, event):

         self.deleteLater()



if __name__ == "__main__":
     app = QApplication(sys.argv)
     myWindow = MyWindow()
     myWindow.show()
     sys.exit(app.exec())
     window = MWindow()