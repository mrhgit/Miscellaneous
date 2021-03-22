import numpy as np
import argparse
import time
import sys
import os

def testmode(mode):
    mode = mode.lower()
    valid_modes = ["all","any"]
    if mode not in valid_modes:
        raise Exception("mode '{mode}' is not valid - must be one of {valid_modes}")
    return mode
def testaggr(aggr):
    try:
        aggr = min(20,max(-20,int(aggr)))
        return aggr
    except:
        raise Exception("auto-aggressiveness '{aggr}' is not valid - see usage")
    

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--input",                              type=str,   help="(REQUIRED) name of input wav file", required=True)
parser.add_argument("--output",       default="result.wav", type=str,   help="name of output wave file")
parser.add_argument("--threshold",    default="-25dB",      type=str,   help="silence threshold - can be expressed in dB, e.g. --threshold=-25.5dB")
parser.add_argument("--silence-dur",  default=0.5,          type=float, help="maximum silence duration desired in output")
parser.add_argument("--non-silence-dur", default=0.1,      type=float, help="minimum non-silence duration between periods of silence of at least --silence-dur length")
parser.add_argument("--mode",         default="all",        type=testmode,  help="silence detection mode - can be 'any' or 'all'")
parser.add_argument("--auto-threshold",action="store_true",             help="automatically determine silence threshold")
parser.add_argument("--auto-aggressiveness",default=3,type=testaggr, help="aggressiveness of the auto-threshold algorithm.  Integer between [-20,20]")
parser.add_argument("--detect-only",  action="store_true",              help="don't trim, just detect periods of silence")
parser.add_argument("--verbose",      action="store_true",              help="print general information to the screen")
parser.add_argument("--show-silence", action="store_true",              help="print locations of silence (always true if --detect-only is used)")
parser.add_argument("--time-it",      action="store_true",              help="show steps and time to complete them")
parser.add_argument("--overwrite",    action="store_true",              help="overwrite existing output file, if applicable")

args = parser.parse_args()
args.show_silence = args.show_silence or args.detect_only
if not args.detect_only and not args.overwrite:
    if os.path.isfile(args.output):
        print(f"Output file ({args.output}) already exists.  Use --overwrite to overwrite the existing file.")
        sys.exit(1)

if (args.silence_dur < 0):  raise Exception("Maximum silence duration must be >= 0.0")
if (args.non_silence_dur < 0):  raise Exception("Minimum non-silence duration must be >= 0.0")

try:
    from scipy.io import wavfile
    using_scipy = True
except:
    if args.verbose:  print("Failure using 'import scipy.io.wavfile'.  Using 'import wave' instead.")
    import wave
    using_scipy = False

if args.verbose: print(f"Inputs:\n  Input File: {args.input}\n  Output File: {args.output}\n  Max. Silence Duration: {args.silence_dur}\n  Min. Non-silence Duration: {args.non_silence_dur}")

from matplotlib import pyplot as plt
def plot(x):
    plt.figure()
    plt.plot(x,'o')
    plt.show()

def threshold_for_channel(ch):
    global data
    nbins = 100
    max_len = min(1024*1024*100,data.shape[0]) # limit to first 100 MiB
    if len(data.shape) > 1:
        x = np.abs(data[:max_len,ch]*1.0)
    else:
        x = np.abs(data[:max_len]*1.0)
    if data.dtype==np.uint8: x -= 127
    hist,edges = np.histogram(x,bins=nbins,density=True)
    slope = np.abs(hist[1:] - hist[:-1])
    argmax = np.argmax(slope < 0.00002)
    argmax = max(0,min(argmax + args.auto_aggressiveness, len(edges)-1))
    thresh = edges[argmax] + (127 if data.dtype==np.uint8 else 0)
    return thresh

def auto_threshold():
    global data
    max_thresh = 0
    channel_count = 1 if len(data.shape)==1 else data.shape[1]
    for ch in range(channel_count):
        max_thresh = max(max_thresh,threshold_for_channel(ch))
    return max_thresh
        

silence_threshold = str(args.threshold).lower().strip()
if args.auto_threshold:
    if args.verbose: print (f"  Silence Threshold: AUTO (aggressiveness={args.auto_aggressiveness})")
else:
    if "db" in silence_threshold:
        silence_threshold_db = float(silence_threshold.replace("db",""))
        silence_threshold = np.round(10**(silence_threshold_db/20.),6)
    else:
        silence_threshold = float(silence_threshold)
        silence_threshold_db = 20*np.log10(silence_threshold)

    if args.verbose: print (f"  Silence Threshold: {silence_threshold} ({np.round(silence_threshold_db,2)} dB)")
if args.verbose: print (f"  Silence Mode: {args.mode.upper()}")
if args.verbose: print("")
if args.time_it: print(f"Reading in data from {args.input}... ",end="",flush=True)
start = time.time()
if using_scipy:
    sample_rate, data = wavfile.read(args.input)
    input_dtype = data.dtype
    Ts = 1./sample_rate
    
    if args.auto_threshold:
        silence_threshold = auto_threshold()
    else:
        if data.dtype != np.float32:
            sampwidth = data.dtype.itemsize
            if (data.dtype==np.uint8):  silence_threshold += 0.5 # 8-bit unsigned PCM
            scale_factor = (256**sampwidth)/2.
            silence_threshold *= scale_factor
else:
    handled_sampwidths = [2]
    with wave.open(args.input,"rb") as wavin:
        params = wavin.getparams()
        if params.sampwidth in handled_sampwidths:
            raw_data = wavin.readframes(params.nframes)
    if params.sampwidth not in handled_sampwidths:
        print(f"Unable to handle a sample width of {params.sampwidth}")
        sys.exit(1)
