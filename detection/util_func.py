import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pywt

from datetime import datetime

from sklearn.model_selection import train_test_split
# from scipy import stats

# from detection.ecg_signal import ECGSignal

# Helper
def grouped_symbols(symbols):
    indices = []
    for i in range(len(symbols)):
        if (symbols[i] == 'p') or (symbols[i] == 'N') or (symbols[i] == 't'):
            if (symbols[i-1] == '(') and (symbols[i+1] == ')'):
                indices.append((i-1, i, i+1))
        
    return indices



def save_file(fpath, data):
    with open(fpath, 'wb') as f:
        pickle.dump(data, f)

def open_pickle(fpath):
    with open(fpath, 'rb') as f:
        return pickle.load(f)
    
def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)\

# Fixed for 80% train, 10% val, 10% test
def train_val_test_split(X, y):
    # these should sum to 1
    train_ratio = 0.8
    val_ratio = 0.1
    test_ratio = 0.1

    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=test_ratio, shuffle=False, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=val_ratio/(train_ratio+test_ratio), shuffle=False, random_state=42)

    return X_train, X_val, X_test, y_train, y_val, y_test

def get_x_y(pickle_path):
    data = open_pickle(pickle_path)
    df = pd.DataFrame(data=data)

    features = df.loc[:, df.columns != 'segment_map']
    y = df.loc[:, 'segment_map']

    features_train, features_val, features_test, y_train, y_val, y_test = train_val_test_split(features, y)

    # Really weird workaround to convert these from dtype object to dtype float
    X_train = np.array(features_train['signal'].tolist())
    X_val = np.array(features_val['signal'].tolist())
    X_test = np.array(features_test['signal'].tolist())
    y_train = np.array(y_train.tolist())
    y_val = np.array(y_val.tolist())
    y_test = np.array(y_test.tolist())
    zpad_length_train = features_train['zpad_length'].values
    zpad_length_val = features_val['zpad_length'].values
    zpad_length_test = features_test['zpad_length'].values

    train_set = (X_train, y_train)
    val_set = (X_val, y_val)
    test_set = (X_test, y_test)
    zpad_length = (zpad_length_train, zpad_length_val, zpad_length_test)

    return train_set, val_set, test_set, zpad_length

def ValSUREThresh(X):
        noise_var = np.median(np.abs(X)) / 0.6745  # Assuming Gaussian noise
        universal = np.sqrt(2 * np.log(len(X)))

        # Calculate the SURE threshold
        sure_threshold = universal * noise_var

        return sure_threshold

def denoise_dwt(signal, wavelet, level):
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    '''
    As per the pywt.wavedec docs:
    coeffs[0] contains approximation coeffs and the rest are detail coeffs
    '''

    threshold = ValSUREThresh(coeffs[-1])
    # threshold = stats.median_abs_deviation(coeffs[0]) * np.sqrt(2 * np.log(len(signal))) # universtal threshold

    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], value=threshold, mode="soft")

    new_signal = pywt.waverec(coeffs, wavelet=wavelet)

    return new_signal

def calculate_snr(original_signal, denoised_signal):
    if len(original_signal) != len(denoised_signal):
        raise ValueError("Original and denoised signal must have the same length")
    
    original_signal = np.asarray(original_signal)
    denoised_signal = np.asarray(denoised_signal)

    original_sq = np.sum(original_signal ** 2)

    noise = original_signal - denoised_signal
    noise_sq = np.sum(noise ** 2)

    # result in decibels
    snr = 10 * np.log10(original_sq / noise_sq)

    return snr

# def plot_rhytm(X, y, zpad, start_idx, length=5, ax=None, save_path=None):
#     all_signal = []
#     all_segment_map = []

#     # 1 rhytm = 5 beats hence the default length is 5
#     for i in range(length):
#         signal = X[start_idx+i].flatten()
#         segment_map = y[start_idx+i].argmax(axis=1)
        
#         if zpad is not None:
#             beat_span = len(signal) - zpad[start_idx+i]
#             all_signal.extend(signal[:beat_span])
#             all_segment_map.extend(segment_map[:beat_span])
#         else:
#             all_signal.extend(signal)
#             all_segment_map.extend(segment_map)

#     ax = ECGSignal.plot_signal_segments(all_signal, all_segment_map, ax, save_path)

#     return ax

# def plot_rhytm_gt_pred(X, y, y_pred, zpad, start_idx,  fig_title, length=5, save_path=None):
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(28, 6))

#     plot_rhytm(X, y, zpad=zpad, start_idx=start_idx, length=length, ax=ax1)
#     plot_rhytm(X, y_pred, zpad=zpad, start_idx=start_idx, length=length, ax=ax2)

#     ax1.get_legend().remove()
#     ax1.set_xticks([])
#     ax1.set_yticks([])
#     ax1.set_xlabel('')
#     ax1.set_ylabel('Ground Truth', fontsize=16)

#     ax2.get_legend().remove()
#     ax2.set_xticks([])
#     ax2.set_yticks([])
#     ax2.set_xlabel('')
#     ax2.set_ylabel('Prediction', fontsize=16)

#     fig.suptitle(fig_title, fontsize=18, fontweight='bold')
#     fig.subplots_adjust(hspace=0, top=0.9)
#     if save_path is not None:
#         fig.savefig(save_path, bbox_inches='tight')


def find_island_boundaries(arr, island_value, include_stop=True):
    if isinstance(arr, list):
        arr = np.array(arr)
        
    extended_arr = np.r_[False, arr == island_value, False]

    transition_indices = np.flatnonzero(extended_arr[:-1] != extended_arr[1:])

    island_lengths = transition_indices[1::2] - transition_indices[:-1:2]

    stop_indices = transition_indices[1::2] - int(include_stop)
    island_boundaries = list(zip(transition_indices[:-1:2], stop_indices))

    return transition_indices[:-1:2], island_boundaries, island_lengths

def get_segment_start_end(y_pred):
    predictions = {}
    for label in range(8):
        predictions[label] = find_island_boundaries(y_pred, label)[1]
    return predictions

def get_lead_display_name(lead):
    lead_dict = {
        'avr': 'aVR',
        'avl': 'aVL',
        'avf': 'aVF'
    }

    if (lead == 'avr') or (lead == 'avl') or (lead == 'avf'):
        return lead_dict[lead]
    else:
        return lead.upper()

def remove_zero_padding(signal, y_pred):
    assert signal.shape == y_pred.shape

    nonzero = np.where(y_pred != 7)[0]
    new_signal = signal[nonzero]
    new_y = y_pred[nonzero]

    assert new_signal.shape == new_y.shape

    return new_signal, new_y

def moving_average(signal, window_size=50): # default 1/10 sampling frequency
    kernel = np.ones(window_size) / window_size

    return np.convolve(signal, kernel, mode='valid')