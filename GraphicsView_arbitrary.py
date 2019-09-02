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
        self.x2 = 0
        self.y2 = 0
        self.xx0 = 0
        self.xx1 = 0
        self.yy0 = 0
        self.yy1 = 0
        self.oldPos = None
        self.rect = None

        self.MoveMode = 2
        self.FrameMode = 0
        self.SelectMode = 1
        self.temp_line = None
        self.temp_rect = None

        self.mode = 0
        self.flag = 0
        self.move_signal_for_move_mode = 0

        self.oldPos = None
        self.undo_array = []  # [ [0,0],[1,0],[2,1] ]  first:operation batch; second:operation(0:add, 1:delete)
        self.operation_batch = 0
        self.now_state = 0
        self.DeleteOperation = 1
        self.AddOperation = 0
        self.undo_redo_signal = 0

    def mousePressEvent(self, event):

        if event.button() == Qt.MiddleButton:
            self.change_cursor_to_hand()

        if self.mode == self.FrameMode:
            for i in self.painted_rects:
                if i.pen() == self.pen_select:
                    i.setPen(self.pen_framing)
            if event.button() == Qt.RightButton:
                self.change_cursor_to_cross()
                self.flag = 0
                if self.temp_line is not None:
                    self.scene().removeItem(self.temp_line)
                if self.temp_rect is not None:
                    self.scene().removeItem(self.temp_rect)
                if self.rect is not None:
                    self.scene().removeItem(self.rect)
                    self.rect = None
            if event.button() == Qt.LeftButton:
                if self.flag == 0:
                    if self.temp_rect is not None:
                        self.scene().removeItem(self.temp_rect)
                if self.flag == 1:
                    if self.temp_line is not None:
                        self.scene().removeItem(self.temp_line)
        elif self.mode == self.SelectMode:
            if event.button() == Qt.LeftButton:
                item = self.itemAt(event.pos())
                for idx, i in enumerate(self.painted_rects):
                    if item == i:
                        if i.pen() == self.pen_select:
                            i.setPen(self.pen_framing)
                        else:
                            i.setPen(self.pen_select)
        elif self.mode == self.MoveMode:
            if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
                self.oldPos = event.pos()
                self.move_signal_for_move_mode = 1

    def mouseReleaseEvent(self, event):
        pos = self.mapToScene(event.pos())
        if self.mode == self.FrameMode:
            if event.button() == Qt.LeftButton:
                if self.flag ==0:
                    self.change_cursor_to_size()
                    self.flag =2
                    self.x0 = pos.x()
                    self.y0 = pos.y()
                elif self.flag == 2:

                    self.x1 = pos.x()
                    self.y1 = pos.y()
                    self.x2 = self.x1
                    self.y2 = self.y1
                    self.flag -= 1
                elif self.flag == 1:
                    self.change_cursor_to_cross()
                    self.x2 = pos.x()
                    self.y2 = pos.y()
                    self.flag -=1
        elif self.mode == self.MoveMode:
            if event.button() == Qt.MiddleButton:
                if self.flag>0:
                    self.change_cursor_to_size()
                else:
                    self.change_cursor_to_cross()
                self.move_signal_for_move_mode = 0
            elif event.button() == Qt.LeftButton:
                self.move_signal_for_move_mode = 0

    def wheelEvent(self, event: QWheelEvent):
        zoomInFactor = 1.06
        zoomOutFactor = 1 / zoomInFactor
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

    def mouseMoveEvent(self, event):

        super().mouseMoveEvent(event)
        if self.mode == self.FrameMode:
            if self.flag ==2:
                pos = self.mapToScene(event.pos())
                self.x1, self.y1= pos.x(), pos.y()
            elif self.flag ==1:
                pos = self.mapToScene(event.pos())
                self.x2, self.y2 = pos.x(), pos.y()
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
        if self.flag == 2:
            self.line1 = QGraphicsLineItem(self.x0,self.y0,self.x1,self.y1)
            self.line1.setPen(self.pen_select)
            if self.temp_line is not None:
                self.scene().removeItem(self.temp_line)
            self.scene().addItem(self.line1)
            self.temp_line = self.line1
        elif self.flag ==1:

            c = [self.x2,self.y2]
            ab = [self.x1-self.x0,self.y1-self.y0]
            ac = [self.x2-self.x0,self.y2-self.y0]
            l2_ab = (ab[0]**2 + ab[1]**2)**0.5
            if l2_ab ==0:
                self.flag = 0
                return

            d = (ab[0]*ac[0]+ab[1]*ac[1])/l2_ab
            self.xx0 = c[0] - d*(ab[0]/l2_ab)
            self.yy0 = c[1] - d * (ab[1] / l2_ab)

            self.xx1 = self.xx0+ab[0]
            self.yy1 = self.yy0+ab[1]


            self.rect = QGraphicsPolygonItem(QPolygonF([
                QPointF(self.x0,self.y0),
                QPointF(self.x1, self.y1),
                QPointF(self.xx1, self.yy1),
                QPointF(self.xx0, self.yy0)
            ]))
            self.rect.setPen(self.pen_select)
            self.scene().removeItem(self.temp_line)
            if self.temp_rect is not None:
                self.scene().removeItem(self.temp_rect)
            self.scene().addItem(self.rect)
            self.temp_rect = self.rect

    def clear_rects(self):
        self.refresh_undo_array()
        self.operation_batch += 1
        self.now_state += 1
        for idx, rect in enumerate(self.painted_rects):
            self.scene().removeItem(rect)
            self.undo_array[idx] = [self.operation_batch, self.DeleteOperation]

        self.save_to_json()
        self.refresh_completeness_signal.emit()
        if self.temp_line is not None:
            self.scene().removeItem(self.temp_line)
        if self.temp_rect is not None:
            self.scene().removeItem(self.temp_rect)
        if self.rect is not None:
            self.scene().removeItem(self.rect)
            self.rect = None

    def parse_image(self, image_path):
        self.painted_rects = []
        self.undo_array = []
        self.now_state = 0
        self.operation_batch = 0
        self.image = QPixmap(image_path)
        # thickness = self.image.width() // 1000
        thickness=2
        self.pen_framing = QPen(Qt.red, thickness, Qt.SolidLine)
        self.pen_select = QPen(Qt.blue, thickness, Qt.DotLine)
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(image_path))
        self.rect = None
        self.temp_rect = None
        self.temp_line = None

        rects = []
        for idx, image in enumerate(self.jd['images']):
            if image['name'] == os.path.split(image_path)[-1]:
                if 'rects' in image:
                    rects = image['rects']
                    self.idx = idx
                break
        for r in rects:
            rect = QGraphicsPolygonItem(QPolygonF([
                QPointF(*r[0]),
                QPointF(*r[1]),
                QPointF(*r[2]),
                QPointF(*r[3])
            ]))
            rect.setPen(self.pen_framing)
            self.painted_rects.append(rect)
            self.undo_array.append([self.operation_batch, self.AddOperation])
            scene.addItem(rect)

        self.setScene(scene)

    def add_rects(self):
        points = []
        if self.rect is not None:
            for i in range(4):
                point = self.rect.polygon().at(i).toPoint()
                points.append((point.x(),point.y()))
            # a = np.array(points[0])
            # b = np.array(points[1])
            # c = np.array(points[2])
            # ab = b -a
            # bc = c -b
            # s = np.linalg.norm(ab)*np.linalg.norm(bc)
            ab = [points[1][0] - points[0][0], points[1][1] - points[0][1]]
            bc = [points[2][0] - points[1][0], points[2][1] - points[1][1]]
            s = (ab[0]**2 + ab[1]**2)**0.5 * (bc[0]**2 + bc[1]**2)**0.5

            if s>10:

                if self.flag == 1:
                    self.flag = 0
                    self.change_cursor_to_cross()

                self.refresh_undo_array()
                self.operation_batch += 1
                self.now_state += 1
                # rotated_rect =
                # self.shot = self.image.copy(rotated_rect)
                self.painted_rects.append(self.rect)
                self.undo_array.append([self.operation_batch,self.AddOperation])

                self.rect.setPen(self.pen_framing)
                self.scene().removeItem(self.temp_rect)
                self.scene().addItem(self.rect)
                self.temp_rect = None
                self.save_to_json()
                # self.refresh_completeness_signal.emit()
                self.rect = None
                self.refresh_completeness_signal.emit()
                return True
            else:
                return False

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
            if self.temp_line is not None:
                self.scene().removeItem(self.temp_line)
            if self.temp_rect is not None:
                self.scene().removeItem(self.temp_rect)
            if self.rect is not None:
                self.scene().removeItem(self.rect)
                self.rect = None

    def redo(self):
        pass

    def delete(self):
        self.refresh_undo_array()
        self.operation_batch += 1
        self.now_state += 1
        for idx, rect in enumerate(self.painted_rects):
            if rect.pen() == self.pen_select:
                rect.setPen(self.pen_framing)
                self.scene().removeItem(rect)
                self.undo_array[idx] = [self.operation_batch, self.DeleteOperation]
        self.save_to_json()
        self.refresh_completeness_signal.emit()

    def _get_fine_tune_rect(self,rect,mode,step):

        mid = -1
        mx = 10000
        tid = -1
        ty = 10000
        for i in range(4):
            if mx > rect.polygon().value(i).x():
                mx = rect.polygon().value(i).x()
                mid = i
        for i in range(4):
            if ty >= rect.polygon().value(i).x() and i!=mid:
                ty = rect.polygon().value(i).x()
                tid = i
        if rect.polygon().value(mid).x() > rect.polygon().value(tid).x():
            right_up = mid
            left_up = tid
        else:
            right_up = tid
            left_up = mid

        if (left_up + 1) % 4 == right_up:
            right_down = (right_up + 1) % 4
            left_down = (right_down + 1) % 4
        else:
            left_down = (left_up + 1) % 4
            right_down = (left_down + 1) % 4

        def vector(i, j):
            x = rect.polygon().value(j).x() - rect.polygon().value(i).x()
            y = rect.polygon().value(j).y() - rect.polygon().value(i).y()
            return (x, y)

        def vector_length(v):
            x = v[0]
            y = v[1]
            length = (x ** 2 + y ** 2) ** 0.5
            return length

        def vector_mul(v, i):
            return (v[0] * i, v[1] * i)

        def unit_vector(v):
            length = vector_length(v)
            return (v[0] / length, v[1] / length)

        def get_head_point(v, p):
            x = rect.polygon().value(p).x() + v[0]
            y = rect.polygon().value(p).y() + v[1]
            return x, y

        if mode == 'a':  # up
            left_up_vector = vector(left_up, left_down)
            new_left_up_vector = vector_mul(unit_vector(left_up_vector), step)
            new_left_up_pointf = get_head_point(new_left_up_vector, left_up)

            right_up_vector = vector(right_up, right_down)
            new_right_up_vector = vector_mul(unit_vector(right_up_vector), step)
            new_right_up_pointf = get_head_point(new_right_up_vector, right_up)

            new_rect = QGraphicsPolygonItem(QPolygonF([
                QPointF(*new_left_up_pointf),
                QPointF(*new_right_up_pointf),
                rect.polygon().value(right_down),
                rect.polygon().value(left_down)
            ]))

        elif mode == 'd':  # down
            left_down_vector = vector(left_down, left_up)
            new_left_down_vector = vector_mul(unit_vector(left_down_vector), step)
            new_left_down_pointf = get_head_point(new_left_down_vector, left_down)

            right_down_vector = vector(right_down, right_up)
            new_right_down_vector = vector_mul(unit_vector(right_down_vector), step)
            new_right_down_pointf = get_head_point(new_right_down_vector, right_down)

            new_rect = QGraphicsPolygonItem(QPolygonF([
                QPointF(*new_left_down_pointf),
                QPointF(*new_right_down_pointf),
                rect.polygon().value(right_up),
                rect.polygon().value(left_up)
            ]))

        elif mode == 'w':  # left

            if rect.polygon().value(mid).y() < rect.polygon().value(tid).y():
                left_up_vector = vector(left_up, right_up)
                new_left_up_vector = vector_mul(unit_vector(left_up_vector), step)
                new_left_up_pointf = get_head_point(new_left_up_vector, left_up)

                lift_down_vector = vector(left_down, right_down)
                new_left_down_vector = vector_mul(unit_vector(lift_down_vector), step)
                new_left_down_pointf = get_head_point(new_left_down_vector, left_down)

                new_rect = QGraphicsPolygonItem(QPolygonF([
                    QPointF(*new_left_up_pointf),
                    QPointF(*new_left_down_pointf),
                    rect.polygon().value(right_down),
                    rect.polygon().value(right_up)
                ]))
            else:
                right_up_vector = vector(right_up, left_up)
                new_right_up_vector = vector_mul(unit_vector(right_up_vector), step)
                new_right_up_pointf = get_head_point(new_right_up_vector, right_up)

                right_down_vector = vector(right_down, left_down)
                new_right_down_vector = vector_mul(unit_vector(right_down_vector), step)
                new_right_down_pointf = get_head_point(new_right_down_vector, right_down)

                new_rect = QGraphicsPolygonItem(QPolygonF([
                    QPointF(*new_right_up_pointf),
                    QPointF(*new_right_down_pointf),
                    rect.polygon().value(left_down),
                    rect.polygon().value(left_up)
                ]))

        else:  # right
            if rect.polygon().value(mid).y() <= rect.polygon().value(tid).y():
                right_up_vector = vector(right_up, left_up)
                new_right_up_vector = vector_mul(unit_vector(right_up_vector), step)
                new_right_up_pointf = get_head_point(new_right_up_vector, right_up)

                right_down_vector = vector(right_down, left_down)
                new_right_down_vector = vector_mul(unit_vector(right_down_vector), step)
                new_right_down_pointf = get_head_point(new_right_down_vector, right_down)

                new_rect = QGraphicsPolygonItem(QPolygonF([
                    QPointF(*new_right_up_pointf),
                    QPointF(*new_right_down_pointf),
                    rect.polygon().value(left_down),
                    rect.polygon().value(left_up)
                ]))
            else:
                left_up_vector = vector(left_up, right_up)
                new_left_up_vector = vector_mul(unit_vector(left_up_vector), step)
                new_left_up_pointf = get_head_point(new_left_up_vector, left_up)

                lift_down_vector = vector(left_down, right_down)
                new_left_down_vector = vector_mul(unit_vector(lift_down_vector), step)
                new_left_down_pointf = get_head_point(new_left_down_vector, left_down)

                new_rect = QGraphicsPolygonItem(QPolygonF([
                    QPointF(*new_left_up_pointf),
                    QPointF(*new_left_down_pointf),
                    rect.polygon().value(right_down),
                    rect.polygon().value(right_up)
                ]))
        return new_rect

    def fine_tune(self,mode,step=-1):
        if isinstance(self.rect,QGraphicsPolygonItem):
            new_rect = self._get_fine_tune_rect(self.rect, mode, step)
            new_rect.setPen(self.pen_select)
            self.scene().removeItem(self.rect)
            self.rect = new_rect
            self.scene().addItem(self.rect)
            self.save_to_json()
            return

        new_rects = []
        for idx, rect in enumerate(self.painted_rects):
            if rect.pen() == self.pen_select:
                rect.setPen(self.pen_framing)
                self.scene().removeItem(rect)

                new_rect = self._get_fine_tune_rect(rect,mode,step)

                new_rect.setPen(self.pen_select)
                rect.setPen(self.pen_select)
                new_rects.append([idx,new_rect])
                self.scene().addItem(new_rect)

        for i,rect in new_rects:
            self.painted_rects[i] = rect

        self.save_to_json()

    def save_to_json(self):
        rects = []
        for idx, qrectf in enumerate(self.painted_rects):
            if self.undo_array[idx][1] != self.DeleteOperation and self.undo_array[idx][0] <= self.now_state \
                    and self.undo_array[idx][0] >= 0:
                points = []
                for i in range(4):
                    point = qrectf.polygon().at(i).toPoint()
                    points.append((point.x(), point.y()))
                rects.append(points)
        self.jd['images'][self.idx]['rects'] = rects

    def refresh_undo_array(self):
        if self.undo_redo_signal == 1:
            for idx,i in enumerate(self.undo_array):
                if i[0]>self.now_state:
                    self.undo_array[idx][0] = -1
            self.undo_redo_signal = 0
            self.operation_batch = self.now_state

    def setJsonDict(self, jd):
        self.jd = jd

    def change_cursor_to_arrow(self):
        self.mode = self.SelectMode
        self.viewport().setProperty("cursor",QCursor(Qt.ArrowCursor))

    def change_cursor_to_cross(self):
        self.mode = self.FrameMode
        self.viewport().setProperty("cursor", QCursor(Qt.CrossCursor))

    def change_cursor_to_hand(self):
        if self.mode == self.FrameMode:
            self.mode = self.MoveMode
            self.viewport().setProperty("cursor", QCursor(Qt.ClosedHandCursor))

    def change_cursor_to_size(self):
        self.mode = self.FrameMode
        self.viewport().setProperty("cursor", QCursor(Qt.SizeAllCursor))
