import os
import json
import random
import sys
from PyQt6.QtWidgets import (QWidget, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMenu)
from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class InteractionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(500, 300, 400, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.option = ["游戏", "动作", "音乐", "退出"]
        self.active_bubbles = []

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.is_paused = False
        self.music_dir = r"..\data\audio\music"

        self.top_widget = QWidget(self)
        self.top_widget.setFixedSize(300, 50)

        self.dialog_box = QComboBox()
        self.dialog_box.setPlaceholderText(" 聊 天 ")
        self.dialog_box.addItems(self.dialog_q())
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.dialog_a)

        topLayout = QHBoxLayout(self.top_widget)
        topLayout.addWidget(self.dialog_box)
        topLayout.addWidget(self.send_button)

        self.bottom_widget = QWidget(self)
        self.bottom_widget.setFixedSize(300, 100)
        self.button_layout = QHBoxLayout(self.bottom_widget)

        self.buttons = {}
        for opt in self.option:
            button = QPushButton(opt)
            self.button_layout.addWidget(button)
            self.buttons[opt] = button

        self.buttons["游戏"].clicked.connect(self.game)
        self.buttons["动作"].clicked.connect(self.actions)
        self.buttons["音乐"].clicked.connect(self.music_player)
        self.buttons["退出"].clicked.connect(os._exit)

        self.top_widget.move(90, -10)
        self.bottom_widget.move(90, 230)

    def dialog_q(self):
        with open("dialog.json", "r", encoding="utf-8") as file:
            self.dialog = json.load(file)
        return list(self.dialog["对话选择"].keys())

    def dialog_a(self):
        try:
            opt = self.dialog_box.currentText()
            branch = getattr(self, 'branch', None)

            if branch:
                if opt in self.dialog["分支对话"][branch]:
                    answers = self.dialog["分支对话"][branch][opt]
                    self.bubble(random.choice(answers))
                    self.dialog_box.clear()
                    self.dialog_box.addItems(list(self.dialog["对话选择"].keys()))
                    del self.branch
            elif opt in self.dialog["对话选择"]:
                dialog_info = self.dialog["对话选择"][opt]
                self.bubble(random.choice(dialog_info["回答"]))

                if "关联分支" in dialog_info:
                    self.branch = dialog_info["关联分支"]
                    branch_q = list(self.dialog["分支对话"][self.branch].keys())
                    self.dialog_box.clear()
                    self.dialog_box.addItems(branch_q)
        except:
            pass

    def greeting(self):
        center = self.parent().geometry().center()
        self.greeting_bubble = BubbleDialog(random.choice(self.dialog["欢迎对话"]["见面"]), center, self)
        self.greeting_bubble.show()

    def game(self):
        menu = QMenu(self)
        menu.addAction("1", lambda: print("待开发"))
        menu.addAction("2", lambda: print("待开发"))
        button = self.buttons["游戏"]
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec(pos)

    def actions(self):
        sender = self.sender()
        menu = QMenu(self)
        menu.addAction("睡觉", lambda: self.parent().sleeping())
        pos = sender.mapToGlobal(sender.rect().bottomLeft())
        menu.exec(pos)


    def music_player(self):
        menu = QMenu(self)
        pause_action = menu.addAction("暂停/播放")
        pause_action.triggered.connect(self.toggle_pause)

        if os.path.exists(self.music_dir):
            for file in os.listdir(self.music_dir):
                if file.lower().endswith((".mp3", ".flac")):
                    action = menu.addAction(file)
                    full_path = os.path.join(self.music_dir, file)
                    action.triggered.connect(
                        lambda _, path=full_path: self.play_music(path)
                    )

        button = self.buttons["音乐"]
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec(pos)

    def play_music(self, file_path):
        url = QUrl.fromLocalFile(file_path)
        self.player.setSource(url)
        self.player.play()
        self.is_paused = False

    def toggle_pause(self):
        if not self.player.source().isLocalFile():
            return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.is_paused = True
        else:
            self.player.play()
            self.is_paused = False


    def bubble(self, text):
        bubble = BubbleDialog(text, self.anchor_point(), self)
        bubble.destroyed.connect(lambda: self.active_bubbles.remove(bubble))
        self.active_bubbles.append(bubble)
        bubble.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        bubble.raise_()  # 确保置顶
        bubble.activateWindow()

    def anchor_point(self):
        return QPoint(self.x() + self.width() // 2, self.y() + 20)

    def moveEvent(self, event):
        super().moveEvent(event)
        new_anchor = self.anchor_point()
        for bubble in self.active_bubbles:
            bubble.update_position(new_anchor)


class BubbleDialog(QWidget):
    def __init__(self, text, anchor_point, parent=None):
        super().__init__(parent)
        self.anchor_point = anchor_point
        self.init_bubble(text)
        self.show_animation()

    def init_bubble(self, text):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.raise_()
        self.activateWindow()

        self.label = QLabel(text)
        self.label.setStyleSheet("""QLabel {background-color: rgba(173, 216, 230, 220);border-radius: 10px;padding: 8px;color: black;min-width: 250px; min-height: 60px;font: 14px Microsoft YaHei;}""")
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.adjust_position()
        QTimer.singleShot(3000, self.close)

    def show_animation(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        self.show()

    def update_position(self, new_anchor):
        self.anchor_point = new_anchor
        self.adjust_position()
        self.repaint()

    def adjust_position(self):
        self.adjustSize()
        x = self.anchor_point.x() - self.width() + 185
        y = self.anchor_point.y() - self.height() + 250
        self.move(x, y)









