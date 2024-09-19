import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import wfdb
from wfdb.processing import normalize_bound

from tensorflow.keras.utils import to_categorical

from detection import util_func

CURR_DIR = os.getcwd()
DATA_DIR = os.path.join(CURR_DIR, '../data/ludb')

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# for better readability
SEGMENTS_STR = {
    0: 'Pon-Poff',
    1: 'Poff-QRSon',
    2: 'QRSon-Rpeak',
    3: 'Rpeak-QRSoff',
    4: 'QRSoff-Ton',
    5: 'Ton-Toff',
    6: 'Toff-Pon2',
    7: 'Zero padding',
}
SEGMENTS_NUM = {
    'Pon-Poff': 0,
    'Poff-QRSon': 1,
    'QRSon-Rpeak': 2,
    'Rpeak-QRSoff': 3,
    'QRSoff-Ton': 4,
    'Ton-Toff': 5,
    'Toff-Pon2': 6,
    'Zero padding': 7
}
SEGMENT_TO_COLOR = {
    -1: 'none',
    0: 'red',
    1: 'darkorange',
    2: 'yellow',
    3: 'green',
    4: 'blue',
    5: 'darkcyan',
    6: 'purple'
}
# LEADS = ['avf', 'avl', 'avr', 'i', 'ii', 'iii', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6'] WRONG
LEADS = ['i', 'ii', 'iii', 'avr', 'avl', 'avf', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6']

WAVELET_FUNCTION = 'bior3.3'
DECOMPOSITION_LEVEL = 7

class ECGSignal:
    def __init__(self, signal, samples, symbols, is_st_elevation):
        self.signal = signal
        self.samples = samples
        self.symbols = symbols

        self.segment_map, self.segment_start_end = self.segmentate()

        self.is_st_elevation = is_st_elevation
    
    @staticmethod
    def _check_st_elevation(record):
        result = 0
        for comment in record.comments:
            if comment.startswith("STEMI:"):
                result = 1
                break
        
        return result

    @staticmethod
    def get_signal(leads, record_numbers=-1):
        if record_numbers == -1:
            record_numbers = range(1, 201)

        ludb_csv = pd.read_csv('../data/ludb/ludb.csv')
        ludb_csv = ludb_csv.replace('\n', '', regex=True)

        result = {
            'record_number': [],
            'lead': [],
            'sex': [],
            'age': [],
            'signal': [],
            'is_st_elevation': []
        }

        for record_num in record_numbers:
            record_dir = os.path.join(DATA_DIR, str(record_num))
            record = wfdb.rdrecord(record_dir)

            is_st_elevation = ECGSignal._check_st_elevation(record)

            for lead in leads:
                signal = record.p_signal[:, LEADS.index(lead)]

                result['record_number'].append(record_num)
                result['lead'].append(lead)
                result['sex'].append(ludb_csv[ludb_csv['ID'] == record_num]['Sex'].values[0])
                result['age'].append(ludb_csv[ludb_csv['ID'] == record_num]['Age'].values[0])
                result['signal'].append(signal)
                result['is_st_elevation'].append(is_st_elevation)
        
        return result


    @staticmethod
    def load_ecg_signal(record_number, lead, raw=False):
        record_dir = os.path.join(DATA_DIR, str(record_number))

        record = wfdb.rdrecord(record_dir)
        ann = wfdb.rdann(record_dir, lead)

        signal = record.p_signal[:, LEADS.index(lead)]

        if not raw:
            signal = util_func.denoise_dwt(signal, wavelet=WAVELET_FUNCTION, level=DECOMPOSITION_LEVEL)
            signal = normalize_bound(signal)

        samples = ann.sample
        symbols = ann.symbol

        is_st_elevation = ECGSignal._check_st_elevation(record)

        return ECGSignal(signal, samples, symbols, is_st_elevation)
    
    
    @staticmethod
    def to_dict(leads, record_numbers=-1, longest_beat=None):
        '''
        Parameters:
        leads (list of string): list of lead file extension name
        longest_beat (int): longest beat used for zero padding reference
        record_numbers (list of int): if not provided, all records will be used
        '''

        def _find_longest_beat(leads, record_numbers, longest_beat):
            if longest_beat is None:
                longest_beat = 0
                for record_num in record_numbers:
                    for lead in leads:
                        s = ECGSignal.load_ecg_signal(record_num, lead)
                        s_beats = s.cut_per_beat()

                        for beat in s_beats:
                            signal, _ = beat
                            longest_beat = max(longest_beat, len(signal))

            return longest_beat
        
        if record_numbers == -1:
            record_numbers = range(1, 201)
        
        longest_beat = _find_longest_beat(leads, record_numbers, longest_beat)
        
        feature = []
        zero_pad_length = []
        lead_n = []
        record_n = []
        is_st_elevations = []
        label = []
        for record_num in record_numbers:
            # print(f"Record {record_num} starts at index: {len(feature)}")
            for lead in leads:
                try:
                    s = ECGSignal.load_ecg_signal(record_num, lead)
                    s_beats = s.cut_per_beat()

                    for beat in s_beats:
                        signal, segment_map = beat
                        signal = np.array(signal)
                        segment_map = np.array(segment_map)

                        # Zero padding
                        pad_length = longest_beat - len(signal)

                        signal = np.pad(signal, (0, pad_length), mode='constant', constant_values=0)
                        segment_map = np.pad(segment_map, (0, pad_length), mode='constant', constant_values=SEGMENTS_NUM['Zero padding'])

                        segment_map = to_categorical(segment_map, num_classes=8)

                        feature.append(signal)
                        zero_pad_length.append(pad_length)
                        lead_n.append(lead)
                        record_n.append(record_num)
                        is_st_elevations.append(s.is_st_elevation)
                        label.append(segment_map)

                except:
                    # Print failed instance
                    print(f"Record: {record_num} | Lead: {lead}", end=' , ')
                    
        result = {
            'signal': feature,
            'zpad_length': zero_pad_length,
            'lead': lead_n,
            'record': record_n,
            'is_st_elevation': is_st_elevations,
            'segment_map': label
        }
        return result

    @staticmethod
    def plot_signal_segments(signal, segment_map, ax=None, save_path=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(28, 3))
        # TODO: NO IDEA HOW I CAN SAVE THIS PASSED AX INSTANCE. So if ax is not None but save_path is not None, thing will surely break

        ax.plot(signal, color='blue')

        segment_start_end = []
        segments = []
        legend_patches = []

        ptr_start = 0
        ptr_end = 0

        for i in range(1, len(segment_map)):
            curr_seg = segment_map[i]
            prev_seg = segment_map[i-1]
            if curr_seg != prev_seg:
                ptr_end = i - 1
                if(segment_map[ptr_start] not in [-1, SEGMENTS_NUM['Zero padding']]): # not annotated (-1) and zero pad
                    segment_start_end.append((segment_map[ptr_start], (ptr_start, ptr_end)))
                    if(segment_map[ptr_start] not in segments):
                        segments.append(segment_map[ptr_start])
                ptr_start = i
        
        # add last segment
        ptr_end = len(segment_map) - 1
        if(segment_map[ptr_start] not in [-1, SEGMENTS_NUM['Zero padding']]):
            segment_start_end.append((segment_map[ptr_start], (ptr_start, ptr_end)))
            if(segment_map[ptr_start] not in segments):
                segments.append(segment_map[ptr_start])

        for seg, points in segment_start_end:
            start, end = points
            color = SEGMENT_TO_COLOR[seg]
            ax.axvspan(start, end, color=color, alpha=0.4)
        
        for seg in sorted(segments):
            if seg == -1: continue

            patch = patches.Patch(color=SEGMENT_TO_COLOR[seg], label=SEGMENTS_STR[seg], alpha=0.4)
            legend_patches.append(patch)

        ax.legend(handles=legend_patches, loc='upper right')
        if save_path is not None:
            fig.savefig(save_path, bbox_inches='tight')

    def plot_signal_samples(self, ax=None, save_path=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(28, 3))

        ax.plot(self.signal, color='blue', linewidth=1)
        ax.scatter(self.samples, self.signal[self.samples], c='red', s=100)

        ax.set_xlabel('Nodes (point)', fontsize=20)
        ax.set_ylabel('Amplitude (mV)', fontsize=20)

        ax.xaxis.set_tick_params(labelsize=12)
        ax.yaxis.set_tick_params(labelsize=12)

        if save_path is not None:
            fig.savefig(save_path, bbox_inches='tight')
    
    def plot_segments(self, ax=None, save_path=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(28, 3))

        ax.plot(self.signal, color='blue')

        segments = []
        legend_patches = []
        
        for _, points in self.segment_start_end:
            start, end = points
            color = SEGMENT_TO_COLOR[self.segment_map[start]]
            ax.axvspan(start, end, color=color, alpha=0.4)

            if self.segment_map[start] not in segments:
                segments.append(self.segment_map[start])
        
        # make patches for existing segments
        for seg in sorted(segments):
            if seg == -1: continue

            patch = patches.Patch(color=SEGMENT_TO_COLOR[seg], label=SEGMENTS_STR[seg])
            legend_patches.append(patch)

        ax.legend(handles=legend_patches, loc='upper right')

        if save_path is not None:
            fig.savefig(save_path, bbox_inches='tight')
        
    def segmentate(self):
        segment_map = np.full(len(self.signal), -1)
        segment_start_end = []

        prev_symbol = None

        for idx_start, idx_peak, idx_end in util_func.grouped_symbols(self.symbols):
            start = self.samples[idx_start]
            peak = self.samples[idx_peak]
            end = self.samples[idx_end]

            # symbol_idx = np.where(self.samples == peak)[0][0]
            symbol_idx = idx_peak

            curr_symbol = self.symbols[symbol_idx]

            if curr_symbol == 'p':
                if prev_symbol is not None and prev_symbol == 't':
                    segment_map[prev_end:start] = SEGMENTS_NUM['Toff-Pon2']
                    segment_start_end.append((SEGMENTS_NUM['Toff-Pon2'], (prev_end, start)))

                segment_map[start:end] = SEGMENTS_NUM['Pon-Poff']
                segment_start_end.append((SEGMENTS_NUM['Pon-Poff'], (start, end)))
                

            elif curr_symbol == 'N':
                if prev_symbol == 'p':
                    segment_map[prev_end:start] = SEGMENTS_NUM['Poff-QRSon']
                    segment_start_end.append((SEGMENTS_NUM['Poff-QRSon'], (prev_end, start)))

                segment_map[start:peak] = SEGMENTS_NUM['QRSon-Rpeak']
                segment_start_end.append((SEGMENTS_NUM['QRSon-Rpeak'], (start, peak)))

                segment_map[peak:end] = SEGMENTS_NUM['Rpeak-QRSoff']
                segment_start_end.append((SEGMENTS_NUM['Rpeak-QRSoff'], (peak, end)))

            elif curr_symbol == 't':
                if prev_symbol == 'N':
                    segment_map[prev_end:start] = SEGMENTS_NUM['QRSoff-Ton']
                    segment_start_end.append((SEGMENTS_NUM['QRSoff-Ton'], (prev_end, start)))

                segment_map[start:end] = SEGMENTS_NUM['Ton-Toff']
                segment_start_end.append((SEGMENTS_NUM['Ton-Toff'], (start, end)))
            
            prev_symbol = curr_symbol
            prev_end = end
        
        return segment_map, segment_start_end


    # returns signal and segment_map
    def cut_per_beat(self):
        normal_beat_seq = [0, 1, 2, 3, 4, 5, 6] # normal beat segments sequence
        seq_to_compare = []
        p_start_ptr = 0
        t_end_ptr = 0
        prev_end = None
        beats = [] # beats list contains tuple (signal, segment_map) of each beat

        for seg, points in self.segment_start_end:
            start, end = points

            # if start - prev_end is not 0 that means theres a gap between the segment (not a normal beat)
            if(prev_end is None) or (start - prev_end == 0):
                seq_to_compare.append(seg)

            prev_end = end

            if(seg == SEGMENTS_NUM['Pon-Poff']):
                p_start_ptr = start

                seq_to_compare = [SEGMENTS_NUM['Pon-Poff']]
            
            elif(seg == SEGMENTS_NUM['Toff-Pon2']):
                t_end_ptr = end

                if(seq_to_compare == normal_beat_seq):
                    signal = self.signal[p_start_ptr:t_end_ptr]
                    segment_map = self.segment_map[p_start_ptr:t_end_ptr] 

                    beats.append((signal, segment_map))
        
        return beats

    # def cut_per_beat(self):
    #     beats = [] # beats list contains tuple (signal, segment_map) of each beat

    #     mark = 0
    #     ptr_start = 0
    #     ptr_end = 0

    #     for seg, points in self.segment_start_end:
    #         start, end = points

    #         if seg == SEGMENTS_NUM['Pon-Poff']:
    #             mark += 1
    #             ptr_start = start
    #             if mark == 1:
    #                 continue
    #             else:
    #                 mark = 0
            
    #         elif seg == SEGMENTS_NUM['Poff-QRSon']:
    #             mark += 1
    #             if mark == 2:
    #                 continue
    #             else:
    #                 mark = 0

    #         elif seg == SEGMENTS_NUM['QRSon-Rpeak']:
    #             mark += 1
    #             if mark == 3:
    #                 continue
    #             else:
    #                 mark = 0

    #         elif seg == SEGMENTS_NUM['Rpeak-QRSoff']:
    #             mark += 1
    #             if mark == 4:
    #                 continue
    #             else:
    #                 mark = 0
            
    #         elif seg == SEGMENTS_NUM['QRSoff-Ton']:
    #             mark += 1
    #             if mark == 5:
    #                 continue
    #             else:
    #                 mark = 0

    #         elif seg == SEGMENTS_NUM['Ton-Toff']:
    #             mark += 1
    #             if mark == 6:
    #                 continue
    #             else:
    #                 mark = 0

    #         elif seg == SEGMENTS_NUM['Toff-Pon2']:
    #             mark += 1
    #             if mark == 7:
    #                 ptr_end = end

    #                 signal = self.signal[ptr_start:ptr_end]
    #                 segment_map = self.segment_map[ptr_start:ptr_end]

    #                 beats.append((signal, segment_map)) 

    #                 mark = 0
    #             else:
    #                 mark = 0
        
    #     return beats

    # def cut_p_to_p(self):
    #     prev_p_start = None
    #     beats = []
    #     for seg, points in self.segment_start_end:
    #         start, _ = points

    #         if (seg == SEGMENTS_NUM['Pon-Poff']) and (prev_p_start is None):
    #             prev_p_start = start
    #             break
            
    #         elif (seg == SEGMENTS_NUM['Pon-Poff']):
    #             signal = self.signal[prev_p_start:start]
    #             segment_map = self.segment_map[prev_p_start:start]

    #             beats.append((signal, segment_map))
        
    #     return beats


            