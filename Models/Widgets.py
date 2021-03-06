from PyQt5 import QtWidgets

from Designs import valveMapDesign


class ValveMapWidget(QtWidgets.QWidget, valveMapDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valveNumberSelect.valueChanged.connect(self.change_valve_map)

    def change_valve_map(self):
        self.valveValenceTable.setColumnCount(int(self.valveNumberSelect.value()))

    def get_valence_map(self):
        map = []
        for i in range(self.valveValenceTable.columnCount()):
            map.append(int(self.valveValenceTable.item(0, i).text()))

        return map
