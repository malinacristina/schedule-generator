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
import os

corr_plume_pairs = list()
# correlated file
for a in range (53): # for every plume pair in the set
    params = list()
    for i in range(1,3):
        data_path = os.path.join('Z:\working\marinc\Animal experiments\Correlation project\Plumes\DO NOT MOVE\Odour%d_mix_2s' % i, 'plume_%d.mat' % a)
        param = {'plume_pair': a, 'type': 'Plume', 'onset': 0.1, 'offset': 0.1, 'lick_fraction': 0.1, 'shatter_frequency': 500,
                'data_fs': 10000, 'data_path': data_path, 'target_max': 1}
        params.append(param)
    corr_plume_pairs.append(params)

pickle.dump(corr_plume_pairs, open('Corr_pairs.plume', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

# uncorrelated file
uncorr_plume_pairs = list()
for a in range(74): # for every plume pair in the set
    params = list()
    for i in range(1,3):
        data_path = os.path.join('Z:\working\marinc\Animal experiments\Correlation project\Plumes\DO NOT MOVE\Odour%d_50_2s' % i, 'plume_%d.mat' % a)
        param = {'plume_pair': a, 'type': 'Plume', 'onset': 0.1, 'offset': 0.1, 'lick_fraction': 0.1, 'shatter_frequency': 500,
                'data_fs': 10000, 'data_path': data_path, 'target_max': 1}
        params.append(param)
    uncorr_plume_pairs.append(params)
pickle.dump(uncorr_plume_pairs, open('UnCorr_pairs.plume', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


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
#
uncorr_plumes = pickle.Unpickler(open('UnCorr_pairs.plume', 'rb')).load()


print(uncorr_plumes)

print(uncorr_plumes[24][1])

print(uncorr_plumes[5])