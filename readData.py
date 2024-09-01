import numpy as np
import matplotlib.pyplot as plt

class IQFile:
    def __init__(self, file_path, sample_rate=1000000, complex_data_type=np.complex64):
        """
        Initializes the IQFile object.

        Args:
            file_path: Path to the IQ file.
            sample_rate: Sample rate of the IQ data.
            complex_data_type: NumPy data type for complex numbers (default: np.complex64).
        """
        self.file_path = file_path
        self.sample_rate = sample_rate
        self.complex_data_type = complex_data_type
        self.data = None

    def read(self):
        """
        Reads the IQ data from the file and stores it in the `data` attribute.
        """
        with open(self.file_path, 'rb') as f:
            data = np.fromfile(f, dtype=self.complex_data_type)
            self.data = data

    def print_info(self):
        """
        Prints information about the IQ data.
        """
        if self.data is None:
            print("IQ data not loaded yet. Please call read() first.")
            return

        print("File Path:", self.file_path)
        print("Sample Rate:", self.sample_rate)
        print("Data Type:", self.complex_data_type)
        print("Number of Samples:", len(self.data))
        print("Data Shape:", self.data.shape)
        print("Number of packets:", len(self.data)/8192)
        
    def get_data(self):
        """
        Returns the IQ data as a NumPy array.
        """
        return self.data
    
    def plot(self, num_samples=None, title=""):
        """
        Plots the IQ data.

        Args:
            num_samples: Number of samples to plot (default: None, plot all).
        """
        if self.data is None:
            print("IQ data not loaded yet. Please call read() first.")
            return

        if num_samples is None:
            num_samples = len(self.data)

        time = np.arange(num_samples) / self.sample_rate

        # Plot I and Q components
        plt.title(title)
        plt.plot(time, self.data[:num_samples].real, label='I')
        plt.plot(time, self.data[:num_samples].imag, label='Q')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.show()
    
    
if __name__ == '__main__':
    modulationTypes = ['8PSK', '16QAM', '64QAM', 'B-FM', 'BPSK', 'CPFSK', 'DSB-AM', 'GFSK', 'PAM4', 'QPSK', 'SSB-AM']
    nodes = ["friendship", "behavioral"]
    dataFolder = "/Users/josea/Documents/powder/"
    for node in nodes:
        print(node)
        for modulation in modulationTypes:
            print(modulation)
            iqFile = IQFile(file_path=dataFolder+node+"/tmp/"+modulation+".iq")
            iqFile.read()
            iqFile.print_info()
            iqFile.plot(num_samples=8192*4, title=node+" node "+modulation+" IQ samples graph")
            