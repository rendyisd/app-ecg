import os
import wfdb
import wfdb.processing
import wfdb.processing.peaks
import numpy as np
import math
import tensorflow as tf
import matplotlib.pyplot as plt

from matplotlib.lines import Line2D

from detection import util_func
from detection.ecg_signal import ECGSignal

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

INPUT_LENGTH = 816

FS = 500
T1 = 125
T2 = 245

MIN_BPM = 20
MAX_BPM = 230

SEARCH_RADIUS = int(FS * 60 / MAX_BPM)

WAVELET_FUNCTION = 'bior3.3'
DECOMPOSITION_LEVEL = 7

INTERPRETATION_TO_NUM = {
    'Neither': 0,
    'ST-elevation': 1,
    'ST-depression': 2
}

def detection(record_path, lead, result_root_path):
    record = wfdb.rdrecord(record_path)
    model = tf.keras.models.load_model(f"detection/delineation-models/{lead}-CustomModel.h5")
    
    signal = record.p_signal[:, record.sig_name.index(lead)]
    denoised_signal = util_func.denoise_dwt(signal, WAVELET_FUNCTION, DECOMPOSITION_LEVEL)
    preprocessed_signal = wfdb.processing.normalize_bound(denoised_signal)

    index_qrs = wfdb.processing.gqrs_detect(signal, FS)

    if len(index_qrs) == 0:
        print("Can't detect QRS")
        return
    
    corrected_peak_inds = wfdb.processing.peaks.correct_peaks(
        signal,
        peak_inds=index_qrs,
        search_radius=SEARCH_RADIUS,
        smooth_window_size=150
    )

    if len(corrected_peak_inds) % 2 != 0:
        corrected_peak_inds = np.delete(corrected_peak_inds, -1)
    
    offset = 0
    denoised_beats = []

    beat_interpretations = []

    for i, peak in enumerate(corrected_peak_inds):
        if (peak - T1) < 0 or (peak + T2) > len(signal):
            continue

        denoised_beat = denoised_signal[peak - T1 : peak + T2]
        beat = preprocessed_signal[peak - T1 : peak + T2]

        beat = np.pad(beat, (0, INPUT_LENGTH - len(beat)))
        beat = beat.reshape((1, -1, 1))

        y_pred = model.predict(beat, verbose=0)
        y_pred = y_pred.round().reshape((INPUT_LENGTH, 8))
        y_pred = y_pred.argmax(axis=1)

        beat = beat.flatten()

        beat, y_pred = util_func.remove_zero_padding(beat, y_pred)

        segment_start_end = util_func.get_segment_start_end(y_pred)

        denoised_beats.extend(denoised_beat)
    
        try:
            st_segment = segment_start_end[4][0]
            tp_segment = segment_start_end[6][0]
        except:
            print(f'Detection failed.')
        
        j_point_amp = denoised_beat[st_segment[0]]
        baseline_amp = np.mean(util_func.moving_average(denoised_beat[tp_segment[0]:tp_segment[1]+1], 50))

        if j_point_amp - baseline_amp >= 0.1: # Universal ST elevation rules
            beat_interpretation = INTERPRETATION_TO_NUM['ST-elevation']
        
        elif j_point_amp < baseline_amp: # ST depression rules
            beat_interpretation = INTERPRETATION_TO_NUM['ST-depression']
        
        else:
            beat_interpretation = INTERPRETATION_TO_NUM['Neither']
        
        beat_interpretations.append( 
            (beat_interpretation, (offset, offset + len(beat))) 
        )
        offset += len(beat)

        plot_jpoint_baseline(
            denoised_beat,
            y_pred,
            st_segment,
            j_point_amp,
            baseline_amp,
            beat_interpretation,
            f"{os.path.basename(os.path.normpath(result_root_path))}_{i}",
            os.path.join(result_root_path, "result")
        )
    
    plot_all_detection(
        denoised_beats,
        beat_interpretations,
        os.path.basename(os.path.normpath(result_root_path)),
        os.path.join(result_root_path, "result")
    )


def plot_jpoint_baseline(beat, y_pred, st_segment, j_point_amp, baseline_amp, beat_interpretation, unique_name, save_dir):
    fig, ax = plt.subplots(figsize=(28, 5))
    
    fig.suptitle(f"{unique_name}")
    ax.set_title(f"J-point ({j_point_amp}) - Baseline ({baseline_amp}) = {j_point_amp-baseline_amp} ({beat_interpretation})")

    ECGSignal.plot_signal_segments(beat, y_pred, ax=ax)

    ax.axhline(y=baseline_amp, color='gray', linestyle='-', linewidth=4)
    ax.plot(st_segment[0], j_point_amp, 'o', color='black', markersize=10)
    ax.set_yticks(np.arange(
        (math.floor(np.min(beat) * 10) / 10) + 0.1,
        (math.ceil(np.max(beat) * 10) / 10) + 0.1,
        0.1)
    )

    ax.set_xlabel('Nodes (point)', fontsize=20)
    ax.set_ylabel('Amplitude (mV)', fontsize=20)

    legend_patches = [
        Line2D([0], [0], label='Isoelectric line', color='gray', linewidth=4),
        Line2D([0], [0], marker='o', label='J-Point', color='w', markerfacecolor='black', markersize=10),
    ]
    leg1 = ax.get_legend()
    leg2 = ax.legend(handles=legend_patches, loc='lower right', fontsize=18)
    ax.add_artist(leg1)
    ax.grid()

    fig.savefig(os.path.join(save_dir, f"{unique_name}"), bbox_inches='tight')


def plot_all_detection(denoised_beats, beat_interpretations, unique_name, save_dir):
    fig, ax = plt.subplots(figsize=(28, 5))

    beat_plot_colors = ['blue', 'red', 'limegreen']

    ax.plot(denoised_beats, color='blue', linewidth=1)
    for interpretation, beat_start_end in beat_interpretations:
        if (interpretation == INTERPRETATION_TO_NUM['ST-elevation']) \
            or (interpretation == INTERPRETATION_TO_NUM['ST-depression']):

            start, end = beat_start_end

            ax.plot(range(start, end), denoised_beats[start:end], color=beat_plot_colors[interpretation], linewidth=2)

    ax.set_xlabel('Nodes (point)', fontsize=20)
    ax.set_ylabel('Amplitude (mV)', fontsize=20)

    ax.set_yticks(np.arange(
        (math.floor(np.min(denoised_beats) * 10) / 10),
        (math.ceil(np.max(denoised_beats) * 10) / 10),
        0.1)
    )
    ax.grid()
    legend_patches = [
        Line2D([0], [0], label='Neither', color=beat_plot_colors[0], linewidth=1),
        Line2D([0], [0], label='ST-elevation', color=beat_plot_colors[1], linewidth=2),
        Line2D([0], [0], label='ST-depression', color=beat_plot_colors[2], linewidth=2)
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=18)

    ax.xaxis.set_tick_params(labelsize=14)
    ax.yaxis.set_tick_params(labelsize=14)
    ax.set_title(f'{unique_name}', weight='bold', fontsize=22)

    fig.savefig(os.path.join(save_dir, f"{unique_name}"), bbox_inches='tight')