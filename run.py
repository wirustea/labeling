from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import start
import login
import os
import address
import json
from Window import Window
from util import compute_completeness,reconnect
from params import labels

class Login(QMainWindow,login.Ui_MainWindow):
    mode = 'login' # 'login','init'
    tasks_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.load_json()
        self.pushButton.clicked.connect(self.check)

        self.delete_button.setDisabled(True)
        self.delete_button.setVisible(False)
        self.submit_button.setDisabled(True)
        self.submit_button.setVisible(False)
        self.data_list_widget.setDisabled(True)
        self.data_list_widget.setVisible(False)
        self.label.setVisible(False)
        self.num_total.setVisible(False)

        self.label_2.setText('')

    def check_user_validate(self):
        if self.config['current_user'] is None:
            return False
        else:
            return True

    def get_current_user_tasks(self):
        if not hasattr(self,'tasks'):
            idx = self.config['names'].index(self.config['current_user'])
            self.tasks = self.config['tasks'][idx]
        return self.tasks

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.pushButton.click()
        elif event.key() == Qt.Key_Delete:
            self.delete_button.click()

    def check(self):
        if self.mode == 'login':
            if self.lineEdit.text() == 'labeling':
                self.label_2.setText('')
                self.config['current_user'] = None
                self.lineEdit.setText('请依次添加参与者姓名')
                self.mode = 'init'
                self.pushButton.setText('添加(enter)')
                self.setGeometry(self.x(),self.y(),self.width(),self.width())
                self.delete_button.setDisabled(False)
                self.delete_button.setVisible(True)
                self.submit_button.setDisabled(False)
                self.submit_button.setVisible(True)
                self.data_list_widget.setDisabled(False)
                self.data_list_widget.setVisible(True)
                self.label.setVisible(True)
                self.num_total.setVisible(True)

                reconnect(self.pushButton.clicked, self.update_date_list)
                reconnect(self.delete_button.clicked, self.delete_data_list)
                reconnect(self.submit_button.clicked, self.submit_data_list)

            else:
                name = self.lineEdit.text()
                if name in self.config['names']:
                    self.label_2.setText('')
                    idx = self.config['names'].index(name)
                    self.tasks = self.config['tasks'][idx]
                    self.config['current_user'] = name
                    self.save_json()
                    self.tasks_signal.emit()
                    self.close()
                else:
                    self.label_2.setText('请输入正确姓名')

    def load_json(self):
        if os.path.exists(address.congif_file_path):
            with open(address.congif_file_path,'r') as f:
                self.config = json.load(f)
                self.reload_data_list(self.config['names'])
        else:
            self.config = {
                'labels':labels,
                'names':[],
                'tasks':[],
                'current_user':None
            }

    def save_json(self):

        with open(address.congif_file_path, 'w') as f:
             json.dump(self.config,f,indent='\t')

    @pyqtSlot()
    def update_date_list(self):
        self.label_2.setText('')
        res = self.lineEdit.text()
        if len(res)>0:
            data = []
            for row in range(self.data_list_widget.rowCount()):
                item = self.data_list_widget.item(row, 0)
                data.append(item.data(0))
            if res in data:
                self.label_2.setText('重复姓名')
                return
            self.lineEdit.clear()
            rowPosition = self.data_list_widget.rowCount()
            self.data_list_widget.insertRow(rowPosition)
            item = QTableWidgetItem(res)
            self.data_list_widget.setItem(rowPosition, 0, item)
            self.data_list_widget.scrollToBottom()
            self.num_total.setText(str(self.data_list_widget.rowCount()))
            data.append(res)
            self.config['names'] = data
            self.save_json()


    def reload_data_list(self,data):
        for d in data:
            rowPosition = self.data_list_widget.rowCount()
            self.data_list_widget.insertRow(rowPosition)
            item = QTableWidgetItem(d)
            self.data_list_widget.setItem(rowPosition, 0, item)
            self.data_list_widget.scrollToBottom()
        self.num_total.setText(str(self.data_list_widget.rowCount()))

    @pyqtSlot()
    def delete_data_list(self):
        selected = set(index.row() for index in self.data_list_widget.selectedIndexes())
        selected = list(selected)
        selected.reverse()
        for it in selected:
            self.data_list_widget.removeRow(it)
        self.num_total.setText(str(self.data_list_widget.rowCount()))
        data = []
        for row in range(self.data_list_widget.rowCount()):
            item = self.data_list_widget.item(row, 0)
            data.append(item.data(0))
        self.config['names'] = data
        self.save_json()

    @pyqtSlot()
    def submit_data_list(self):
        self.reassign_task()
        self.save_json()
        self.close()

    def reassign_task(self):
        num_names = len(self.config['names'])
        self.config['tasks'] = []
        subsets = []
        for i in range(num_names):
            self.config['tasks'].append([])
            subsets.append([])
        if num_names >0:
            sorted_dict = dict(sorted(self.config['labels'].items(), key=lambda item:item[1], reverse=True))
            for t in sorted_dict:
                sum_subsets = [sum(s) for s in subsets]
                min_idx = sum_subsets.index(min(sum_subsets))
                subsets[min_idx].append(sorted_dict[t])
                self.config['tasks'][min_idx].append(t)

    def closeEvent(self, event: QCloseEvent):
        self.reassign_task()
        self.save_json()


