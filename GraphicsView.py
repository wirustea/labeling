from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

class GraphicsView(QGraphicsView):
    refresh_completeness_signal = pyqtSignal()

    def __init__(self,father):
        super().__init__(father)
        self.initUI()
          # thickness depends on picture's size

    def initUI(self,thickness=2):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.flag = False
        self.rect = None
        self.shot = None
        self.painted_rects = []
        self.temp_rect =None
        self.start = False
        self.image = None
        self.idx = 0
        self.pen1 = QPen(Qt.gray, 2, Qt.DotLine)
        self.pen2 = QPen(Qt.red, 2, Qt.SolidLine)
        self.pen3 = QPen(Qt.blue, 2, Qt.DotLine)
        self.mode = 0 # 0:framing  1:select  2:move
        self.FrameMode = 0
        self.SelectMode = 1
        self.MoveMode = 2
        self.move_signal_for_move_mode = 0
        self.oldPos = None
        self.undo_array = []   # [ [0,0],[1,0],[2,1] ]  first:operation batch; second:operation(0:add, 1:delete)
        self.operation_batch = 0
        self.now_state = 0
        self.DeleteOperation = 1
        self.AddOperation = 0
        self.undo_redo_signal = 0

    def mousePressEvent(self, event):

        if event.button() == Qt.MiddleButton:
            self.change_cursor_to_hand()

        if self.mode == self.FrameMode:
            if event.button() == Qt.LeftButton:
                #清空选择
                for i in self.painted_rects:
                    if i.pen() == self.pen3:
                        i.setPen(self.pen2)

                pos = self.mapToScene(event.pos())
                self.flag = True
                self.start = True
                self.x0 = pos.x()
                self.y0 = pos.y()
                self.scene().update()
        elif self.mode == self.SelectMode:
            if event.button() == Qt.LeftButton:
                item = self.itemAt(event.pos())
                for idx, i in enumerate(self.painted_rects):
                    if item == i:
                        if i.pen() == self.pen3:
                            i.setPen(self.pen2)
                        else:
                            i.setPen(self.pen3)
        elif self.mode == self.MoveMode:
            if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
                self.oldPos = event.pos()
                self.move_signal_for_move_mode = 1

    def mouseReleaseEvent(self, event):
        if self.mode == self.FrameMode:
            if event.button() == Qt.LeftButton:
                pos = self.mapToScene(event.pos())
                self.flag = False
                self.start = False
                self.x1 = pos.x()
                self.y1 = pos.y()
                self.rect = QGraphicsRectItem(float(min(self.x0, self.x1)), float(min(self.y0, self.y1)),
                                              float(abs(self.x1 - self.x0)), float(abs(self.y1 - self.y0)))

        elif self.mode == self.SelectMode:
            pass
        elif self.mode == self.MoveMode:
            if event.button() == Qt.MiddleButton:
                self.change_cursor_to_cross()
                self.move_signal_for_move_mode = 0
            elif event.button() == Qt.LeftButton:
                self.move_signal_for_move_mode = 0

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.mode == self.FrameMode:
            if self.flag:
                self.start = False
                pos = self.mapToScene(event.pos())
                self.x1 = pos.x()
                self.y1 = pos.y()
                self.scene().update()
        elif self.mode == self.MoveMode:
            if self.move_signal_for_move_mode == 1:
                newPos = event.pos()
                delta = self.oldPos - newPos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())
                self.oldPos = newPos

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        self.rect = QGraphicsRectItem(float(min(self.x0, self.x1)), float(min(self.y0, self.y1)),
                      float(abs(self.x1 - self.x0)), float(abs(self.y1 - self.y0)))
        self.rect.setPen(self.pen1)

        if self.flag:
            if not self.start:
                if self.temp_rect is not None:
                    self.scene().removeItem(self.temp_rect)
                self.scene().addItem(self.rect)
                self.temp_rect = self.rect
            else:
                if self.temp_rect is not None:
                    self.scene().removeItem(self.temp_rect)

    def wheelEvent(self, event: QWheelEvent):
        zoomInFactor = 1.06
        zoomOutFactor = 1 / zoomInFactor
        # oldPos = self.mapToScene(event.pos())
        oldPos = event.pos()
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor

        self.scale(zoomFactor, zoomFactor)
        # newPos = self.mapToScene(event.pos())
        newPos = event.pos()
        delta = newPos - oldPos
        # self.translate(delta.x(), delta.y())
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())

    def parse_image(self,image_path):
        self.painted_rects = []
        self.undo_array = []
        self.now_state = 0
        self.operation_batch = 0
        self.image = QPixmap(image_path)
        thickness = self.image.width()//400
        self.pen1 = QPen(Qt.blue, thickness, Qt.DotLine)
        self.pen2 = QPen(Qt.red, thickness, Qt.SolidLine)
        self.pen3 = QPen(Qt.blue, thickness, Qt.DotLine)
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(image_path))

        if image_path.split('.')[0] != 'sample':
            rects = []
            for idx,image in enumerate(self.jd['images']):
                if image['name'] == os.path.split(image_path)[-1]:
                    if 'rects' in image:
                        rects=image['rects']
                        self.idx = idx
                    break

            for r in rects:
                rect = QGraphicsRectItem(QRectF(*r))
                rect.setPen(self.pen2)
                self.painted_rects.append(rect)
                self.undo_array.append([self.operation_batch,self.AddOperation])
                scene.addItem(rect)

        self.setScene(scene)

    def add_rects(self):
        if self.rect.rect().height()*self.rect.rect().width()>0:
            self.refresh_undo_array()
            self.operation_batch += 1
            self.now_state += 1
            rect = self.rect.rect().toAlignedRect()
            self.shot = self.image.copy(rect)
            self.painted_rects.append(self.rect)
            self.undo_array.append([self.operation_batch,self.AddOperation])

            self.rect.setPen(self.pen2)

            self.scene().removeItem(self.temp_rect)
            self.scene().addItem(self.rect)
            self.save_to_json()
            self.refresh_completeness_signal.emit()
            return True
        else:
            return False

    def undo(self):

        if self.now_state>0:
            for idx,i in enumerate(self.painted_rects):
                if self.undo_array[idx][0]==self.now_state:
                    if self.undo_array[idx][1] == self.DeleteOperation:
                        self.scene().addItem(i)
                    else:
                        self.scene().removeItem(i)
            self.now_state -=1
            self.save_to_json()
            self.refresh_completeness_signal.emit()
            self.undo_redo_signal=1

    def redo(self):
        if self.now_state <self.operation_batch:
            for idx,i in enumerate(self.painted_rects):
                if self.undo_array[idx][0]==self.now_state:
                    if self.undo_array[idx][1] != self.DeleteOperation:
                        self.scene().addItem(i)
                    else:
                        self.scene().removeItem(i)
            self.now_state += 1
            self.save_to_json()
            self.refresh_completeness_signal.emit()
            self.undo_redo_signal = 1

    def clear_rects(self):
        self.refresh_undo_array()
        self.operation_batch += 1
        self.now_state +=1
        for idx, rect in enumerate(self.painted_rects):
            self.scene().removeItem(rect)
            self.undo_array[idx] = [self.operation_batch, self.DeleteOperation]

        self.save_to_json()
        self.refresh_completeness_signal.emit()

    def delete(self):
        self.refresh_undo_array()
        self.operation_batch += 1
        self.now_state += 1
        for idx,rect in enumerate(self.painted_rects):
            if rect.pen() == self.pen3:
                rect.setPen(self.pen2)
                self.scene().removeItem(rect)
                self.undo_array[idx] = [self.operation_batch,self.DeleteOperation]
        self.save_to_json()
        self.refresh_completeness_signal.emit()

    def save_to_json(self):
        rects = []
        for idx,qrectf in enumerate(self.painted_rects):
            if self.undo_array[idx][1] != self.DeleteOperation and self.undo_array[idx][0]<=self.now_state \
                    and self.undo_array[idx][0]>=0:
                rect = qrectf.rect().toAlignedRect().getRect()
                rects.append(rect)
        self.jd['images'][self.idx]['rects'] = rects

    def refresh_undo_array(self):
        if self.undo_redo_signal == 1:
            for idx,i in enumerate(self.undo_array):
                if i[0]>self.now_state:
                    self.undo_array[idx][0] = -1
            self.undo_redo_signal = 0
            self.operation_batch = self.now_state


    def setJsonDict(self,jd):
        self.jd = jd

    def change_cursor_to_arrow(self):
        self.mode = 1
        self.viewport().setProperty("cursor",QCursor(Qt.ArrowCursor))

    def change_cursor_to_cross(self):
        self.mode = 0
        self.viewport().setProperty("cursor", QCursor(Qt.CrossCursor))

    def change_cursor_to_hand(self):
        if self.mode == 0:
            self.mode = 2
            self.viewport().setProperty("cursor", QCursor(Qt.ClosedHandCursor))
