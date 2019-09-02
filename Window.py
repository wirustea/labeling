from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import gui
import os
from GraphicsView_arbitrary import GraphicsView
import address
import json
import reference
import util

class Reference(QMainWindow, reference.Ui_MainWindow):
    '''
    this is reference window, show where to label
    '''
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def set_reference_image(self,label):
        self.label.setPixmap(QPixmap(address.get_sample_image(label)).scaled(
            self.label.width(), self.label.height()))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.close()


class Window(QMainWindow, gui.Ui_MainWindow):
    '''
    this is work space main window
    '''
    def __init__(self,close_signal):
        super().__init__()
        self.setupUi(self)
        self.iamclosing = close_signal
        self.reference_window = Reference()

        logo = QPixmap(os.path.join(address.sample_folder_path,'logo.png')).scaled(self.logo.width(),self.logo.height())
        self.logo.setPixmap(logo)

        self.label = GraphicsView(self.centralwidget)
        self.label.setGeometry(QRect(257, 20, 871, 588))
        self.label.setBackgroundBrush(QColor(100,100,100))
        self.label.setAutoFillBackground(True)
        self.label.viewport().setProperty("cursor",QCursor(Qt.CrossCursor))
        self.label.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.label.setDragMode(QGraphicsView.NoDrag)
        self.label.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.label.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.label.setObjectName("graphicsView")

        self.sample_label = QLabel(self)
        self.sample_label.setGeometry(QRect(257, 20, 871, 588))
        font = QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(40)
        self.sample_label.setFont(font)
        self.sample_label.setLayoutDirection(Qt.LeftToRight)
        self.sample_label.setAlignment(Qt.AlignCenter)

        self.clear.clicked.connect(self.label.clear_rects)
        self.label.refresh_completeness_signal.connect(self.restore_finished_with_warning)
        self.finished_and_next_image_buttton.clicked.connect(self.finished_and_next_image)
        self.warning_button.clicked.connect(self.finished_with_warning)
        self.reference.clicked.connect(self.open_reference)
        self.previous.clicked.connect(self.previous_image)
        self.next.clicked.connect(self.next_labeled_image)

    def initUI(self,label):
        self.class_label = label
        self.label.initUI()
        self.load_image_list()

        self.setWindowTitle(label)
        self.sample_label.setPixmap(QPixmap(address.get_sample_image(label)).scaled(
            self.sample_label.width(), self.sample_label.height()))
        self.reference_window.set_reference_image(label)
        self.label.setDisabled(True)
        self.label.setVisible(False)
        self.sample_label.setVisible(True)
        self.clear.setDisabled(True)
        self.start_signal = False
        self.warning_button.setVisible(False)
        self.warning_button.setDisabled(True)
        self.next.setDisabled(True)
        self.previous.setDisabled(True)
        self.finished_and_next_image_buttton.setDisabled(False)
        self.finished_and_next_image_buttton.setText('开始')
        util.reconnect(self.finished_and_next_image_buttton.clicked, self.finished_and_next_image)
        self.completeness.setText('Sample')

        self.finished_signal = False

    @pyqtSlot()
    def open_reference(self):
        '''
        open reference window
        :return: None
        '''
        self.reference_window.show()

    def closeEvent(self, event: QCloseEvent):
        self.save_json()
        self.iamclosing.emit()
        self.close()

    def keyPressEvent(self, event):
        if (event.modifiers() & Qt.ShiftModifier) and (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return):
            # next unlabeled image
            if self.warning_button.isVisible():
                self.warning_button.click()
            else:
                self.finished_and_next_image_buttton.click()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            # affirm select box
            self.label.add_rects()
        elif (event.modifiers() & Qt.ShiftModifier) and (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_Z:
            self.label.redo()
        elif event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier):
            self.label.undo()

        elif event.key() == Qt.Key_W and (event.modifiers() & Qt.ControlModifier):
            self.label.fine_tune('w',1)
        elif event.key() == Qt.Key_S and (event.modifiers() & Qt.ControlModifier):
            self.label.fine_tune('s',1)
        elif event.key() == Qt.Key_A and (event.modifiers() & Qt.ControlModifier):
            self.label.fine_tune('a',1)
        elif event.key() == Qt.Key_D and (event.modifiers() & Qt.ControlModifier):
            self.label.fine_tune('d',1)

        elif event.key() == Qt.Key_W:
            self.label.fine_tune('w')
        elif event.key() == Qt.Key_S:
            self.label.fine_tune('s')
        elif event.key() == Qt.Key_A:
            self.label.fine_tune('a')
        elif event.key() == Qt.Key_D:
            self.label.fine_tune('d')

        elif event.key() == Qt.Key_Control:
            self.label.change_cursor_to_arrow()
        elif event.key() == Qt.Key_Alt:
            self.label.change_cursor_to_hand()
        elif event.key() == Qt.Key_Delete:
            self.label.delete()
        elif event.key() == Qt.Key_F1:
            self.reference.click()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control or event.key() == Qt.Key_Alt:
            self.label.change_cursor_to_cross()

    def load_image_list(self):
        '''
        load image list from folder located in address.images_folder_path
        :return: None
        '''
        self.image_list = os.listdir(address.image_folder_path)
        self.pointer = -1
        self.browse_pointer = -1

        #create json
        with open(address.get_json_file_path(self.class_label), 'r') as f:
            self.jd = json.load(f)

        self.label.setJsonDict(self.jd)
        self.compute_completeness()

    def next_image(self,dont_next = False):
        '''
        next unlabeled image, update pointer and load what it indicates
        :param dont_next: if dont_next is True, just reload current image
        :return: None
        '''
        if not self.start_signal:
            self.label.setDisabled(False)
            self.clear.setDisabled(False)
            self.label.setVisible(True)
            self.sample_label.setVisible(False)
            # self.previous.setEnabled(True)
            self.start_signal = True
            self.finished_and_next_image_buttton.setText('完成！下一张\n(shift+enter)')
        self.save_json()

        if dont_next:
            self.parse_image(self.pointer)
            return

        while self.pointer+1 < len(self.image_list):
            self.pointer += 1
            if self.jd['finished'][self.pointer] == False:
                self.parse_image(self.pointer)
                self.browse_pointer = self.pointer
                if not self.previous.isEnabled() and self.browse_pointer > 0:
                    self.previous.setEnabled(True)
                return
        self.finished()

    def finished(self):
        '''
        when this task is finished, run this function to update interface to finished state, include next_iimage button
        or label's image
        :return: None
        '''
        self.finished_signal=True
        if not self.previous.isEnabled():
            self.previous.setEnabled(True)
        self.finished_and_next_image_buttton.setText('退出')
        util.reconnect(self.finished_and_next_image_buttton.clicked,self.close)
        self.label.setVisible(False)
        self.label.setDisabled(True)
        self.sample_label.clear()
        self.sample_label.setText('Accomplished!')
        self.sample_label.setVisible(True)
        self.pointer=len(self.jd['finished'])

    def unfinished(self):
        '''
        when check the labeled images, use this function to cancel finished state
        :return: None
        '''
        self.finished_signal = False
        self.label.setVisible(True)
        self.label.setDisabled(False)
        self.sample_label.clear()
        self.sample_label.setVisible(False)

    def finished_and_next_image(self):
        '''
        current image labeling is finished, swift to next unlabeled image
        :return: None
        '''
        if self.start_signal:
            if self.browse_pointer == self.pointer:
                if len(self.jd['images'][self.pointer]['rects']) == 0:
                    self.warning_button.setVisible(True)
                    self.warning_button.setDisabled(False)
                    self.finished_and_next_image_buttton.setDisabled(True)
                    self.finished_and_next_image_buttton.setVisible(False)
                    self.compute_completeness()
                    return
                else:
                    self.jd['finished'][self.pointer] = True
            else:
                self.browse_pointer = self.pointer
                self.next_image(dont_next=True)
                self.next.setDisabled(True)
                self.previous.setEnabled(True)
                self.compute_completeness()
                return

        self.next_image()
        self.browse_pointer = self.pointer
        self.compute_completeness()

    def finished_with_warning(self):
        '''
        when this labeling has no selected box, then this function will run to update finished_and_next button
        :return: None
        '''
        self.jd['finished'][self.pointer] = True
        self.warning_button.setVisible(False)
        self.warning_button.setDisabled(True)
        self.finished_and_next_image_buttton.setDisabled(False)
        self.finished_and_next_image_buttton.setVisible(True)
        self.next_image()
        self.browse_pointer = self.pointer
        self.compute_completeness()

    def restore_finished_with_warning(self):
        '''
        anti-operation of finished_with warning function
        :return: None
        '''
        if self.warning_button.isVisible():
            self.warning_button.setVisible(False)
            self.warning_button.setDisabled(True)
            self.finished_and_next_image_buttton.setDisabled(False)
            self.finished_and_next_image_buttton.setVisible(True)

    def previous_image(self):
        '''
        browse to previous image
        :return: None
        '''
        if self.browse_pointer == len(self.jd['finished']):
            self.unfinished()
        if not self.start_signal:
            self.label.setDisabled(False)
            self.clear.setDisabled(False)
            self.label.setVisible(True)
            self.sample_label.setVisible(False)
            self.start_signal = True
        self.save_json()
        if self.browse_pointer!=0:
            self.browse_pointer -= 1
            self.parse_image(self.browse_pointer)
        if self.browse_pointer==0:
            self.previous.setDisabled(True)
        if self.browse_pointer <self.pointer:
            self.next.setDisabled(False)
        self.compute_completeness()

    def next_labeled_image(self):
        '''
        browse to next labeled image, if next image is not labeled, this button will disabled.
        :return:
        '''
        if not self.start_signal:
            self.label.setDisabled(False)
            self.clear.setDisabled(False)
            self.label.setVisible(True)
            self.sample_label.setVisible(False)
            self.start_signal = True
        self.save_json()
        if self.browse_pointer<self.pointer:
            self.browse_pointer += 1
            if self.browse_pointer == self.pointer and self.pointer == len(self.jd['finished']):
                self.finished()
            else:
                self.parse_image(self.browse_pointer)
        if self.browse_pointer==self.pointer:
            self.next.setDisabled(True)
        if self.browse_pointer>0:
            self.previous.setEnabled(True)
        self.compute_completeness()

    def parse_image(self,pointer):
        '''
        parse image to label widget
        :param pointer: index
        :return: None
        '''
        file_name = self.image_list[pointer]
        self.label.parse_image(os.path.join(address.image_folder_path, file_name))

    def save_json(self):
        with open(address.get_json_file_path(self.class_label),'w') as f:
            json.dump(self.jd,f,indent='\t')

    @pyqtSlot()
    def compute_completeness(self):
        total = len(self.jd['finished'])
        finished = self.browse_pointer
        if finished < total:
            self.completeness.setText(str(finished+1)+'/'+str(total))
        else:
            self.completeness.setText('---')