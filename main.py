import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from Menuui import Ui_MainWindow
from io import BytesIO
import requests
from PIL import Image
import sys


class MyMaps(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lon = 50
        self.lat = 50
        self.l = 'map'
        self.ll = [0, 0]
        # Маштаб
        self.cur = 2
        self.spn_list = [
            0,
            0.001,
            0.002,
            0.003,
            0.006,
            0.012,
            0.024,
            0.048,
            0.096,
            0.200,
            0.400,
            0.800,
            1.600,
            3.200
        ]
        self.spn_lon = self.spn_list[self.cur]
        self.spn_lat = self.spn_list[self.cur]
        # Стартовый Запрос
        self.beg_searh = 'Липецк Быханов Сад'
        self.update_on_search(self.beg_searh)
        self.lineEdit.setText(self.beg_searh)
        # Для цели
        self.lon_trg = 0
        self.lat_trg = 0
        self.need_to_show_trg = False
        # Установки
        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_map.clicked.connect(self.set_l_map)
        self.pushButton_sat.clicked.connect(self.set_l_sat)
        self.pushButton_skl.clicked.connect(self.set_l_skl)
        # Внешний вид
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), PyQt5.QtCore.Qt.gray)
        self.setPalette(p)


    def search(self):
        adress = self.lineEdit.text()
        self.update_on_search(adress)

    def update_on_search(self, adress):
        toponym = self.geocode(adress)
        # Обработка ошибок
        if toponym is None:
            return
        # Новые корды
        self.lon, self.lat = self.get_ll_coord(toponym)
        self.set_image()

    def geocode(self, address):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": address,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            return None, None

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        return toponym

    def get_ll_coord(self, toponym):
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        return float(toponym_longitude), float(toponym_lattitude)

    def set_image(self):
        print(self.spn_lon)
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            'll': str(self.lon) + ',' + str(self.lat),
            'l': self.l,
            'spn': str(self.spn_lon) + ',' + str(self.spn_lat),
        }

        response = requests.get(map_api_server, params=map_params)
        if not response:
            print(response.status_code)
            return
        print(response.url)
        img = Image.open(BytesIO(response.content))
        img.save('now_picture.png')
        self.image_label.setPixmap(QtGui.QPixmap('now_picture.png'))

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_PageUp:
            self.cur = max(0, self.cur - 1)
            self.spn_lon = self.spn_list[self.cur]
            self.spn_lat = self.spn_list[self.cur]
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.cur = min(len(self.spn_list) - 1, self.cur + 1)
            self.spn_lon = self.spn_list[self.cur]
            self.spn_lat = self.spn_list[self.cur]
        else:
            event.accept()
            return
        event.accept()
        self.set_image()

    def set_l_map(self):
        self.l = 'map'
        self.set_image()

    def set_l_sat(self):
        self.l = 'sat'
        self.set_image()

    def set_l_skl(self):
        self.l = 'skl'
        self.set_image()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MyMaps()
    ex.show()
    sys.exit(app.exec())