end = time.time()
if args.time_it: print(f"complete (took {np.round(end-start,6)} seconds)")

if not using_scipy:
    if args.time_it: print(f"Unpacking data... ",end="",flush=True)
    start = time.time()
    Ts = 1.0/params.framerate
    if params.sampwidth==2: # 16-bit PCM
        format_ = 'h'
        data = np.frombuffer(raw_data,dtype=np.int16)
    elif params.sampwidth==3: # 24-bit PCM
        format_ = 'i'
        print(len(raw_data))
        data = np.frombuffer(raw_data,dtype=np.int32)
    
    data = data.reshape(-1,params.nchannels) # reshape into channels
    if args.auto_threshold:
        silence_threshold = auto_threshold()
    else:
        scale_factor = (256**params.sampwidth)/2. # scale to [-1:1)
        silence_threshold *= scale_factor
    data = 1.0*data # convert to np.float64
    end = time.time()
    if args.time_it: print(f"complete (took {np.round(end-start,6)} seconds)")

silence_duration_samples = args.silence_dur / Ts

if args.verbose: print(f"Input File Duration = {np.round(data.shape[0]*Ts,6)}\n")

combined_channel_silences = None
def detect_silence_in_channels():
    global combined_channel_silences
    if len(data.shape) > 1:
        if args.mode=="any":
            combined_channel_silences = np.min(np.abs(data),axis=1) <= silence_threshold
        else:
            combined_channel_silences = np.max(np.abs(data),axis=1) <= silence_threshold
    else:
        combined_channel_silences = np.abs(data) <= silence_threshold

    combined_channel_silences = np.pad(combined_channel_silences, pad_width=1,mode='constant',constant_values=0)
    
    
def get_silence_locations():
    global combined_channel_silences

    starts =  combined_channel_silences[1:] & ~combined_channel_silences[0:-1]
    ends   = ~combined_channel_silences[1:] &  combined_channel_silences[0:-1]
    start_locs = np.nonzero(starts)[0]
    end_locs   = np.nonzero(ends)[0]
    durations  = end_locs - start_locs
    long_durations = (durations > silence_duration_samples)
    long_duration_indexes = np.nonzero(long_durations)[0]
    
    if len(long_duration_indexes) > 1:
        non_silence_gaps = start_locs[long_duration_indexes[1:]] - end_locs[long_duration_indexes[:-1]]
        short_non_silence_gap_locs = np.nonzero(non_silence_gaps <= (args.non_silence_dur/Ts))[0]
        for loc in short_non_silence_gap_locs:
            if args.verbose and args.show_silence:
                ns_gap_start = end_locs[long_duration_indexes[loc]] * Ts
                ns_gap_end   = start_locs[long_duration_indexes[loc+1]] * Ts
                ns_gap_dur   = ns_gap_end - ns_gap_start
                print(f"Removing non-silence gap at {np.round(ns_gap_start,6)} seconds with duration {np.round(ns_gap_dur,6)} seconds")
            end_locs[long_duration_indexes[loc]] = end_locs[long_duration_indexes[loc+1]]
                
        long_duration_indexes = np.delete(long_duration_indexes, short_non_silence_gap_locs + 1)

    if args.show_silence:
        if len(long_duration_indexes)==0:
            if args.verbose: print("No periods of silence found")
        else:
            if args.verbose: print("Periods of silence shown below")
            fmt_str = "%-12s  %-12s  %-12s"
            print(fmt_str % ("start","end","duration"))
            for idx in long_duration_indexes:
                start = start_locs[idx]
                end = end_locs[idx]
                duration = end - start
                print(fmt_str % (np.round(start*Ts,6),np.round(end*Ts,6),np.round(duration*Ts,6)))
        if args.verbose: print("")

    return start_locs[long_duration_indexes], end_locs[long_duration_indexes]

def trim_data(start_locs,end_locs):
    global data
    if len(start_locs)==0: return
    keep_at_start = int(silence_duration_samples / 2)
    keep_at_end = int(silence_duration_samples - keep_at_start)
    start_locs = start_locs + keep_at_start
    end_locs = end_locs - keep_at_end
    delete_locs = np.concatenate([np.arange(start_locs[idx],end_locs[idx]) for idx in range(len(start_locs))])
    data = np.delete(data, delete_locs, axis=0)

def output_data(start_locs,end_locs):
    global data
    if args.verbose: print(f"Output File Duration = {np.round(data.shape[0]*Ts,6)}\n")
    if args.time_it: print(f"Writing out data to {args.output}... ",end="",flush=True)
    if using_scipy:
        wavfile.write(args.output, sample_rate, data)
    else:
        packed_buf = data.astype(format_).tobytes()
        with wave.open(args.output,"wb") as wavout:
            wavout.setparams(params) # same params as input
            wavout.writeframes(packed_buf)

start = time.time()
if not args.verbose and args.time_it: print("Detecting silence... ",end="",flush=True)
detect_silence_in_channels()
(start_locs,end_locs) = get_silence_locations()
end = time.time()
if not args.verbose and args.time_it: print(f"complete (took {np.round(end-start,6)} seconds)")

if args.detect_only:
    if args.verbose: print("Not trimming, because 'detect only' flag was set")
else:
    if args.time_it: print("Trimming data... ",end="",flush=True)
    start = time.time()
    trim_data(start_locs,end_locs)
    end = time.time()
    if args.time_it: print(f"complete (took {np.round(end-start,6)} seconds)")
    start = time.time()
    output_data(start_locs, end_locs)
    end = time.time()
    if args.time_it: print(f"complete (took {np.round(end-start,6)} seconds)")

