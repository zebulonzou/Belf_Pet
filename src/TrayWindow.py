import os
import webbrowser
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget, QMenu, QSystemTrayIcon


class TrayWindow(QWidget):
    def __init__(self):
        super().__init__()
        quit = QAction("退出", self, triggered = os._exit)
        setting = QAction("设置", self, triggered =self.setting)
        about = QAction("github", self, triggered= self.About)
        self.tray_menu = QMenu(self)
        self.tray_menu.addAction(about)
        self.tray_menu.addAction(setting)
        self.tray_menu.addAction(quit)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(r"..\data\images\icon\icon.png"))
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()


    def setting(self):
        pass


    def About(self):
        webbrowser.open("https://github.com/zebulonzou/Belf_Pet")