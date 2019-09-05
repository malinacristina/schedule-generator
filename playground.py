"""import sys
from PyQt5.QtWidgets import QApplication, QDialog
from ui_imagedialog import Ui_ImageDialog

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_ImageDialog()
ui.setupUi(window)

window.show()
sys.exit(app.exec_())"""
import pickle
import random
#
# plumes = pickle.Unpickler(open('test_pairs.valve', 'rb')).load()
# number_trials = 12
# number_pairs = len(plumes)
# plume_pair_sequence = list()
# i = 0
# j = 0
# for i in range(0,number_trials):
#     plume_pair_sequence.append(j)
#     if j == number_pairs:
#         j = 0
#     else:
#         j += 1
#
# random.shuffle(plume_pair_sequence)
# print(plume_pair_sequence)
#



# plume_pairs = list()
#
# for a in range (1,10):
#     params = list()
#     for i in range(1,3):
#         param = {'type': 'Plume', 'onset': 0.2, 'offset': 0.1, 'lick_fraction': 0.1, 'shatter_frequency': 500,
#                 'data_fs': 10000, 'data_path': 'C:/Users/marinc/OneDrive - The Francis Crick Institute/Imaging/Stimuli/bgnoiseplume_2000ms.mat',
#                 'target_max': i*0.5, 'number': a*10+i}
#         print(param)
#         params.append(param)
#     print(params)
#     plume_pairs.append(params)
# print(plume_pairs)
#
# pickle.dump(plume_pairs, open('test_pairs.valve', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
#
plumes = pickle.Unpickler(open('test_pairs.valve', 'rb')).load()
#
#
print(plumes)

