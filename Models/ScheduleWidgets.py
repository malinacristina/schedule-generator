from PyQt5 import QtWidgets
import numpy as np

from Designs import simpleCorrDesign, corrDesign, simpleGNGDesign, pretrainDesign, shatterValveTestDesign, \
    corrRandomFrequencyDesign, corrRandomFrequency2Design, corrDifficultySwitchDesign, DistanceGNGDesign, \
    DistanceGNGRandomSwapDesign, DistanceRobotGNGDesign
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
