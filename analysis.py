import numpy as np
import os
import subprocess
import audioflux as af
from audioflux.type import SpectralDataType, SpectralFilterBankScaleType

class Corpus:
    """ 
    Class for audio and audio repo's. For now
    focusing on just wav file processing. 
    """
    def __init__(self, path):
        self.path= path
        self.sr = None
        self.name = self.__class__.__name__
        self.metadata = None #path to metadata subfolder
        # self.analyses = []
        # self.slices = {}
    
    def check_metadata(self):
        if os.path.exists(""):
            pass
        
    def get_slices(self):

        """ 
        Use static or dynamic slicing to get starting 
        indices of grains. 
        """
        

        pass
    
    def analyze_grains(self, descriptors):
        """  
        descriptors: a list of the descriptors to be computed. I.e.
        ["centroid", "energy", "rms"]

        Compute (sub)set of all descriptors for the grains.
        Outputs metadata corresponding to these descriptors in csv or json. 

        idea: a perpetually updated csv/ json file where unique grains are 
            added with their unique descriptor values
        Think of what way would make most sense to store data pertaining to 
        some field recording. 

        A grain might be represented as a row, with its slicing type, recording id, centroid etc,
        """
        pass


def compute_spectral_descriptors(file_path, sr, output_dir, grain_size):
    """
    grain_size: in samples (consider the sample rate)
    """
    y, sr = af.read(file_path)
    audio_len = len(y)
    slice_indices = np.array(
        [i*grain_size for i in range(audio_len//grain_size)]
    )
    
    if y.ndim > 1:
        y=np.mean(y, axis=1)
        
    grains_descriptors = []
    for index in slice_indices:
        grain_end = index+grain_size # 1ms to 100ms
        if grain_end > audio_len:
            grain_end = audio_len
        s, e = index, grain_end
        grain = y[s: e]
        # print(grain)
        bft_obj = af.BFT(num=64, samplate=sr, radix2_exp=7,
                    data_type=SpectralDataType.MAG,
                    scale_type=SpectralFilterBankScaleType.LINEAR)
        spec_arr = bft_obj.bft(grain)
        spec_arr = np.abs(spec_arr)
        
        # Create Spectral object and extract spectral feature
        spectral_obj = af.Spectral(num=bft_obj.num,
                                fre_band_arr=bft_obj.get_fre_band_arr())
        spectral_obj.set_time_length(spec_arr.shape[-1])
        
        d ={
            "source_id": 0,
            "grain_start": int(s),
            "grain_size": len(grain),
            "centroid": float(np.mean(spectral_obj.centroid(spec_arr))),
            # "flatness": float(np.mean(spectral_obj.flatness(spec_arr))),
            # "kurtosis": float(np.mean(spectral_obj.kurtosis(spec_arr))),
            "flux": float(np.mean(spectral_obj.flux(spec_arr))),
            "energy": float(np.mean(spectral_obj.energy(spec_arr))),
            # "crest": float(np.mean(spectral_obj.crest(spec_arr))),
            "rms": float(np.mean(spectral_obj.rms(spec_arr))),
            # "eef": float(np.mean(spectral_obj.eef(spec_arr))),
            # "eer": float(np.mean(spectral_obj.eer(spec_arr))),
            # "band_width": float(np.mean(spectral_obj.band_width(spec_arr))),
            # "decrease": float(np.mean(spectral_obj.decrease(spec_arr))),
            "entropy": float(np.mean(spectral_obj.entropy(spec_arr))),
            "spread": float(np.mean(spectral_obj.spread(spec_arr))),
            # "slope": float(np.mean(spectral_obj.slope(spec_arr)))
        }
        grains_descriptors.append(d)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    path = os.path.join(output_dir, f"{file_path[7:-4]}.json")
    with open(path, "w") as f:
        # json.dump(grains_descriptors, f, indent=4)
        pass
    # print(f"Saved {len(df)} grains to {output_parquet}")

# compute_spectral_descriptors(FILE_PATH, "metadata", 10)


""" 
AmpSlicerl, OnsetSlicer are Flucoma slicers from the CLI toolset. 
AmpSlicer slices based on amplitude shifts in the spectral representation
of the sound. 
OnsetSlicer _

"""

class AmpSlicer:
    EXE = "fluid-ampslice"
    def __init__(
        self,
        fastrampdown=1,
        fastrampup=1,
        floor=-144.0,
        highpassfreq=85.0,
        minslicelength=2,
        numchans=-1,
        numframes=-1,
        offthreshold=-144.0,
        onthreshold=144.0,
        slowrampdown=100,
        slowrampup=100,
        startchan=0,
        startframe=0,
        warnings=0
    ):
        self.fastrampdown = fastrampdown
        self.fastrampup = fastrampup
        self.floor = floor
        self.highpassfreq = highpassfreq
        self.minslicelength = minslicelength
        self.numchans = numchans
        self.numframes = numframes
        self.offthreshold = offthreshold
        self.onthreshold = onthreshold
        self.slowrampdown = slowrampdown
        self.slowrampup = slowrampup
        self.startchan = startchan
        self.startframe = startframe
        # self.warnings = warnings

        self.name = self.__class__.__name__

    
    def run(self, output, source):
        """ 
        Output should be a csv file. Source is the (Corpus object)
        """
        print(source.path)
        command = [
            self.EXE,
            "-source", str(source.path),
            "-indices", str(output), 
            "-fastrampdown", str(self.fastrampdown),
            "-fastrampup", str(self.fastrampup),
            "-floor", str(self.floor),
            "-highpassfreq", str(self.highpassfreq),
            "-minslicelength", str(self.minslicelength),
            "-numchans", str(self.numchans),
            "-numframes", str(self.numframes),
            "-offthreshold", str(self.offthreshold),
            "-onthreshold", str(self.onthreshold),
            "-slowrampdown", str(self.slowrampdown),
            "-slowrampup", str(self.slowrampup),
            "-startchan", str(self.startchan),
            "-startframe", str(self.startframe)
        ]
        try:
            result = subprocess.run(
                command, 
                check=True,          # Raises CalledProcessError if the exit code is non-zero
                capture_output=True, # Captures stdout and stderr
                text=True            # Returns output as strings instead of bytes
            )
            print("Command Output:\n", result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running fluid-noveltyslice: {e}")
            print("Error details:", e.stderr)

        source.slices[source.name] = source.slices.get(source.name, []).append({output: self})


class OnsetSlicer:
    EXE = "fluid-onsetslice"

    def __init__(
        self,
        fftsettings=[1024, -1, -1],
        filtersize=5,
        framedelta=0,
        maxfftsize=-1,
        metric=0,
        minslicelength=2,
        numchans=-1,
        numframes=-1,
        startchan=0,
        startframe=0,
        threshold=0.5,
        warnings=0
    ):
        self.fftsettings = fftsettings
        self.filtersize = filtersize
        self.framedelta = framedelta
        # self.indices = indices
        self.maxfftsize = maxfftsize
        self.metric = metric
        self.minslicelength = minslicelength
        self.numchans = numchans
        self.numframes = numframes
        # self.source = source
        self.startchan = startchan
        self.startframe = startframe
        self.threshold = threshold
        self.warnings = warnings

        self.name = self.__class__.__name__

    def run(self, source, indices):
            """Constructs and executes the fluid-onsetslice command."""
            cmd = [self.EXE]

            # if self.fftsettings:
            #     cmd.append("-fftsettings")
            #     cmd.extend(map(str, self.fftsettings))

            options = {
                # "-filtersize": self.filtersize,
                # "-framedelta": self.framedelta,
                "-indices": indices,
                # "-maxfftsize": self.maxfftsize,
                # "-metric": self.metric,
                # "-minslicelength": self.minslicelength,
                # "-numchans": self.numchans,
                # "-numframes": self.numframes,
                "-source": source,
                # "-startchan": self.startchan,
                # "-startframe": self.startframe,
                # "-threshold": self.threshold,
                # "-warnings": self.warnings,
            }

            for flag, value in options.items():
                if value is not None:
                    cmd.append(flag)
                    cmd.append(str(value))

            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error: {result.stderr}")
                return result.stdout
            except FileNotFoundError:
                print(f"Executable {self.EXE} not found in PATH.")