class Start(QMainWindow,start.Ui_MainWindow):
    windowisclosing = pyqtSignal()

    block_start = 50
    block_interval = 90
    block_width = 426
    row = 6

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.login = Login()
        self.login.tasks_signal.connect(self.initUI)
        # print(self.login.config)
        if not self.login.check_user_validate():
            self.login.show()
        else:
            self.initUI()

    def initUI(self):
        self.task_list = self.login.get_current_user_tasks()
        self.window = Window(self.windowisclosing)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        if self.check():
            column = len(self.task_list)//self.row +1

            w = self.block_width*column
            h = min(self.block_start+self.block_interval*len(self.task_list)+self.block_start+30,
                    self.block_start+self.block_interval*self.row+30)

            self.resize(w,h)
            self.setGeometry(0,0,w,h)
            self.center()
            self.setMinimumSize(QSize(w,h))
            self.setMaximumSize(QSize(w,h))
            self.image_list = os.listdir(address.image_folder_path)
            for idx,task in enumerate(self.task_list):
                open_button = self.add_block(idx)
                self.connect_open_task_window_with_button(open_button,task)
                if not os.path.exists(address.get_json_file_path(task)):
                    jd = {'label':task, 'finished':[False]* len(self.image_list),
                          'images': [{'name': img_name,'rects':[]} for img_name in self.image_list]}
                    with open(address.get_json_file_path(task), 'w') as f:
                        json.dump(jd, f, indent='\t')

            self.pushButton = QPushButton(self.centralwidget)
            self.pushButton.setGeometry(QRect(
                self.width()-150, self.height()-60, 93, 28))
            self.pushButton.setObjectName("pushButton")
            self.pushButton.setText('切换用户')

            self.compute_completeness()
            self.window.iamclosing.connect(self.restart_start_window)
            self.pushButton.clicked.connect(self.swift_user)

            self.show()

    def center(self):  # 实现窗体在屏幕中央
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def check(self,task=None):
        while not os.path.exists(address.image_folder_path):
            msgBox = QMessageBox()
            msgBox.setWindowTitle('找不到images文件夹')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("当前目录下没有images文件夹,图片应存放于当前目录下images文件夹中")
            msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
            msgBox.setDefaultButton(QMessageBox.Retry)
            reply = msgBox.exec()
            if reply == QMessageBox.Retry:
                continue
            elif reply == QMessageBox.Abort:
                if task:
                    return False
                else:
                    QCoreApplication.quit()
                    break

        if task is not None:
            image_list = set(os.listdir(address.image_folder_path))
            with open(address.get_json_file_path(task), 'r') as f:
                jd = json.load(f)
            list_in_json = set([j['name'] for j in jd['images']])
            while image_list != list_in_json:
                msgBox = QMessageBox()
                msgBox.setWindowTitle('json文件内容不匹配')
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText("images文件夹中的图片与json文件不匹配，忽略将以images文件夹为准修改json文件，这将导致部分标注丢失")
                msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort | QMessageBox.Ignore)
                msgBox.setDefaultButton(QMessageBox.Retry)
                reply = msgBox.exec()
                if reply == QMessageBox.Retry:
                    continue
                elif reply == QMessageBox.Abort:
                    return False
                else:
                    lost = list(image_list - list_in_json)
                    residual = list(list_in_json - image_list)
                    for idx,j in enumerate(jd['images']):
                        if j['name'] in residual:
                            jd['images'].remove(j)
                            del jd['finished'][idx]
                    for l in lost:
                        jd['images'].append({'name':l,'rects':[]})
                        jd['finished'].append(False)
                    with open(address.get_json_file_path(task), 'w') as f:
                        json.dump(jd,f,indent='\t')
                    break
        return True

    def swift_user(self):
        self.close()
        self.login.show()

    def add_block(self,id):
        self.__setattr__('task_' + str(id), QGroupBox(self.centralwidget))
        task = self.__getattribute__('task_' + str(id))
        self.__setattr__('process_' + str(id), QProgressBar(task))
        self.__setattr__('open_' + str(id), QPushButton(task))
        process = self.__getattribute__('process_' + str(id))
        open = self.__getattribute__('open_' + str(id))

        task.setGeometry(QRect(70+self.block_width*(id//self.row), (id%self.row)*self.block_interval+self.block_start, 281, 61))
        task.setObjectName("task_"+str(id))
        process.setGeometry(QRect(20, 30, 151, 16))
        process.setProperty("value", 0)
        process.setTextVisible(True)
        process.setObjectName("process_"+str(id))
        open.setGeometry(QRect(190, 20, 81, 31))
        open.setObjectName("open_"+str(id))

        font = QFont()
        font.setFamily("微软雅黑")
        open.setFont(font)
        open.setText('进入')
        task.setFont(font)
        task.setTitle('任务 '+str(id+1)+' ('+self.task_list[id]+')')
        return open

    def restart_start_window(self):
        self.compute_completeness()
        self.show()

    def connect_open_task_window_with_button(self,button,task):
        button.clicked.connect(lambda: self.open_task_window(task))

    def open_task_window(self,task):
        if self.check(task):
            self.window.initUI(task)
            self.window.show()
            self.close()

    def compute_completeness(self):
        for idx,task in enumerate(self.task_list):
            variable_name = 'process_'+str(idx)
            process = getattr(self,variable_name)

            with open(address.get_json_file_path(task), 'r') as f:
                jd = json.load(f)
                finished,total = compute_completeness(jd)
            process.setMaximum(total)
            process.setValue(finished)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    # login_window = Login()
    # login_window.show()
    # tasks = ['编号','购货单位-名称','购货单位-名称-抬头']
    start = Start()
    # start.show()

    sys.exit(app.exec_())