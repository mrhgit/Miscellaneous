import numpy as np
from scipy.io import wavfile

# Params
(infile,outfile,threshold_db,silence_dur,non_silence_dur,mode) = ("test_stereo.wav","result.wav",-25,0.5,0.1,"all")
silence_threshold = np.round(10**(threshold_db/20.),6) * 32768 # Convert from dB to linear units and scale, assuming 16-bit PCM input

# Read data
Fs, data = wavfile.read(infile)
silence_duration_samples = silence_dur * Fs
if len(data.shape)==1: data = np.expand_dims(data,axis=1)

# Find silence
find_func = np.min if mode=="any" else np.max
combined_channel_silences = find_func(np.abs(data),axis=1) <= silence_threshold
combined_channel_silences = np.pad(combined_channel_silences, pad_width=1,mode='constant',constant_values=0)

# Get start and stop locations
starts =  combined_channel_silences[1:] & ~combined_channel_silences[0:-1]
ends   = ~combined_channel_silences[1:] &  combined_channel_silences[0:-1]
start_locs = np.nonzero(starts)[0]
end_locs   = np.nonzero(ends)[0]
durations  = end_locs - start_locs
long_durations = (durations > silence_duration_samples)
long_duration_indexes = np.nonzero(long_durations)[0]
    
# Cut out short non-silence between silence
if len(long_duration_indexes) > 1:
    non_silence_gaps = start_locs[long_duration_indexes[1:]] - end_locs[long_duration_indexes[:-1]]
    short_non_silence_gap_locs = np.nonzero(non_silence_gaps <= (non_silence_dur * Fs))[0]
    for loc in short_non_silence_gap_locs:
        end_locs[long_duration_indexes[loc]] = end_locs[long_duration_indexes[loc+1]]
    long_duration_indexes = np.delete(long_duration_indexes, short_non_silence_gap_locs + 1)

    (start_locs,end_locs) = (start_locs[long_duration_indexes], end_locs[long_duration_indexes])

# Trim data
if len(long_duration_indexes) > 1:
    if len(start_locs) > 0:
        keep_at_start = int(silence_duration_samples / 2)
        keep_at_end = int(silence_duration_samples - keep_at_start)
        start_locs = start_locs + keep_at_start
        end_locs = end_locs - keep_at_end
        delete_locs = np.concatenate([np.arange(start_locs[idx],end_locs[idx]) for idx in range(len(start_locs))])
        data = np.delete(data, delete_locs, axis=0)

# Output data
wavfile.write(outfile, Fs, data)

