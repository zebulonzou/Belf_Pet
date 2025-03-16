import os
import sys
import time
from TrayWindow import TrayWindow
from InteractionWindow import InteractionWindow
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QMouseEvent, QIcon

class BelfPet(QWidget):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.current_frame = 0
        self.image_path = r"..\data\images\init"
        self.timer = None
        self.is_clicked = False
        self.is_dragged = False
        self.dragging = False
        self.drag_position = QPoint()
        self.clicked_start_time = 0
        self.loop_duration = 1500
        self.InitUi()
        self.inter_window = InteractionWindow(self)

        self.inter_window.greeting()

    def InitUi(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Belfast")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(500, 500, 200, 200)
        self.setMouseTracking(True)

        self.frames = self.load_images(self.image_path)

        if self.frames:
            self.label = QLabel(self)
            self.label.setFixedSize(self.frames[0].size())
            self.label.setScaledContents(True)  # 自动将图片拉伸填充 label
            self.label.setPixmap(self.frames[self.current_frame])
            self.resize(self.frames[0].width(), self.frames[0].height())

        self.start_timer()

    def load_images(self, images_path):
        frames = []
        screen = QApplication.primaryScreen()
        dpi_x = screen.physicalDotsPerInchX()
        dpi_y = screen.physicalDotsPerInchY()
        target_width = int((6 / 2.54) * dpi_x)
        target_height = int((6 / 2.54) * dpi_y)

        for image_name in sorted(os.listdir(images_path)):
            if image_name.endswith('.png'):
                full_path = os.path.join(images_path, image_name)
                pixmap = QPixmap(full_path)
                scaled_pixmap = pixmap.scaled(target_width, target_height,
                                              Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                frames.append(scaled_pixmap)
        return frames

    def update_action(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.label.setPixmap(self.frames[self.current_frame])
        if self.is_clicked:
            current_time = int(time.time() * 1000)
            if current_time - self.clicked_start_time >= self.loop_duration:
                self.is_clicked = False
                self.frames = self.load_images(r"..\data\images\init")
                self.current_frame = 0
                self.start_timer()

    def sleeping(self):
        self.frames = self.load_images(r"..\data\images\sleeping")
        self.current_frame = 0
        timer = QTimer(self)
        timer.start(1000)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_start_time = int(time.time() * 1000)
            self.is_clicked = True
            self.frames = self.load_images(r"..\data\images\clicked")
            self.current_frame = 0
            self.start_timer()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.is_dragged = True
            self.frames = self.load_images(r"..\data\images\move")
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.inter_window.setVisible(not self.inter_window.isVisible())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.is_dragged = False
            if not self.is_clicked:
                self.frames = self.load_images(r"..\data\images\init")
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.interw_pos()
        if hasattr(self.inter_window, 'greeting_bubble'):
            c = self.geometry().center()
            offset = 72
            gb = self.inter_window.greeting_bubble
            gb.move(c.x() - gb.width() // 2, c.y() + offset - gb.height() // 2)

    def interw_pos(self):
        new_x = self.x() - 100
        new_y = self.y()
        self.inter_window.move(new_x, new_y)

    def greeting(self):
        pass

    def start_timer(self):
        if self.timer is None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_action)
            self.timer.start(240)

    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tray = TrayWindow()
    w = BelfPet()
    w.setWindowIcon(QIcon(r"..\data\images\icon\icon.png"))
    w.show()
    sys.exit(app.exec())

