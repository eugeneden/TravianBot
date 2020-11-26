import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QWidget, QComboBox, QLineEdit, \
    QLabel, QGridLayout, QLayoutItem, QSizePolicy, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from api import TravianApi

STATUS_ONLINE = 1
STATUS_OFFLINE = 0


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.api = None
        self.logged_in = False
        self.init_ui()

    def init_ui(self):
        self.statusBar().showMessage('')
        self.setFixedSize(1000, 700)
        self.setWindowTitle('Travian Bot v1.0')
        self.add_toolbar()
        self.build_main()
        self.build_buildings()
        self.build_resources()

        self.show()

    def build_resources(self):
        self.resources_widget = QWidget(self)
        self.resources_widget.hide()
        self.resources_widget.move(0, 60)
        self.resources_widget.resize(1000, 610)
        self.resources_widget.setAutoFillBackground(True)

        label = QLabel('Ресурсы', self.resources_widget)
        label.move(20, 10)

    def build_buildings(self):
        self.buildings_widget = QWidget(self)
        self.buildings_widget.hide()
        self.buildings_widget.move(0, 60)
        self.buildings_widget.resize(1000, 610)
        self.buildings_widget.setAutoFillBackground(True)

        label = QLabel('Центр деревни', self.buildings_widget)
        label.move(20, 10)

    def build_main(self):
        self.main_widget = QWidget(self)
        self.main_widget.hide()
        self.main_widget.move(0, 60)
        self.main_widget.resize(1000, 610)
        self.main_widget.setAutoFillBackground(True)

        servers_label = QLabel('Сервер', self.main_widget)
        servers_label.move(20, 10)

        self.server_combo = QComboBox(self.main_widget)
        self.server_combo.addItem('RU (tx3)', ['ru', 'tx3'])
        self.server_combo.resize(220, 25)
        self.server_combo.move(14, 30)

        self.login = QLineEdit(self.main_widget)
        self.login.setPlaceholderText('Логин')
        self.login.resize(220, 25)
        self.login.move(20, 60)

        self.passw = QLineEdit(self.main_widget)
        self.passw.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.passw.setPlaceholderText('Пароль')
        self.passw.resize(220, 25)
        self.passw.move(20, 90)

        self.race_label = QLabel('Раса: -', self.main_widget)
        self.race_label.move(850, 10)
        self.race_label.setFixedWidth(140)
        # self.status_label = QLabel('Статус: -', self.main_widget)
        # self.status_label.move(850, 30)

        self.login_btn = QPushButton('ОК', self.main_widget)
        self.login_btn.resize(110, 40)
        self.login_btn.move(14, 120)
        self.login_btn.clicked.connect(self.log_in)

        self.logout_btn = QPushButton('Выйти', self.main_widget)
        self.logout_btn.resize(110, 40)
        self.logout_btn.move(14, 120)
        self.logout_btn.clicked.connect(self.log_out)
        self.logout_btn.hide()

    def add_toolbar(self):
        action_params = [
            ('Главная', 'img/a_main.png', self.main),
            ('Ресурсы', 'img/a_resources.png', self.resources),
            ('Центр деревни', 'img/a_buildings.png', self.buildings),
        ]
        tool_bar = QToolBar()
        tool_bar.setMovable(False)
        tool_bar.setIconSize(QSize(48, 48))

        for name, icon, action in action_params:
            _action = QAction(QIcon(icon), name, self)
            _action.triggered.connect(action)
            tool_bar.addAction(_action)

        tool_bar.addSeparator()

        self.village_list = QComboBox()
        self.village_list.setFixedSize(220, 25)
        self.village_list.currentIndexChanged.connect(self.set_current_village)
        tool_bar.addWidget(self.village_list)

        self.addToolBar(tool_bar)

    def set_current_village(self):
        self.api.set_village(self.village_list.currentData())

    def log_out(self):
        self.statusBar().showMessage('')
        try:
            self.api.logout()
            self.set_online_status()
            self.statusBar().showMessage('Успешно')
        except:
            self.statusBar().showMessage('Ошибка выхода с учетной записи!')

    def log_in(self):
        self.statusBar().showMessage('')
        domain, world = self.server_combo.currentData()
        login = self.login.text()
        passw = self.passw.text()

        self.api = TravianApi(login, passw, world, domain)

        try:
            self.api.login()
            self.set_online_status(STATUS_ONLINE)
            self.statusBar().showMessage('Успешно')
        except:
            self.set_online_status(STATUS_OFFLINE)
            self.statusBar().showMessage('Ошибка авторизации!')

    def set_online_status(self, status=STATUS_OFFLINE):
        self.logged_in = bool(status)

        if status == STATUS_OFFLINE:
            self.login.setDisabled(False)
            self.passw.setDisabled(False)
            self.server_combo.setDisabled(False)
            self.login_btn.show()
            self.logout_btn.hide()
            self.village_list.clear()
            self.set_race()
        else:
            self.login.setDisabled(True)
            self.passw.setDisabled(True)
            self.server_combo.setDisabled(True)
            self.login_btn.hide()
            self.logout_btn.show()
            self.get_villages()
            self.set_race()

    def set_race(self):
        if not self.logged_in:
            self.race_label.setText('Раса: -')
            return

        race = self.api.get_race()
        self.race_label.setText('Раса: {}'.format(race))

    def get_villages(self):
        self.village_list.clear()
        for v in self.api.list_villages():
            self.village_list.addItem('{} (ID: {})'.format(v.name, v.id), v.id)

    def main(self):
        self.buildings_widget.hide()
        self.resources_widget.hide()
        self.main_widget.show()

    def resources(self):
        self.main_widget.hide()
        self.buildings_widget.hide()
        self.resources_widget.show()

    def buildings(self):
        self.main_widget.hide()
        self.resources_widget.hide()
        self.buildings_widget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = Main()
    sys.exit(app.exec_())
