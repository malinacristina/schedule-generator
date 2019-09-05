from PyQt5 import QtWidgets
import numpy as np
import random
import os
import pickle

from Designs import simpleCorrDesign, corrDesign, simpleGNGDesign, pretrainDesign, shatterValveTestDesign, \
    corrRandomFrequencyDesign, corrRandomFrequency2Design, corrDifficultySwitchDesign, DistanceGNGDesign, \
    DistanceGNGRandomSwapDesign, DistanceRobotGNGDesign, SimpleGNGPlumesDesign, SimpleGNGVariableOnsetDesign, \
    PretrainPlumeBgDesign, GNGPlumeBgDesign, GNGPlumeBgDesign, GNGPlumeBgDelaysDesign, \
    DistanceTaskOnsetJitterDesign, DistanceTrainingDesign, DistanceTraining2Design, CorrelationGNGNaturalPlumesDesign,\
    CorrelationGNGNaturalPlumes2Design


from Generation import Gen


class PretrainWidget(QtWidgets.QWidget, pretrainDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        target = int(self.targetEdit.text())

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        schedule = []
        for t in range(n_trials):
            valve = np.random.choice(valve_index[target], 1) + 1
            schedule.append([1, valve, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Valve', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        valve = trial[1]
        valence_map = trial[2]

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': False,
                     'fromValues': True,
                     'pulse_width': length,
                     'pulse_delay': 0.0,
                     'fromLength': False,
                     'fromRepeats': True,
                     'repeats': 0,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': trial[3]}

            if p + 1 in valve:
                param['repeats'] = 1

            params.append(param)

        return params


class SimpleGNGWidget(QtWidgets.QWidget, simpleGNGDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        if not bool(self.reverseValenceCheck.isChecked()):
            rewarded_choice = valve_index[1]
            unrewarded_choice = valve_index[2]
        else:
            rewarded_choice = valve_index[2]
            unrewarded_choice = valve_index[1]

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                valve = np.random.choice(rewarded_choice, 1) + 1
            else:
                valve = np.random.choice(unrewarded_choice, 1) + 1

            schedule.append([reward_sequence[t], valve, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Valve', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        valve = trial[1]
        valence_map = trial[2]

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': False,
                     'fromValues': True,
                     'pulse_width': length,
                     'pulse_delay': 0.0,
                     'fromLength': False,
                     'fromRepeats': True,
                     'repeats': 0,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': trial[3]}

            if p + 1 in valve:
                param['repeats'] = 1

            params.append(param)

        return params


class SimpleCorrWidget(QtWidgets.QWidget, simpleCorrDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials + n_control_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        frequency = float(self.pulseFrequencyEdit.text())
        sp_correlated = bool(self.spCorrelatedCheck.isChecked())

        schedule = []
        for t in range(n_trials + n_control_trials):
            # set correlation
            if sp_correlated:
                correlated = True if reward_sequence[t] == 1 else False
            else:
                correlated = False if reward_sequence[t] == 1 else True

            if t < n_trials:
                o1_valve = np.random.choice(valve_index[1], 1) + 1
                o2_valve = np.random.choice(valve_index[2], 1) + 1
                b_valves = np.random.choice(valve_index[0], 2, replace=False) + 1
            else:
                o1_valve = np.random.choice(valve_index[3], 1) + 1
                o2_valve = np.random.choice(valve_index[2], 1) + 1
                b_valves = np.hstack((np.random.choice(valve_index[0], 1)[0] + 1, np.random.choice(valve_index[4], 1)[0] + 1))

            schedule.append([reward_sequence[t], correlated, o1_valve, o2_valve, b_valves, frequency, valence_map,
                             lick_fraction])

        return schedule, ['Rewarded', 'Correlated', 'Odour 1 Valve', 'Odour 2 Valves', 'Blank Valves', 'Frequency',
                          'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        correlated = trial[1]
        o1_valve = trial[2]
        o2_valve = trial[3]
        b_valves = trial[4]
        frequency = trial[5]
        valence_map = trial[6]

        anti_phase_offset = (1.0 / frequency) * 0.5
        phase_choice = np.random.randint(0, 2)

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': True,
                     'frequency': frequency,
                     'duty': 0.5,
                     'fromLength': True,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'phase_chop': True,
                     'chop_amount': 0.25,
                     'lick_fraction': trial[7]}

            # is this an odour 1 valve
            if p + 1 in o1_valve:
                param['length'] = length
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * phase_choice

            # is this an odour 2 valve
            if p + 1 in o2_valve:
                param['length'] = length
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)

            # is this a blank valve
            if p + 1 in b_valves:
                param['length'] = length
                if correlated:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)
                else:
                    param['onset'] += anti_phase_offset * np.where(b_valves == p + 1)[0][0]

            params.append(param)

        return params


class CorrWidget(QtWidgets.QWidget, corrDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials + n_control_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        frequency = float(self.pulseFrequencyEdit.text())
        sp_correlated = bool(self.spCorrelatedCheck.isChecked())

        schedule = []
        for t in range(n_trials + n_control_trials):
            # set correlation
            if sp_correlated:
                correlated = True if reward_sequence[t] == 1 else False
            else:
                correlated = False if reward_sequence[t] == 1 else True

            simple_choice = np.random.uniform() > float(self.fractionSimpleTrialsEdit.text())

            if t < n_trials:
                o1_choice = valve_index[1]
                o2_choice = valve_index[2]
                b_choice = valve_index[0]
            else:
                simple_choice = True
                o1_choice = valve_index[3]
                o2_choice = valve_index[2]
                b_choice = np.hstack((valve_index[4], np.random.choice(valve_index[0], 1)))

            if simple_choice:
                # for a simple choice we will always need 1 o1, 1 o2 valves and 2 b valves all at 50% open
                o1_valve = np.random.choice(o1_choice, 1, replace=False) + 1
                o1_contributions = [0.5]

                o2_valve = np.random.choice(o2_choice, 1, replace=False) + 1
                o2_contributions = [0.5]

                b_valve = np.random.choice(b_choice, 2, replace=False) + 1
                b_contributions = [0.5, 0.5]
            # otherwise there are some differences according to correlation structure
            else:
                # can be made up of random combination of 1 or 2 valves, b valve contrs. add to 1
                o1_valve = np.random.choice(o1_choice, np.random.randint(1, len(o1_choice) + 1), replace=False) + 1
                o1_contributions = np.round(np.random.dirichlet(np.ones(len(o1_valve))) * 0.5, 2)

                o2_valve = np.random.choice(o2_choice, np.random.randint(1, 3), replace=False) + 1
                o2_contributions = np.round(np.random.dirichlet(np.ones(len(o2_valve))) * 0.5, 2)

                if correlated:
                    # if correlated we want our blank valves to add to 1 + we always need 2 valves
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))), 2)
                else:
                    # else they must add to 0.5
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))) * 0.5, 2)

            schedule.append([reward_sequence[t], correlated, o1_valve, o1_contributions, o2_valve, o2_contributions,
                             b_valve, b_contributions, frequency, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Correlated', 'Odour 1 Valve', 'O1 Contributions', 'Odour 2 Valves',
                          'O2 Contributions', 'Blank Valves', 'B Contributions', 'Frequency',
                          'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_hz = float(self.shatterHzEdit.text())
        correlated = trial[1]
        o1_valve = trial[2]
        o1_contr = trial[3]
        o2_valve = trial[4]
        o2_contr = trial[5]
        b_valve = trial[6]
        b_contr = trial[7]
        frequency = trial[8]
        valence_map = trial[9]

        anti_phase_offset = (1.0 / frequency) * 0.5
        phase_choice = np.random.randint(0, 2)

        for p in range(len(valence_map)):
            param = {'type': 'RandomNoise',
                     'fromDuty': True,
                     'frequency': frequency,
                     'duty': 0.5,
                     'fromLength': True,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'phase_chop': True,
                     'lick_fraction': trial[10],
                     'shadow': False,
                     'shatter_frequency': shatter_hz,
                     'target_duty': 0.5,
                     'amp_min': 0.0,
                     'amp_max': 1.0}

            # is this an odour 1 valve
            if p + 1 in o1_valve:
                param['length'] = length
                param['target_duty'] = o1_contr[np.where(o1_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * phase_choice

            # is this an odour 2 valve
            if p + 1 in o2_valve:
                param['length'] = length
                param['target_duty'] = o2_contr[np.where(o2_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)

            # is this a blank valve
            if p + 1 in b_valve:
                param['length'] = length
                param['target_duty'] = b_contr[np.where(b_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)
                else:
                    if param['target_duty'] != 0.5:
                        param['shadow'] = True
                    else:
                        param['onset'] += anti_phase_offset * np.where(b_valve == p + 1)[0][0]

            params.append(param)

        return params


class CorrDifficultySwitchWidget(QtWidgets.QWidget, corrDifficultySwitchDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials + n_control_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        frequency_low = float(self.pulseLowFrequencyEdit.text())
        frequency_high = float(self.pulseHighFrequencyEdit.text())
        sp_correlated = bool(self.spCorrelatedCheck.isChecked())

        schedule = []
        for t in range(n_trials + n_control_trials):
            # set correlation
            if sp_correlated:
                correlated = True if reward_sequence[t] == 1 else False
            else:
                correlated = False if reward_sequence[t] == 1 else True

            simple_choice = np.random.uniform() > float(self.fractionSimpleTrialsEdit.text())

            if t < n_trials:
                o1_choice = valve_index[1]
                o2_choice = valve_index[2]
                b_choice = valve_index[0]
            else:
                simple_choice = True
                o1_choice = valve_index[3]
                o2_choice = valve_index[2]
                b_choice = np.hstack((valve_index[4], np.random.choice(valve_index[0], 1)))

            if simple_choice:
                # for a simple choice we will always need 1 o1, 1 o2 valves and 2 b valves all at 50% open
                o1_valve = np.random.choice(o1_choice, 1, replace=False) + 1
                o1_contributions = [0.5]

                o2_valve = np.random.choice(o2_choice, 1, replace=False) + 1
                o2_contributions = [0.5]

                b_valve = np.random.choice(b_choice, 2, replace=False) + 1
                b_contributions = [0.5, 0.5]
            # otherwise there are some differences according to correlation structure
            else:
                # can be made up of random combination of 1 or 2 valves, b valve contrs. add to 1
                o1_valve = np.random.choice(o1_choice, np.random.randint(1, len(o1_choice) + 1), replace=False) + 1
                o1_contributions = np.round(np.random.dirichlet(np.ones(len(o1_valve))) * 0.5, 2)

                o2_valve = np.random.choice(o2_choice, np.random.randint(1, 3), replace=False) + 1
                o2_contributions = np.round(np.random.dirichlet(np.ones(len(o2_valve))) * 0.5, 2)

                if correlated:
                    # if correlated we want our blank valves to add to 1 + we always need 2 valves
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))), 2)
                else:
                    # else they must add to 0.5
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))) * 0.5, 2)

            frequency = np.random.choice([frequency_low, frequency_high], 1)[0]

            schedule.append([reward_sequence[t], correlated, o1_valve, o1_contributions, o2_valve, o2_contributions,
                             b_valve, b_contributions, frequency, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Correlated', 'Odour 1 Valve', 'O1 Contributions', 'Odour 2 Valves',
                          'O2 Contributions', 'Blank Valves', 'B Contributions', 'Frequency',
                          'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_hz = float(self.shatterHzEdit.text())
        correlated = trial[1]
        o1_valve = trial[2]
        o1_contr = trial[3]
        o2_valve = trial[4]
        o2_contr = trial[5]
        b_valve = trial[6]
        b_contr = trial[7]
        frequency = trial[8]
        valence_map = trial[9]

        anti_phase_offset = (1.0 / frequency) * 0.5
        phase_choice = np.random.randint(0, 2)

        for p in range(len(valence_map)):
            param = {'type': 'RandomNoise',
                     'fromDuty': True,
                     'frequency': frequency,
                     'duty': 0.5,
                     'fromLength': True,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'phase_chop': True,
                     'lick_fraction': trial[10],
                     'shadow': False,
                     'shatter_frequency': shatter_hz,
                     'target_duty': 0.5,
                     'amp_min': 0.0,
                     'amp_max': 1.0}

            # is this an odour 1 valve
            if p + 1 in o1_valve:
                param['length'] = length
                param['target_duty'] = o1_contr[np.where(o1_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * phase_choice

            # is this an odour 2 valve
            if p + 1 in o2_valve:
                param['length'] = length
                param['target_duty'] = o2_contr[np.where(o2_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)

            # is this a blank valve
            if p + 1 in b_valve:
                param['length'] = length
                param['target_duty'] = b_contr[np.where(b_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)
                else:
                    if param['target_duty'] != 0.5:
                        param['shadow'] = True
                    else:
                        param['onset'] += anti_phase_offset * np.where(b_valve == p + 1)[0][0]

            params.append(param)

        return params


class CorrRandomisedFrequencyWidget(QtWidgets.QWidget, corrRandomFrequencyDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials + n_control_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        cycle_min = float(self.cycleLengthLowerEdit.text())
        cycle_max = float(self.cycleLengthUpperEdit.text())
        sp_correlated = bool(self.spCorrelatedCheck.isChecked())

        schedule = []
        for t in range(n_trials + n_control_trials):
            # choose frequency
            cycle_choice = np.random.uniform(cycle_min, cycle_max)
            frequency = int(1000.0 / cycle_choice)
            print(frequency)

            # set correlation
            if sp_correlated:
                correlated = True if reward_sequence[t] == 1 else False
            else:
                correlated = False if reward_sequence[t] == 1 else True

            simple_choice = np.random.uniform() > float(self.fractionSimpleTrialsEdit.text())

            if t < n_trials:
                o1_choice = valve_index[1]
                o2_choice = valve_index[2]
                b_choice = valve_index[0]
            else:
                simple_choice = True
                o1_choice = valve_index[3]
                o2_choice = valve_index[2]
                b_choice = np.hstack((valve_index[4], np.random.choice(valve_index[0], 1)))

            if simple_choice:
                # for a simple choice we will always need 1 o1, 1 o2 valves and 2 b valves all at 50% open
                o1_valve = np.random.choice(o1_choice, 1, replace=False) + 1
                o1_contributions = [0.5]

                o2_valve = np.random.choice(o2_choice, 1, replace=False) + 1
                o2_contributions = [0.5]

                b_valve = np.random.choice(b_choice, 2, replace=False) + 1
                b_contributions = [0.5, 0.5]
            # otherwise there are some differences according to correlation structure
            else:
                # can be made up of random combination of 1 or 2 valves, b valve contrs. add to 1
                o1_valve = np.random.choice(o1_choice, np.random.randint(1, len(o1_choice) + 1), replace=False) + 1
                o1_contributions = np.round(np.random.dirichlet(np.ones(len(o1_valve))) * 0.5, 2)

                o2_valve = np.random.choice(o2_choice, np.random.randint(1, 3), replace=False) + 1
                o2_contributions = np.round(np.random.dirichlet(np.ones(len(o2_valve))) * 0.5, 2)

                if correlated:
                    # if correlated we want our blank valves to add to 1 + we always need 2 valves
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))), 2)
                else:
                    # else they must add to 0.5
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))) * 0.5, 2)

            schedule.append([reward_sequence[t], correlated, o1_valve, o1_contributions, o2_valve, o2_contributions,
                             b_valve, b_contributions, frequency, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Correlated', 'Odour 1 Valve', 'O1 Contributions', 'Odour 2 Valves',
                          'O2 Contributions', 'Blank Valves', 'B Contributions', 'Frequency',
                          'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_hz = float(self.shatterHzEdit.text())
        correlated = trial[1]
        o1_valve = trial[2]
        o1_contr = trial[3]
        o2_valve = trial[4]
        o2_contr = trial[5]
        b_valve = trial[6]
        b_contr = trial[7]
        frequency = trial[8]
        valence_map = trial[9]

        anti_phase_offset = (1.0 / frequency) * 0.5
        phase_choice = np.random.randint(0, 2)

        for p in range(len(valence_map)):
            param = {'type': 'RandomNoise',
                     'fromDuty': True,
                     'frequency': frequency,
                     'duty': 0.5,
                     'fromLength': True,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'phase_chop': True,
                     'lick_fraction': trial[10],
                     'shadow': False,
                     'shatter_frequency': shatter_hz,
                     'target_duty': 0.5,
                     'amp_min': 0.0,
                     'amp_max': 1.0}

            # is this an odour 1 valve
            if p + 1 in o1_valve:
                param['length'] = length
                param['target_duty'] = o1_contr[np.where(o1_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * phase_choice

            # is this an odour 2 valve
            if p + 1 in o2_valve:
                param['length'] = length
                param['target_duty'] = o2_contr[np.where(o2_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)

            # is this a blank valve
            if p + 1 in b_valve:
                param['length'] = length
                param['target_duty'] = b_contr[np.where(b_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)
                else:
                    if param['target_duty'] != 0.5:
                        param['shadow'] = True
                    else:
                        param['onset'] += anti_phase_offset * np.where(b_valve == p + 1)[0][0]

            params.append(param)

        return params


class CorrRandomisedFrequency2Widget(QtWidgets.QWidget, corrRandomFrequency2Design.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials + n_control_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        hz_min = int(self.hzLowerEdit.text())
        hz_max_band_1 = int(self.hzUpperBand1Edit.text())
        hz_max_band_2 = int(self.hzUpperBand2Edit.text())
        hz_max_band_3 = int(self.hzUpperBand3Edit.text())
        sp_correlated = bool(self.spCorrelatedCheck.isChecked())

        schedule = []
        for t in range(n_trials + n_control_trials):
            # choose frequency
            band_choice = np.random.uniform(0, 1)
            if band_choice < 0.75:
                hz_band = range(hz_min, hz_max_band_1)
            elif 0.75 <= band_choice < 0.95:
                hz_band = range(hz_max_band_1, hz_max_band_2)
            else:
                hz_band = range(hz_max_band_2, hz_max_band_3)

            frequency = np.random.choice(hz_band)

            # set correlation
            if sp_correlated:
                correlated = True if reward_sequence[t] == 1 else False
            else:
                correlated = False if reward_sequence[t] == 1 else True

            simple_choice = np.random.uniform() > float(self.fractionSimpleTrialsEdit.text())

            if t < n_trials:
                o1_choice = valve_index[1]
                o2_choice = valve_index[2]
                b_choice = valve_index[0]
            else:
                simple_choice = True
                o1_choice = valve_index[3]
                o2_choice = valve_index[2]
                b_choice = np.hstack((valve_index[4], np.random.choice(valve_index[0], 1)))

            if simple_choice:
                # for a simple choice we will always need 1 o1, 1 o2 valves and 2 b valves all at 50% open
                o1_valve = np.random.choice(o1_choice, 1, replace=False) + 1
                o1_contributions = [0.5]

                o2_valve = np.random.choice(o2_choice, 1, replace=False) + 1
                o2_contributions = [0.5]

                b_valve = np.random.choice(b_choice, 2, replace=False) + 1
                b_contributions = [0.5, 0.5]
            # otherwise there are some differences according to correlation structure
            else:
                # can be made up of random combination of 1 or 2 valves, b valve contrs. add to 1
                o1_valve = np.random.choice(o1_choice, np.random.randint(1, len(o1_choice) + 1), replace=False) + 1
                o1_contributions = np.round(np.random.dirichlet(np.ones(len(o1_valve))) * 0.5, 2)

                o2_valve = np.random.choice(o2_choice, np.random.randint(1, 3), replace=False) + 1
                o2_contributions = np.round(np.random.dirichlet(np.ones(len(o2_valve))) * 0.5, 2)

                if correlated:
                    # if correlated we want our blank valves to add to 1 + we always need 2 valves
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))), 2)
                else:
                    # else they must add to 0.5
                    b_valve = np.random.choice(b_choice, 2, replace=False) + 1

                    b_contributions = np.array([1.0, 0.0])
                    while np.prod(b_contributions) == 0:
                        b_contributions = np.round(np.random.dirichlet(np.ones(len(b_valve))) * 0.5, 2)

            schedule.append([reward_sequence[t], correlated, o1_valve, o1_contributions, o2_valve, o2_contributions,
                             b_valve, b_contributions, frequency, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Correlated', 'Odour 1 Valve', 'O1 Contributions', 'Odour 2 Valves',
                          'O2 Contributions', 'Blank Valves', 'B Contributions', 'Frequency',
                          'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_hz = float(self.shatterHzEdit.text())
        correlated = trial[1]
        o1_valve = trial[2]
        o1_contr = trial[3]
        o2_valve = trial[4]
        o2_contr = trial[5]
        b_valve = trial[6]
        b_contr = trial[7]
        frequency = trial[8]
        valence_map = trial[9]

        anti_phase_offset = (1.0 / frequency) * 0.5
        phase_choice = np.random.randint(0, 2)

        for p in range(len(valence_map)):
            param = {'type': 'RandomNoise',
                     'fromDuty': True,
                     'frequency': frequency,
                     'duty': 0.5,
                     'fromLength': True,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'phase_chop': True,
                     'lick_fraction': trial[10],
                     'shadow': False,
                     'shatter_frequency': shatter_hz,
                     'target_duty': 0.5,
                     'amp_min': 0.0,
                     'amp_max': 1.0}

            # is this an odour 1 valve
            if p + 1 in o1_valve:
                param['length'] = length
                param['target_duty'] = o1_contr[np.where(o1_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * phase_choice

            # is this an odour 2 valve
            if p + 1 in o2_valve:
                param['length'] = length
                param['target_duty'] = o2_contr[np.where(o2_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * phase_choice
                else:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)

            # is this a blank valve
            if p + 1 in b_valve:
                param['length'] = length
                param['target_duty'] = b_contr[np.where(b_valve == p + 1)[0]]
                if correlated:
                    param['onset'] += anti_phase_offset * (1 - phase_choice)
                else:
                    if param['target_duty'] != 0.5:
                        param['shadow'] = True
                    else:
                        param['onset'] += anti_phase_offset * np.where(b_valve == p + 1)[0][0]

            params.append(param)

        return params


class ShatterValveWidget(QtWidgets.QWidget, shatterValveTestDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0])

        frequency = float(self.pulseFrequencyEdit.text())

        schedule = []
        for t in range(n_trials):
            o_choice = np.random.choice(valve_index[1], 1) + 1
            b_choice = np.random.choice(valve_index[0], 1) + 1
            amp_target = np.round(np.random.uniform(), 2)

            schedule.append([1, o_choice, b_choice, amp_target, frequency, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Odour Valve', 'Blank Valve', 'Target Amplitude', 'Frequency', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_hz = float(self.shatterHzEdit.text())
        o_valve = trial[1]
        b_valve = trial[2]
        target_amp = trial[3]
        frequency = trial[4]
        valence_map = trial[5]

        anti_phase_offset = (1.0 / frequency) * 0.5
        phase_choice = np.random.randint(0, 2)

        for p in range(len(valence_map)):
            param = {'type': 'RandomNoise',
                     'fromDuty': True,
                     'frequency': frequency,
                     'duty': 0.5,
                     'fromLength': True,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'phase_chop': True,
                     'lick_fraction': trial[6],
                     'shadow': False,
                     'shatter_frequency': shatter_hz,
                     'target_duty': 0.5,
                     'amp_min': 0.0,
                     'amp_max': 1.0}

            # is this an odour 1 valve
            if p + 1 in o_valve:
                print(p + 1)
                param['length'] = length
                param['onset'] += anti_phase_offset * (1 - phase_choice)
                param['target_duty'] = target_amp

            # is this a blank valve
            if p + 1 in b_valve:
                param['length'] = length
                param['onset'] += anti_phase_offset * phase_choice
                param['target_duty'] = target_amp

            params.append(param)

        return params


#Distance widget draft

class DistanceGNG(QtWidgets.QWidget, DistanceGNGDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        n_swap_trials = int(self.nSwapTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials + n_swap_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0],
                       np.where(valence_map == 5)[0],
                       np.where(valence_map == 6)[0],
                       np.where(valence_map == 7)[0])

        target_odour = int(self.OdourSelectEdit.text())
        target_distance = int(self.TargetDistanceEdit.text())

        # first pick the target distance
        if target_distance == 1:

            # then pick the target odour
            if target_odour == 1:
                rewarded_default = valve_index[6]
                rewarded_swap = valve_index[1]
                unrewarded_default = valve_index[2]
                unrewarded_swap = valve_index[7]
            else:
                rewarded_default = valve_index[7]
                rewarded_swap = valve_index[2]
                unrewarded_default = valve_index[1]
                unrewarded_swap = valve_index[6]

            # set up blank valve, must be from the other manifold
            # different valves for rewarded and unrewarded, reversed when swap
            blank_rewarded = valve_index[0]
            blank_unrewarded = valve_index[4]

        else:

            if target_odour == 1:
                rewarded_default = valve_index[1]
                rewarded_swap = valve_index[6]
                unrewarded_default = valve_index[7]
                unrewarded_swap = valve_index[2]
            else:
                rewarded_default = valve_index[2]
                rewarded_swap = valve_index[7]
                unrewarded_default = valve_index[6]
                unrewarded_swap = valve_index[1]

            blank_rewarded = valve_index[4]
            blank_unrewarded = valve_index[0]

        schedule = []
        for t in range(n_trials + n_swap_trials):
            rewarded = reward_sequence[t] == 1

            if t < n_trials:
                swap = False
                if rewarded:
                    odour_valve = np.random.choice(rewarded_default, 1) + 1
                    blank_valve = np.random.choice(blank_rewarded, 1) + 1
                else:
                    odour_valve = np.random.choice(unrewarded_default, 1) + 1
                    blank_valve = np.random.choice(blank_unrewarded, 1) + 1

            else: #must add the actual valve swapping
                swap = True
                if rewarded:
                    odour_valve = np.random.choice(rewarded_swap, 1) + 1
                    blank_valve = np.random.choice(blank_unrewarded, 1) + 1
                else:
                    odour_valve = np.random.choice(unrewarded_swap, 1) + 1
                    blank_valve = np.random.choice(blank_rewarded, 1) + 1

            #turning swap valve if swap is True (5 is swap valve, 3 should be empty for now)
            if swap:
                swap_valve = valve_index[5] + 1
            else:
                swap_valve = valve_index[3] + 1  #this might give the right result but it's an awful solution to problem

            schedule.append([reward_sequence[t], odour_valve, blank_valve, swap_valve, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Odour Valve', 'Blank Valve', 'Swap Valve', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        odour_valve = trial[1]
        blank_valve = trial[2]
        swap_valve = trial[3]
        valence_map = trial[4]

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': False,
                     'fromValues': True,
                     'pulse_width': length,
                     'pulse_delay': 0.0,
                     'fromLength': False,
                     'fromRepeats': True,
                     'repeats': 0,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': trial[5]}

            if p + 1 in odour_valve:
                param['repeats'] = 1

            if p + 1 in swap_valve:
                param['repeats'] = 1

            if p + 1 in blank_valve:
                param['repeats'] = 1

            params.append(param)

        return params

# distance widget draft no 2 = random swap valve for every trial

class DistanceGNGRandomSwap (QtWidgets.QWidget, DistanceGNGRandomSwapDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)
        swap_sequence = Gen.swap_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0],
                       np.where(valence_map == 5)[0],
                       np.where(valence_map == 6)[0],
                       np.where(valence_map == 7)[0])

        target_odour = int(self.OdourSelectEdit.text())
        target_distance = int(self.TargetDistanceEdit.text())

        # first pick the target distance
        if target_distance == 1:

            # then pick the target odour
            if target_odour == 1:
                rewarded_default = valve_index[6]
                rewarded_swap = valve_index[1]
                unrewarded_default = valve_index[2]
                unrewarded_swap = valve_index[7]
            else:
                rewarded_default = valve_index[7]
                rewarded_swap = valve_index[2]
                unrewarded_default = valve_index[1]
                unrewarded_swap = valve_index[6]

            # set up blank valve, must be from the other manifold
            # different valves for rewarded and unrewarded, reversed when swap
            blank_rewarded = valve_index[0]
            blank_unrewarded = valve_index[4]

        else:

            if target_odour == 1:
                rewarded_default = valve_index[1]
                rewarded_swap = valve_index[6]
                unrewarded_default = valve_index[7]
                unrewarded_swap = valve_index[2]
            else:
                rewarded_default = valve_index[2]
                rewarded_swap = valve_index[7]
                unrewarded_default = valve_index[6]
                unrewarded_swap = valve_index[1]

            blank_rewarded = valve_index[4]
            blank_unrewarded = valve_index[0]

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1
            swap = swap_sequence[t] == 1

            if rewarded and swap:
                odour_valve = np.random.choice(rewarded_swap, 1) + 1
                blank_valve = np.random.choice(blank_unrewarded, 1) + 1
            elif rewarded and not swap:
                odour_valve = np.random.choice(rewarded_default, 1) + 1
                blank_valve = np.random.choice(blank_rewarded, 1) + 1
            elif not rewarded and swap:
                odour_valve = np.random.choice(unrewarded_swap, 1) + 1
                blank_valve = np.random.choice(blank_rewarded, 1) + 1
            elif not rewarded and not swap:
                odour_valve = np.random.choice(unrewarded_default, 1) + 1
                blank_valve = np.random.choice(blank_unrewarded, 1) + 1

            if swap:
                swap_valve = valve_index[5] + 1
            else:
                swap_valve = valve_index[3] + 1

            schedule.append([reward_sequence[t], odour_valve, blank_valve, swap_valve, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Odour Valve', 'Blank Valve', 'Swap Valve', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        odour_valve = trial[1]
        blank_valve = trial[2]
        swap_valve = trial[3]
        valence_map = trial[4]

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': False,
                     'fromValues': True,
                     'pulse_width': length,
                     'pulse_delay': 0.0,
                     'fromLength': False,
                     'fromRepeats': True,
                     'repeats': 0,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': trial[5]}

            if p + 1 in odour_valve:
                param['repeats'] = 1

            if p + 1 in swap_valve:
                param['repeats'] = 1

            if p + 1 in blank_valve:
                param['repeats'] = 1

            params.append(param)

        return params

class DistanceRobotGNGWidget(QtWidgets.QWidget, DistanceRobotGNGDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],  # near robot
                       np.where(valence_map == 2)[0],  # far robot
                       np.where(valence_map == 3)[0],  # near unrewarded odour valve
                       np.where(valence_map == 4)[0],  # far unrewarded odour valve
                       np.where(valence_map == 5)[0],  # near blank valve
                       np.where(valence_map == 6)[0])  # far blank valve

        if not bool(self.reverseValenceCheck.isChecked()):  # near is rewarded
            rewarded_robot = valve_index[1]
            unrewarded_robot = valve_index[2]
            unrewarded_valve = valve_index[4]
            blank_valve = valve_index[5]
        else:                                               # far is rewarded
            rewarded_robot = valve_index[2]
            unrewarded_robot = valve_index[1]
            unrewarded_valve = valve_index[3]
            blank_valve = valve_index[6]

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                robot = np.random.choice(rewarded_robot, 1) + 1
                valve = np.random.choice(blank_valve, 1) + 1
            else:
                robot = np.random.choice(unrewarded_robot, 1) + 1
                valve = np.random.choice(unrewarded_valve, 1) + 1

            schedule.append([reward_sequence[t], robot, valve, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Robot', 'Valve', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_hz = float(self.ShatterFreqEdit.text())
        target_amp = float(self.TargetAmplitudeEdit.text())
        robot = trial[1]
        valve = trial[2]
        valence_map = trial[3]

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': False,
                     'fromValues': True,
                     'pulse_width': length,
                     'pulse_delay': 0.0,
                     'fromLength': False,
                     'fromRepeats': True,
                     'repeats': 0,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': trial[4]}

            if p + 1 in robot:
                param['repeats'] = 1

            if p + 1 in valve:
                param['type'] = 'RandomNoise'
                param['repeats'] = 1
                param['length'] = length
                param['isClean'] = False
                param['shatter_frequency'] = shatter_hz
                param['target_duty'] = target_amp
                param['amp_min'] = 0.0
                param['amp_max'] = 1.0
                param['shadow'] = False
                # param['phase_chop'] = True
                # param['chop_amount'] = 0.25

            params.append(param)

        return params

#simple schedule generator for plume A vs plume B to test implementation of plumes in AutonoMouse

class SimpleGNGPlumes(QtWidgets.QWidget, SimpleGNGPlumesDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__,self).__init__()
        self.setupUi(self)
        self.parentUi = parentUi
        self.valence_map = None

        self.openPlumeDataButton1.clicked.connect(self.load_plume_bank1)
        self.openPlumeDataButton2.clicked.connect(self.load_plume_bank2)

        self.odour1rewarded = bool(self.odour1rewardedCheck.isChecked())


    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
       # n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials) #add control trials here too

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],   #blank
                       np.where(valence_map == 1)[0],   #odour1
                       np.where(valence_map == 2)[0],   #odour2
                       np.where(valence_map == 3)[0],   #blank2
                       np.where(valence_map == 4)[0])

        #odour1rewarded = bool(self.odour1rewardedCheck.isChecked())

        if self.odour1rewarded:
            rewarded_choice = valve_index[1]
            rewarded_paths = self.plume_bank1
            unrewarded_choice = random.choice(valve_index[2])
            unrewarded_paths = self.plume_bank2
            print(rewarded_paths)
        else:
            rewarded_choice = valve_index[2]
            rewarded_paths = self.plume_bank2
            unrewarded_choice = valve_index[1]
            unrewarded_paths = self.plume_bank1

        schedule = []
        for t in range(n_trials): #add control trials here too
            rewarded = reward_sequence[t] == 1

            if rewarded:
                odour_valve = np.random.choice(rewarded_choice, 1) + 1
                blank_valve = np.random.choice(valve_index[0], 2, replace=False) + 1
                data_path = random.choice(rewarded_paths)
            else:
                odour_valve = np.random.choice(unrewarded_choice, 1) + 1
                blank_valve = np.hstack((np.random.choice(valve_index[0], 1)[0] + 1, np.random.choice(valve_index[4], 1)[0] + 1))
                data_path = random.choice(unrewarded_paths)

            print(data_path)

            schedule.append([reward_sequence[t], odour_valve, blank_valve, valence_map, lick_fraction, data_path])
        return schedule, ['Rewarded', 'Odour valve', 'Blank valve', 'Valence map', 'Lick Fraction', 'Plume Data Path']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max1 = float(self.targetMax1Edit.text())
        target_max2 = float(self.targetMax2Edit.text())
        odour_valve = trial[1]
        blank_valve = trial[2]
        valence_map = trial[3]

        for p in range(len(valence_map)):
            # assign correct plume to valve
            param = {'type': 'Plume',
                     'onset': onset,
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[4],
                     'target_max': target_max1,
                     }
            if p+1 in odour_valve:
                param['data_path'] = trial[5]
                print(param['data_path'])
            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = False
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True


                # if self.odour1rewarded:
                #     if rewarded:
                #         param['data_path'] = odour1_data_path
                #         param['target_max'] = target_max1
                #     else:
                #         param['data_path'] = odour2_data_path
                #         param['target_max'] = target_max2
                #
                # else:
                #     if rewarded:
                #         param['data_path'] = odour2_data_path
                #         param['target_max'] = target_max2
                #     else:
                #         param['data_path'] = odour1_data_path
                #         param['target_max'] = target_max1

            #if p+1 in blank_valve:
                #this bit will do the compensation for airflow bit

            params.append(param)

        return(params)

    def load_plume_bank1(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plume1DataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank1 = [os.path.join(folder, i) for i in plume_files]
        print(self.plume_bank1)

    def load_plume_bank2(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plume2DataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank2 = [os.path.join(folder, i) for i in plume_files]




#variable onset

class SimpleGNGVariableOnsetWidget(QtWidgets.QWidget, SimpleGNGVariableOnsetDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])

        if not bool(self.reverseValenceCheck.isChecked()):
            rewarded_choice = valve_index[1]
            unrewarded_choice = valve_index[2]
        else:
            rewarded_choice = valve_index[2]
            unrewarded_choice = valve_index[1]

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                valve = np.random.choice(rewarded_choice, 1) + 1
            else:
                valve = np.random.choice(unrewarded_choice, 1) + 1

            schedule.append([reward_sequence[t], valve, valence_map, lick_fraction])

        return schedule, ['Rewarded', 'Valve', 'Valence Map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()

        mindelay = float(self.mindelayEdit.text())
        maxdelay = float(self.maxdelayEdit.text())
        delay = random.random()*(maxdelay-mindelay)
        onset = delay + mindelay
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        valve = trial[1]
        valence_map = trial[2]

        for p in range(len(valence_map)):
            param = {'type': 'Simple',
                     'fromDuty': False,
                     'fromValues': True,
                     'pulse_width': length,
                     'pulse_delay': 0.0,
                     'fromLength': False,
                     'fromRepeats': True,
                     'repeats': 0,
                     'length': 0.0,
                     'isClean': True,
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': trial[3]}

            if p + 1 in valve:
                param['repeats'] = 1

            params.append(param)

        return params

class PretrainPlumeBgWidget(QtWidgets.QWidget, PretrainPlumeBgDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

        self.openPlumeDataButton.clicked.connect(self.load_plume_bank)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        target = int(self.targetEdit.text())

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],
                       np.where(valence_map == 1)[0],
                       np.where(valence_map == 2)[0],
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0],
                       np.where(valence_map == 5)[0]) # blank for plume background

        plume_paths = self.plume_bank

        schedule = []
        for t in range(n_trials):
            valve = np.random.choice(valve_index[target], 1) + 1

            # get plume data
            data_path = plume_paths[0]
            blankvalve1 = np.random.choice(valve_index[4], 1) + 1
            blankvalve2 = np.random.choice(valve_index[5], 1) + 1
            schedule.append([1, valve, valence_map, lick_fraction, data_path, blankvalve1, blankvalve2])


        return schedule, ['Rewarded', 'Valve', 'Valence Map', 'Lick Fraction', 'Data Path', 'Blank Valve 1', 'Blank Valve 2']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max = float(self.targetMaxEdit.text())
        valve = trial[1]
        valence_map = trial[2]
        data_path = trial[4]
        plumevalve = trial[5]
        antiplumevalve = trial[6]

        for p in range(len(valence_map)):
            param = {'type': 'Plume',
                     'onset': onset,
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[3],
                     'target_max': target_max,
                     }

            if p + 1 in valve:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True

            elif p + 1 in plumevalve:
                param['data_path'] = data_path

            # add antiplume noise background
            elif p + 1 in antiplumevalve:
                param['type'] = 'Anti Plume'
                param['data_path'] = data_path

            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True


            params.append(param)

        return params

    def load_plume_bank(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plumeDataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank = [os.path.join(folder, i) for i in plume_files]


class GNGPlumeBgWidget(QtWidgets.QWidget, GNGPlumeBgDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

        self.openPlumeDataButton1.clicked.connect(self.load_plume_bank)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],  # blank
                       np.where(valence_map == 1)[0],  # odour 1
                       np.where(valence_map == 2)[0],  # odour 2
                       np.where(valence_map == 3)[0],  # control odour 1
                       np.where(valence_map == 4)[0],  # blank plume valve
                       np.where(valence_map == 5)[0])  # blank anti plume valve

        if bool(self.odour1rewardedCheck.isChecked()):
            rewarded_choice = valve_index[1]
            unrewarded_choice = valve_index[2]
        else:
            rewarded_choice = valve_index[2]
            unrewarded_choice = valve_index[1]

        plume_paths = self.plume_bank

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                valve = np.random.choice(rewarded_choice, 1) + 1
            else:
                valve = np.random.choice(unrewarded_choice, 1) + 1

            # get plume data
            data_path = plume_paths[0]
            blankvalve1 = np.random.choice(valve_index[4], 1) + 1
            blankvalve2 = np.random.choice(valve_index[5], 1) + 1

            schedule.append([reward_sequence[t], valve, valence_map, lick_fraction, data_path, blankvalve1, blankvalve2])

        return schedule, ['Rewarded', 'Valve', 'Valence Map', 'Lick Fraction', 'Data Path', 'Blank Valve 1', 'Blank Valve 2']

    def pulse_parameters(self, trial):
        params = list()

        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max = float(self.targetMax1Edit.text())
        valve = trial[1]
        valence_map = trial[2]
        data_path = trial[4]
        plumevalve = trial[5]
        antiplumevalve = trial[6]

        for p in range(len(valence_map)):
            param = {'type': 'Plume',
                     'onset': onset,
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[3],
                     'target_max': target_max,
                     }

            if p + 1 in valve:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True

            elif p + 1 in plumevalve:
                param['data_path'] = data_path

            # add antiplume noise background
            elif p + 1 in antiplumevalve:
                param['type'] = 'Anti Plume'
                param['data_path'] = data_path

            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)

        return params

    def load_plume_bank(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plumeDataLabel1.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank = [os.path.join(folder, i) for i in plume_files]


class GNGPlumeBgDelaysWidget(QtWidgets.QWidget, GNGPlumeBgDelaysDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

        self.openPlumeDataButton1.clicked.connect(self.load_plume_bank)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],  # blank
                       np.where(valence_map == 1)[0],  # odour 1
                       np.where(valence_map == 2)[0],  # odour 2
                       np.where(valence_map == 3)[0],  # control odour 1
                       np.where(valence_map == 4)[0],  # blank plume valve
                       np.where(valence_map == 5)[0])  # blank anti plume valve

        if bool(self.odour1rewardedCheck.isChecked()):
            rewarded_choice = valve_index[1]
            unrewarded_choice = valve_index[2]
        else:
            rewarded_choice = valve_index[2]
            unrewarded_choice = valve_index[1]

        plume_paths = self.plume_bank

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                valve = np.random.choice(rewarded_choice, 1) + 1
            else:
                valve = np.random.choice(unrewarded_choice, 1) + 1

            # get plume data
            data_path = plume_paths[0]
            blankvalve1 = np.random.choice(valve_index[4], 1) + 1
            blankvalve2 = np.random.choice(valve_index[5], 1) + 1

            schedule.append([reward_sequence[t], valve, valence_map, lick_fraction, data_path, blankvalve1, blankvalve2])

        return schedule, ['Rewarded', 'Valve', 'Valence Map', 'Lick Fraction', 'Data Path', 'Blank Valve 1', 'Blank Valve 2']

    def pulse_parameters(self, trial):
        params = list()

        mindelay = float(self.mindelayEdit.text())
        maxdelay = float(self.maxdelayEdit.text())
        delay = random.random()*(maxdelay-mindelay)
        onset = delay + mindelay
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max = float(self.targetMax1Edit.text())
        valve = trial[1]
        valence_map = trial[2]
        data_path = trial[4]
        plumevalve = trial[5]
        antiplumevalve = trial[6]

        for p in range(len(valence_map)):
            param = {'type': 'Plume',
                     'onset': 0.01,    # plume noise starts from the beginning of the trial, odour delivery is the only one delayed
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[3],
                     'target_max': target_max,
                     }

            if p + 1 in valve:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = onset

            elif p + 1 in plumevalve:
                param['data_path'] = data_path

            # add antiplume noise background
            elif p + 1 in antiplumevalve:
                param['type'] = 'Anti Plume'
                param['data_path'] = data_path

            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)

        return params

    def load_plume_bank(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plumeDataLabel1.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank = [os.path.join(folder, i) for i in plume_files]


class DistanceTrainingWidget(QtWidgets.QWidget, DistanceTrainingDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

        self.openPlumeDataButton.clicked.connect(self.load_plume_bank)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],    # blank tODD valve
                       np.where(valence_map == 1)[0],    # Box condition 1 (Far)
                       np.where(valence_map == 2)[0],    # Box condition 2 (Near)
                       np.where(valence_map == 3)[0],    # control odour 1
                       np.where(valence_map == 4)[0],    # blank plume valve
                       np.where(valence_map == 5)[0],    # blank anti plume valve
                       np.where(valence_map == 6)[0],    # Blank box condition 1 (Far)
                       np.where(valence_map == 7)[0],    # Blank box condition 2 (Near)
                       np.where(valence_map == 8)[0],    # Guide valve odour 1
                       np.where(valence_map == 9)[0],)   # Guide valve blank

        guidevalvetarget = int(self.GuideValveTargetEdit.text())


        if bool(self.FarBoxRewardedCheck.isChecked()):      # far is rewarded
            rewarded_choice = valve_index[1]
            unrewarded_choice = valve_index[2]
            rewarded_blank = valve_index[7]
            unrewarded_blank = valve_index[6]
            rewarded_guide = valve_index[9]
            unrewarded_guide = valve_index[8]

        else:                                               # near is rewarded
            rewarded_choice = valve_index[2]
            unrewarded_choice = valve_index[1]
            rewarded_blank = valve_index[6]
            unrewarded_blank = valve_index[7]
            rewarded_guide = valve_index[8]
            unrewarded_guide = valve_index[9]



        plume_paths = self.plume_bank

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                odour_box = np.random.choice(rewarded_choice, 1) + 1
                blank_box = np.random.choice(rewarded_blank, 1) + 1
                guide_valve = np.random.choice(rewarded_guide, 1) + 1
            else:
                odour_box = np.random.choice(unrewarded_choice, 1) + 1
                blank_box = np.random.choice(unrewarded_blank, 1) + 1
                guide_valve = np.random.choice(unrewarded_guide, 1) + 1

            # get plume data
            data_path = plume_paths[0]
            blankvalve1 = np.random.choice(valve_index[4], 1) + 1
            blankvalve2 = np.random.choice(valve_index[5], 1) + 1

            schedule.append([reward_sequence[t], odour_box, valence_map, lick_fraction, data_path, blankvalve1, blankvalve2, blank_box, guide_valve])

        return schedule, ['Rewarded', 'Odour Box', 'Valence Map', 'Lick Fraction', 'Data Path', 'Blank Valve 1', 'Blank Valve 2', 'Blank Box', 'Guide Valve']

    def pulse_parameters(self, trial):
        params = list()

        mindelay = float(self.mindelayEdit.text())
        maxdelay = float(self.maxdelayEdit.text())
        delay = random.random()*(maxdelay-mindelay)
        onset = delay + mindelay
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max = float(self.targetMaxEdit.text())
        odour_box = trial[1]
        valence_map = trial[2]
        data_path = trial[4]
        plumevalve = trial[5]
        antiplumevalve = trial[6]
        blank_box = trial[7]
        guide_valve = trial[8]
        shatter_hz = float(self.GuideValveShatterFreqEdit.text())
        target_amp = float(self.GuideValveTargetAmplitudeEdit.text())

        for p in range(len(valence_map)):
            param = {'type': 'Plume',
                     'onset': 0.01,    # plume noise starts from the beginning of the trial, odour delivery is the only one delayed
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[3],
                     'target_max': target_max,
                     }

            if p + 1 in odour_box:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = onset

            elif p + 1 in blank_box:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = onset

            elif p + 1 in guide_valve:
                param['type'] = 'RandomNoise'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = length
                param['isClean'] = False
                param['shatter_frequency'] = shatter_hz
                param['target_duty'] = target_amp
                param['amp_min'] = 0.0
                param['amp_max'] = 1.0
                param['shadow'] = False
                param['onset'] = onset
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                # param['phase_chop'] = True
                # param['chop_amount'] = 0.25


            elif p + 1 in plumevalve:
                param['data_path'] = data_path

            # add antiplume noise background
            elif p + 1 in antiplumevalve:
                param['type'] = 'Anti Plume'
                param['data_path'] = data_path

            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)

        return params

    def load_plume_bank(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plumeDataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank = [os.path.join(folder, i) for i in plume_files]


class DistanceTaskOnsetJitter(QtWidgets.QWidget, DistanceTaskOnsetJitterDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

        self.openPlumeDataButton.clicked.connect(self.load_plume_bank)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],    # blank tODD valve
                       np.where(valence_map == 1)[0],    # Box condition 1 (Far)
                       np.where(valence_map == 2)[0],    # Box condition 2 (Near)
                       np.where(valence_map == 3)[0],    # control odour 1
                       np.where(valence_map == 4)[0],    # blank plume valve
                       np.where(valence_map == 5)[0],    # blank anti plume valve
                       np.where(valence_map == 6)[0],    # Blank box condition 1 (Far)
                       np.where(valence_map == 7)[0])    # Blank box condition 2 (Near)

        mindelayNear = float(self.mindelayNearEdit.text())      # get onset info to be randomised for each trial
        maxdelayNear = float(self.maxdelayNearEdit.text())
        mindelayFar = float(self.mindelayFarEdit.text())
        maxdelayFar = float(self.maxdelayFarEdit.text())

        if bool(self.FarBoxRewardedCheck.isChecked()):      # far is rewarded
            rewarded_choice = valve_index[1]
            unrewarded_choice = valve_index[2]
            rewarded_blank = valve_index[7]
            unrewarded_blank = valve_index[6]

        else:                                               # near is rewarded
            rewarded_choice = valve_index[2]
            unrewarded_choice = valve_index[1]
            rewarded_blank = valve_index[6]
            unrewarded_blank = valve_index[7]


        plume_paths = self.plume_bank

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            # calculate onsets for near and far boxes separately
            delayNear = random.random() * (maxdelayNear - mindelayNear)  # to be added to mindelay
            onsetNear = round(delayNear + mindelayNear,3)
            delayFar = random.random() * (maxdelayFar - mindelayFar)  # to be added to mindelay
            onsetFar = round(delayNear + mindelayFar,3)


            if rewarded:
                odour_box = np.random.choice(rewarded_choice, 1) + 1
                blank_box = np.random.choice(rewarded_blank, 1) + 1
                if bool(self.FarBoxRewardedCheck.isChecked()):  # far is rewarded, S+ trial: odour box is far and blank box is near
                    odour_box_onset = onsetFar
                    blank_box_onset = onsetNear
                else:
                    odour_box_onset = onsetNear
                    blank_box_onset = onsetFar
            else:
                odour_box = np.random.choice(unrewarded_choice, 1) + 1
                blank_box = np.random.choice(unrewarded_blank, 1) + 1
                if bool(self.FarBoxRewardedCheck.isChecked()):  # far is rewarded, S- trial: odour box is near and blank box is far
                    odour_box_onset = onsetNear
                    blank_box_onset = onsetFar
                else:
                    odour_box_onset = onsetFar
                    blank_box_onset = onsetNear


            # get plume data
            data_path = plume_paths[0]
            blankvalve1 = np.random.choice(valve_index[4], 1) + 1
            blankvalve2 = np.random.choice(valve_index[5], 1) + 1


            schedule.append([reward_sequence[t], odour_box, valence_map, lick_fraction, data_path, blankvalve1, blankvalve2, blank_box, odour_box_onset, blank_box_onset])

        return schedule, ['Rewarded', 'Odour Box', 'Valence Map', 'Lick Fraction', 'Data Path', 'Blank Valve 1', 'Blank Valve 2', 'Blank Box', 'Odour Box Onset', 'Blank Box Onset']

    def pulse_parameters(self, trial):
        params = list()

        mindelayNear = float(self.mindelayNearEdit.text())
        maxdelayNear = float(self.maxdelayNearEdit.text())
        delayNear = random.random()*(maxdelayNear-mindelayNear) #to be added to mindelay
        onsetNear = delayNear + mindelayNear

        mindelayFar = float(self.mindelayFarEdit.text())
        maxdelayFar = float(self.maxdelayFarEdit.text())
        delayFar = random.random()*(maxdelayFar-mindelayFar) #to be added to mindelay
        onsetFar = delayNear + mindelayFar

        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max = float(self.targetMaxEdit.text())
        odour_box = trial[1]
        valence_map = trial[2]
        data_path = trial[4]
        plumevalve = trial[5]
        antiplumevalve = trial[6]
        blank_box = trial[7]
        odour_box_onset = trial[8]
        blank_box_onset = trial[9]

        for p in range(len(valence_map)):
            param = {'type': 'Plume',
                     'onset': 0.01,    # plume noise starts from the beginning of the trial, odour delivery is the only one delayed
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[3],
                     'target_max': target_max,
                     }

            if p + 1 in odour_box:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = odour_box_onset

            elif p + 1 in blank_box:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = blank_box_onset

            elif p + 1 in plumevalve:
                param['data_path'] = data_path

            # add antiplume noise background
            elif p + 1 in antiplumevalve:
                param['type'] = 'Anti Plume'
                param['data_path'] = data_path

            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)

        return params

    def load_plume_bank(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plumeDataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank = [os.path.join(folder, i) for i in plume_files]


class DistanceTraining2Widget(QtWidgets.QWidget, DistanceTraining2Design.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.parentUi = parentUi

        self.valence_map = None

        self.openPlumeDataButton.clicked.connect(self.load_plume_bank)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],    # blank tODD valve
                       np.where(valence_map == 1)[0],    # Box condition 1 (Far)
                       np.where(valence_map == 2)[0],    # Box condition 2 (Near)
                       np.where(valence_map == 3)[0],    # control odour 1
                       np.where(valence_map == 4)[0],    # blank plume valve
                       np.where(valence_map == 5)[0],    # blank anti plume valve
                       np.where(valence_map == 6)[0],    # Blank box condition 1 (Far)
                       np.where(valence_map == 7)[0])    # Blank box condition 2 (Near)


        if bool(self.FarBoxRewardedCheck.isChecked()):      # far is rewarded, odour only from near
            rewarded_choice = valve_index[6]
            unrewarded_choice = valve_index[2]
            rewarded_blank = valve_index[7]
            unrewarded_blank = valve_index[6]

        else:                                               # near is rewarded, odour only from far
            rewarded_choice = valve_index[7]
            unrewarded_choice = valve_index[1]
            rewarded_blank = valve_index[6]
            unrewarded_blank = valve_index[7]


        plume_paths = self.plume_bank

        schedule = []
        for t in range(n_trials):
            rewarded = reward_sequence[t] == 1

            if rewarded:
                odour_box = np.random.choice(rewarded_choice, 1) + 1
                blank_box = np.random.choice(rewarded_blank, 1) + 1
            else:
                odour_box = np.random.choice(unrewarded_choice, 1) + 1
                blank_box = np.random.choice(unrewarded_blank, 1) + 1

            # get plume data
            data_path = plume_paths[0]
            blankvalve1 = np.random.choice(valve_index[4], 1) + 1
            blankvalve2 = np.random.choice(valve_index[5], 1) + 1

            schedule.append([reward_sequence[t], odour_box, valence_map, lick_fraction, data_path, blankvalve1, blankvalve2, blank_box])

        return schedule, ['Rewarded', 'Odour Box', 'Valence Map', 'Lick Fraction', 'Data Path', 'Blank Valve 1', 'Blank Valve 2', 'Blank Box']

    def pulse_parameters(self, trial):
        params = list()

        mindelay = float(self.mindelayEdit.text())
        maxdelay = float(self.maxdelayEdit.text())
        delay = random.random()*(maxdelay-mindelay)
        onset = delay + mindelay
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        shatter_frequency = float(self.shatterHzEdit.text())
        data_fs = float(self.dataSamplingRateEdit.text())
        target_max = float(self.targetMaxEdit.text())
        odour_box = trial[1]
        valence_map = trial[2]
        data_path = trial[4]
        plumevalve = trial[5]
        antiplumevalve = trial[6]
        blank_box = trial[7]

        for p in range(len(valence_map)):
            param = {'type': 'Plume',
                     'onset': 0.01,    # plume noise starts from the beginning of the trial, odour delivery is the only one delayed
                     'offset': offset,
                     'shatter_frequency': shatter_frequency,
                     'data_fs': data_fs,
                     'lick_fraction': trial[3],
                     'target_max': target_max,
                     }

            if p + 1 in odour_box:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = onset

            elif p + 1 in blank_box:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 1
                param['length'] = 0.0
                param['isClean'] = True
                param['onset'] = onset

            elif p + 1 in plumevalve:
                param['data_path'] = data_path

            # add antiplume noise background
            elif p + 1 in antiplumevalve:
                param['type'] = 'Anti Plume'
                param['data_path'] = data_path

            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = 0.0
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)

        return params

    def load_plume_bank(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plumeDataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank = [os.path.join(folder, i) for i in plume_files]

# August 2019: messing around with Correlation with real plumes
# left to do: load a bank of plume pairs, not just one pair and implement a random sequence to play them in

class CorrelationGNGNaturalPlumes(QtWidgets.QWidget, CorrelationGNGNaturalPlumesDesign.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__,self).__init__()
        self.setupUi(self)
        self.parentUi = parentUi
        self.valence_map = None

        self.CorrPlumesButton.clicked.connect(self.load_corr_plumes)
        self.UncorrPlumesButton.clicked.connect(self.load_uncorr_plumes)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
       # n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)     # add control trials here too

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],   # blank
                       np.where(valence_map == 1)[0],   # odour1
                       np.where(valence_map == 2)[0],   # odour2
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])   # blank2

        CorrRewarded = bool(self.CorrRewardedCheck.isChecked())     # tick if S+ is correlated,
                                                                    # untick for S+ is uncorrelated

        if CorrRewarded:
            rewarded_plumes = self.corr_plumes
            unrewarded_plumes = self.uncorr_plumes
            correlated = reward_sequence
            print(rewarded_plumes)
        else:
            rewarded_plumes = self.uncorr_plumes
            unrewarded_plumes = self.corr_plumes
            correlated = (reward_sequence*(-1)) + 1
            print(rewarded_plumes)

        # MAKE PLUME PAIR SEQUENCE
        number_pairs = len(rewarded_plumes)
        print(number_pairs)
        plume_pair_sequence = list()
        j = 0
        for i in range(0, n_trials):
            plume_pair_sequence.append(j)
            if j == number_pairs-1:
                j = 0
            else:
                j += 1
        print(plume_pair_sequence)
        random.shuffle(plume_pair_sequence)
        print(plume_pair_sequence)

        schedule = []
        for t in range(n_trials): #add control trials here too
            rewarded = reward_sequence[t] == 1
            o1_valve = np.random.choice(valve_index[1], 1) + 1
            o2_valve = np.random.choice(valve_index[2], 1) + 1
            b1_valve = np.random.choice(valve_index[0], 1) + 1  # keeping the two blank valves separate in case
            b2_valve = np.random.choice(valve_index[4], 1) + 1  # flow compensation is position dependent
            print(plume_pair_sequence[t])

            if rewarded:
                plume1 = rewarded_plumes[plume_pair_sequence[t]][0]
                plume2 = rewarded_plumes[plume_pair_sequence[t]][1]
            else:
                plume1 = unrewarded_plumes[plume_pair_sequence[t]][0]
                plume2 = unrewarded_plumes[plume_pair_sequence[t]][1]


            print(plume1)
            print(plume2)

            schedule.append([reward_sequence[t], correlated[t], plume_pair_sequence[t], o1_valve, o2_valve, b1_valve, b2_valve,
                             plume1, plume2, valence_map, lick_fraction])
        return schedule, ['Rewarded', 'Correlated', 'Plume pair number', 'Odour 1 valve', 'Odour 2 valve', 'Blank 1 valve', 'Blank 2 valve',
                          'Plume 1', 'Plume 2', 'Valence map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()
        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        o1_valve = trial[3]
        o2_valve = trial[4]
        b1_valve = trial[5]
        b2_valve = trial[6]
        plume1 = trial[7]
        plume2 = trial[8]
        valence_map = trial[9]
        lick_fraction = trial[10]

        for p in range(len(valence_map)):
            # assign correct plume to valve
            param = {'type': 'Plume',
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': lick_fraction,
                     }
            if p+1 in o1_valve:
                param['shatter_frequency'] = plume1['shatter_frequency']
                param['data_fs'] = plume1['data_fs']
                param['data_path'] = plume1['data_path']
                param['target_max'] = plume1['target_max']
                print(param)
            elif p+1 in o2_valve:
                param['shatter_frequency'] = plume2['shatter_frequency']
                param['data_fs'] = plume2['data_fs']
                param['data_path'] = plume2['data_path']
                param['target_max'] = plume2['target_max']
                print(param)
            elif p+1 in b1_valve:
                param['type'] = 'Anti Plume'
                param['shatter_frequency'] = plume1['shatter_frequency']
                param['data_fs'] = plume1['data_fs']
                param['data_path'] = plume1['data_path']
                param['target_max'] = plume1['target_max']
                print(param)
            elif p+1 in b2_valve:
                param['type'] = 'Anti Plume'
                param['shatter_frequency'] = plume2['shatter_frequency']
                param['data_fs'] = plume2['data_fs']
                param['data_path'] = plume2['data_path']
                param['target_max'] = plume2['target_max']
                print(param)
            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = False
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)

        return(params)

    def load_plume_bank1(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder:", '', QtWidgets.QFileDialog.ShowDirsOnly)
        self.plume1DataLabel.setText(folder)
        plume_files = os.listdir(folder)
        self.plume_bank1 = [os.path.join(folder, i) for i in plume_files]
        print(self.plume_bank1)

    def load_corr_plumes(self):
        # do the stuff when the button is clicked: load a pair of plumes as params
        corr_file = QtWidgets.QFileDialog.getOpenFileName()
        corr_file = corr_file[0]
        self.CorrPlumesLabel.setText(corr_file)
        print(corr_file)
        self.corr_plumes = pickle.Unpickler(open(corr_file, 'rb')).load()
        print(self.corr_plumes)


    def load_uncorr_plumes(self):
        uncorr_file = QtWidgets.QFileDialog.getOpenFileName()
        uncorr_file = uncorr_file[0]
        self.UncorrPlumesLabel.setText(uncorr_file)
        self.uncorr_plumes = pickle.Unpickler(open(uncorr_file, 'rb')).load()


class CorrelationGNGNaturalPlumes2(QtWidgets.QWidget, CorrelationGNGNaturalPlumes2Design.Ui_Form):
    def __init__(self, parentUi=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.parentUi = parentUi
        self.valence_map = None

        self.CorrPlumesButton.clicked.connect(self.load_corr_plumes)
        self.UncorrPlumesButton.clicked.connect(self.load_uncorr_plumes)

    def generate_schedule(self, valence_map):
        lick_fraction = float(self.lickFractionEdit.text())
        n_valves = len(valence_map)

        n_trials = int(self.nTrialsEdit.text())
        # n_control_trials = int(self.nControlTrialsEdit.text())
        reward_sequence = Gen.reward_sequence(n_trials)  # add control trials here too

        valence_map = np.array(valence_map)
        valve_index = (np.where(valence_map == 0)[0],  # blank
                       np.where(valence_map == 1)[0],  # odour1
                       np.where(valence_map == 2)[0],  # odour2
                       np.where(valence_map == 3)[0],
                       np.where(valence_map == 4)[0])  # blank2

        CorrRewarded = bool(self.CorrRewardedCheck.isChecked())  # tick if S+ is correlated,
        # untick for S+ is uncorrelated

        if CorrRewarded:
            rewarded_plumes = self.corr_plumes
            unrewarded_plumes = self.uncorr_plumes
            correlated = reward_sequence
            print(rewarded_plumes)
        else:
            rewarded_plumes = self.uncorr_plumes
            unrewarded_plumes = self.corr_plumes
            correlated = (reward_sequence * (-1)) + 1
            print(rewarded_plumes)

        schedule = []
        for t in range(n_trials):  # add control trials here too
            rewarded = reward_sequence[t] == 1
            o1_valve = np.random.choice(valve_index[1], 1) + 1
            o2_valve = np.random.choice(valve_index[2], 1) + 1
            b1_valve = np.random.choice(valve_index[0], 1) + 1  # keeping the two blank valves separate in case
            b2_valve = np.random.choice(valve_index[4], 1) + 1  # flow compensation is position dependent

            if rewarded:
                plume1 = rewarded_plumes[0]
                plume2 = rewarded_plumes[1]
            else:
                plume1 = unrewarded_plumes[0]
                plume2 = unrewarded_plumes[1]

            print(plume1)
            print(plume2)

            schedule.append([reward_sequence[t], correlated[t], o1_valve, o2_valve, b1_valve, b2_valve,
                             plume1, plume2, valence_map, lick_fraction])
        return schedule, ['Rewarded', 'Correlated', 'Odour 1 valve', 'Odour 2 valve', 'Blank  1 valve', 'Blank 2 valve',
                          'Plume 1', 'Plume 2', 'Valence map', 'Lick Fraction']

    def pulse_parameters(self, trial):
        params = list()
        onset = float(self.onsetEdit.text())
        offset = float(self.offsetEdit.text())
        length = float(self.trialLengthEdit.text())
        o1_valve = trial[2]
        o2_valve = trial[3]
        b1_valve = trial[4]
        b2_valve = trial[5]
        plume1 = trial[6]
        plume2 = trial[7]
        valence_map = trial[8]
        lick_fraction = trial[9]

        # if we want to jitter target_max around the values in the input file
        AddJitter = bool(self.TargetMaxJitterCheck.isChecked())
        if AddJitter:
            jitterMin = float(self.MinJitterEdit.text())
            jitterMax = float(self.MaxJitterEdit.text())
            jitter = random.random()*(jitterMax-jitterMin) + jitterMin
            target_max = 1 - jitter
        else:
            target_max = 1

        for p in range(len(valence_map)):
            # assign correct plume to valve
            param = {'type': 'Plume',
                     'onset': onset,
                     'offset': offset,
                     'lick_fraction': lick_fraction,
                     'target_max': target_max
                     }
            if p + 1 in o1_valve:
                param['shatter_frequency'] = plume1['shatter_frequency']
                param['data_fs'] = plume1['data_fs']
                param['data_path'] = plume1['data_path']
                param['target_max'] = plume1['target_max']
                print(param)
            elif p + 1 in o2_valve:
                param['shatter_frequency'] = plume2['shatter_frequency']
                param['data_fs'] = plume2['data_fs']
                param['data_path'] = plume2['data_path']
                param['target_max'] = plume2['target_max']
                print(param)
            elif p + 1 in b1_valve:
                param['type'] = 'Anti Plume'
                param['shatter_frequency'] = plume1['shatter_frequency']
                param['data_fs'] = plume1['data_fs']
                param['data_path'] = plume1['data_path']
                param['target_max'] = plume1['target_max']
                print(param)
            elif p + 1 in b2_valve:
                param['type'] = 'Anti Plume'
                param['shatter_frequency'] = plume2['shatter_frequency']
                param['data_fs'] = plume2['data_fs']
                param['data_path'] = plume2['data_path']
                param['target_max'] = plume2['target_max']
                print(param)
            else:
                param['type'] = 'Simple'
                param['fromDuty'] = False
                param['fromValues'] = True
                param['pulse_width'] = length
                param['pulse_delay'] = False
                param['fromLength'] = False
                param['fromRepeats'] = True
                param['repeats'] = 0
                param['length'] = 0.0
                param['isClean'] = True

            params.append(param)
            print(param['target_max'])

        return (params)

    def load_corr_plumes(self):
        # do the stuff when the button is clicked: load a pair of plumes as params
        corr_file = QtWidgets.QFileDialog.getOpenFileName()
        corr_file = corr_file[0]
        self.CorrPlumesLabel.setText(corr_file)
        print(corr_file)
        self.corr_plumes = pickle.Unpickler(open(corr_file, 'rb')).load()
        print(self.corr_plumes)

    def load_uncorr_plumes(self):
        uncorr_file = QtWidgets.QFileDialog.getOpenFileName()
        uncorr_file = uncorr_file[0]
        self.UncorrPlumesLabel.setText(uncorr_file)
        self.uncorr_plumes = pickle.Unpickler(open(uncorr_file, 'rb')).load()