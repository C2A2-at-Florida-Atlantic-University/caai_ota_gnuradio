#!/usr/bin/python

"""
This profile allows the allocation of resources for over-the-air
operation on the POWDER platform. Specifically, the profile has
options to request the allocation of SDR radios in rooftop 
base-stations.

Map of deployment is here:
https://www.powderwireless.net/map

This profile works with the CBRS band (3550 - 3700 MHz) NI/Ettus X310
base-station radios in POWDER.  The naming scheme for these radios is
cbrssdr1-&lt;location&gt;, where 'location' is one of the rooftop names
shown in the above map. Each X310 is paired with a compute node (by default
a Dell d740).

The instructions below shows how GNU Radio software can be used
with SDRs connected to the CBRS antennas to transmit and receive
a file with QPSK over OFDM.

A good node pair to use is:

  * **South Medical Tower (SMT)** and **Honors**

A full set of test results to help in picking devices is located here:

https://docs.google.com/spreadsheets/d/e/2PACX-1vS95aVITSZnZ2gPk4aMnNLrtbV8QgY4_HP93njVN8UcOz5fFLNAadiBp72BcD_epV-WfJWUY9sWpQ2U/pubhtml

(Some devices may not be available due to maintenance, etc.)

Instructions:

#### Overview

We will use one of the nodes in your experiment as the transmitter and
the other as the receiver.

#### SSH to the nodes

1. Once the profile is instantiated, go to `List View` option to get the node address.
2. With a remote SSH client login to the nodes. (Must have SSH public key uploaded).
3. While using SSH, make sure the X11 forwarding option is enable (-Y option).

#### On the transmitter node: Open and edit flowgraph in GNU Radio Companion

GNU Radio provides the building blocks for OFDM modulated signal. We will use these blocks for this experiment.

1. Open transmitter file 
```
bash -l
gnuradio-companion /local/repository/gnuradio/TX.grc
```
2. (Optional) Save the file in your user directory: /users/&lt;username&gt;/ if you'd like to edit it.
3. The transmitter is now ready to transmit with default configuration.

_Note:_ You may also simply use `/local/repository/gnuradio/OFDM_TX.py` if you'd rather not start up gnuradio-companion.

##### Brief description of the transmitter blocks

1. **File Source** : Contains the file we want to transmit (image/text/..)
Now we have streams of bytes as output without any boundary that defines the start/end of the packet.

2. **Stream to tagged stream** : Is the block that defines the packet boundary. It converts a regular stream to tagged stream. All this block does is add a length tag 'packet_len' with a value 30 (or as you provide). Which means after every 30 items there will be a tag called 'packet_len'.

3. **Stream CRC32** : The first byte of the packet has a tag 'packet_len' with value 30 which means the number of bytes in the packet. The output is the same as input with a trailing CRC32 (4 bytes) of the packet. The tag is also now reset to the new length.
This is now the payload that we want to transmit. At this step the flow splits up. The top path is for header generator and the bottom is the payload itself.

4. **Protocol Formatter** : Takes in the tagged stream packet and creates a header. This is configurable. In flowgraph, the format object points to an object 'hdr_format'  that we pass to the block. So the block has the conceptual idea on what it does but how it is done is implemented somewhere else. So its something that we do in python code. We generate a OFDM packet header, giving some information on what I want to do. So the right side, it calculates & generates the header and outputs it on this channel. The other channel is used to transport the payload.

5. **Repack bits** : Prepares for modulation (8 bits to 1 bit) for BPSK and (8 bits to 2 bits) for QPSK.
6. **Virtual Sink** : When paired with a Virtual Source block, this is essentially the same as drawing a wire between two blocks. This block can be useful for tidying up a complex flowgraph.
7. **Chunks to symbols** : Maps bits to complex symbols. Both the paths can have different modulation scheme. Here we have done BPSK for header and QPSK for payload. After this we have complex symbols.
8. **Tagged Stream MUX** : Multiplexer : Which still understand packet boundaries. Packets are output sequentially from each input stream. As the input might have different length. The output signal has a new length tag which is the sum of all individual length tags.

9. **OFDM Carrier allocator** : Allocates the sub-carriers/pilot carriers that will be occupied by data or pilot symbols. Add sync words.
10. **IFFT** : Converts frequency into time domain.
11. **OFDM cyclic Prefixer** : Adds guard interval. 
12. **Multiply constant** : reduces the amplitude so that it is within [-1 : +1] range to avoid clipping.
13. **USRP Sink** : Connects to the antenna
    
#### Receiver node: Open and edit flowgraph in GNU Radio Companion

1. Open receiver file
```
bash -l
gnuradio-companion /local/repository/gnuradio/RX.grc
```
2. (Optional) Save the file in /users/&lt;username&gt;/ if you'd like to edit it.

3. The receiver is now ready to receive and decode the message sent by the transmitter via OFDM (into /tmp/rx.txt).

_Note:_ You may also simply use `/local/repository/gnuradio/OFDM_RX.py` if you'd rather not start up gnuradio-companion.

##### Brief description of the receciver blocks

1. **USRP Source** : Connects to the receiver antenna. Outputs complex samples to process.

2. **Schmidl & Cox OFDM synchronization** : Used for timing synchronization to detect the start of the packet and frequency offset correction with the preambles (sync words).

3. **Header/Payload Demux** : Demultilexes the header and payload. It takes in the received signal in the incoming port and drops until a trigger (high signal- non zero, Schmidl & Cox OFDM synchronization finds out the position for packet start) value is received. Once it is triggered the sample are passed to the outgoing port 0. As the length of the header is always knwon/fixed it pipes in the fixed number of header into the first sub-flow to demodulate the header. Once the header is demodulated it feeds back the payload information (eg. length of the payload) so that the payload can be demodulated in the second sub-flow.

4. **FFT** : Convert time to frequency domain.

5. **OFDM Channel Estimation** : Calculates channel state with sync words. 

6. **OFDM Frame Equalizer** : Reverses the effect of channel on the received symbol.

7. **OFDM Serializer** : Inverse block of carrier allocator. It discard the pilot symbols and output the data symbols.

8. **Constellation Decoder** : Decodes constillation points into bits.

9. **Packet Header Parser** : Inverse of packet header generator in transmitter. It posts header metadata as a message to the Header Payload demux block.

#### Execute the flowgraph

1. Execute the `receiver` file first by clicking Execute/F6 button on the toolbar. 
2. Execute the `transmiter` file.
2. The signal can be viewed in Time/Frequency domain if QT GUI blocks are added after USRP Source at receiver.
3. Hit Kill button or F7 to stop the transmitter/receiver flow after few seconds.
4. Open a new terminal for the receive node and open the the received file.
```
vim /users/username/rx.txt
```
5. Basic Parameters that you can modify to check performance: Gain (Tx/Rx), Sampling rate, Bandwidth

#### Calculate Packet Error Rate

The `Packet header parser` outputs the metadata of the header. We can use a `Message Debug` block to save the output to a file on the receiver.

1. Open your copy of RX.grc with gnuradio-companion (if it isn't already open).
2. Use the search option in the toolbar to find `Message debug block` from the right tree panel.
3. Drag and drop the corresponding block in the working panel.
4. Connect the ouput port of 'Packet Header' parser block to the print port of 'Message Debug' block.
5. Click on `Generate the flow graph` button on the toolbar to save the flow as a python script.
6. Run the python script generated from the .grc file in receiver. Direct the output to be saved in a text file.
```
python /path/to/your/OFDM_TX_RX_1.py >> header.txt
```
7. Execute the transmitter (as described previously)

8. Make a copy of the python script PER.py to whereever your `header.txt` file is located.
```
cp /proj/mww2019/gnuradio-ofdm-example/PER.py /path/to/header/file/..
```

9. Run python script to calculate PER
```
python3 PER.py
```

"""

# Library imports
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.igext as ig


# Global Variables
x310_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"
meas_disk_image = \
        "urn:publicid:IDN+emulab.net+image+PowderTeam:U18-GR-PBUF"
setup_command = "/local/repository/startup.sh"
installs = ["gnuradio"]
nuc_image = meas_disk_image

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Start VNC?
portal.context.defineParameter("start_vnc", 
                               "Start X11 VNC on all compute nodes",
                               portal.ParameterType.BOOLEAN, True)

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(idx, x310_radio_name, node_type, installs):
    radio_link = request.Link("radio-link-%d" % idx)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_disk_image

    service_command = " ".join([setup_command] + installs)
    node.addService(rspec.Execute(shell="bash", command=service_command))

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("%s-x310" % x310_radio_name)
    radio.component_id = x310_radio_name
    radio_link.addNode(radio)

def b210_node_pair(b210_radio_name, component_manager_id):
    nuc = ""
    nuc = request.RawPC("%s-b210" % b210_radio_name)
    nuc.component_manager_id = component_manager_id
    nuc.component_id = "nuc2"
    nuc.disk_image = nuc_image
    if params.start_vnc:
        nuc.startVNC()

# Node type parameter for PCs to be paired with X310 radios.
# Restricted to those that are known to work well with them.
portal.context.defineParameter(
    "nodetype",
    "Compute node type",
    portal.ParameterType.STRING, "d740",
    ["d740","d430"],
    "Type of compute node to be paired with the X310 Radios",
)

# List of CBRS rooftop X310 radios.
rooftop_names = [
    ("cbrssdr1-bes",
     "Behavioral"),
    ("cbrssdr1-browning",
     "Browning"),
    ("cbrssdr1-dentistry",
     "Dentistry"),
    ("cbrssdr1-fm",
     "Friendship Manor"),
    ("cbrssdr1-honors",
     "Honors"),
    ("cbrssdr1-meb",
     "MEB"),
    ("cbrssdr1-smt",
     "SMT"),
    ("cbrssdr1-ustar",
     "USTAR"),
]

# A list of fixed endpoint sites.
fe_names = [
    ('urn:publicid:IDN+bookstore.powderwireless.net+authority+cm',
     "Bookstore"),
    ('urn:publicid:IDN+cpg.powderwireless.net+authority+cm',
     "Garage"),
    ('urn:publicid:IDN+ebc.powderwireless.net+authority+cm',
     "EBC"),
    ('urn:publicid:IDN+guesthouse.powderwireless.net+authority+cm',
     "GuestHouse"),
    ('urn:publicid:IDN+humanities.powderwireless.net+authority+cm',
     "Humanities"),
    ('urn:publicid:IDN+law73.powderwireless.net+authority+cm',
     "Law73"),
    ('urn:publicid:IDN+madsen.powderwireless.net+authority+cm',
     "Madsen"),
    ('urn:publicid:IDN+moran.powderwireless.net+authority+cm',
     "Moran"),
    ('urn:publicid:IDN+sagepoint.powderwireless.net+authority+cm',
     "SagePoint"),
    ('urn:publicid:IDN+web.powderwireless.net+authority+cm',
     "WEB"),
]

# Frequency/spectrum parameters
portal.context.defineStructParameter(
    "freq_ranges", "Range", [],
    multiValue=True,
    min=1,
    multiValueTitle="Frequency ranges for over-the-air operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            3550.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            3560.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

# # Set of Fixed Endpoint devices to allocate
# portal.context.defineStructParameter(
#     "fe_radios", "Fixed Endpoint B210 Sites",
#     multiValue=False,
#     members=[
#         portal.Parameter(
#             "Bookstore",
#             "Fixed Endpoint base-station B210 #1",
#             portal.ParameterType.STRING,
#             fe_names[0], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "Garage",
#             "Fixed Endpoint base-station B210 #2",
#             portal.ParameterType.STRING,
#             fe_names[1], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "EBC",
#             "Fixed Endpoint base-station B210 #3",
#             portal.ParameterType.STRING,
#             fe_names[2], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "GuestHouse",
#             "Fixed Endpoint base-station B210 #4",
#             portal.ParameterType.STRING,
#             fe_names[3], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "Humanities",
#             "Fixed Endpoint base-station B210 #5",
#             portal.ParameterType.STRING,
#             fe_names[4], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "Law73",
#             "Fixed Endpoint base-station B210 #6",
#             portal.ParameterType.STRING,
#             fe_names[5], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "Madsen",
#             "Fixed Endpoint base-station B210 #7",
#             portal.ParameterType.STRING,
#             fe_names[6], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "Moran",
#             "Fixed Endpoint base-station B210 #8",
#             portal.ParameterType.STRING,
#             fe_names[7], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "SagePoint",
#             "Fixed Endpoint base-station B210 #9",
#             portal.ParameterType.STRING,
#             fe_names[8], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         ),
#         portal.Parameter(
#             "WEB",
#             "Fixed Endpoint base-station B210 #10",
#             portal.ParameterType.STRING,
#             fe_names[9], 
#             fe_names,
#             longDescription="A `nuc2` device will be selected at the site."
#         )
#     ])
    
# Multi-value list of x310+PC pairs to add to experiment.
portal.context.defineStructParameter(
    "radios", "X310 CBRS Radios",
    multiValue=False,
    members=[
        portal.Parameter(
            "Behavioral",
            "Rooftop base-station X310 #1",
            portal.ParameterType.STRING,
            rooftop_names[0],
            rooftop_names),
        # portal.Parameter(
        #     "Browning",
        #     "Rooftop base-station X310 #2",
        #     portal.ParameterType.STRING,
        #     rooftop_names[1],
        #     rooftop_names),
        # portal.Parameter(
        #     "Dentistry",
        #     "Rooftop base-station X310 #3",
        #     portal.ParameterType.STRING,
        #     rooftop_names[2],
        #     rooftop_names),
        portal.Parameter(
            "Friendship",
            "Rooftop base-station X310 #4",
            portal.ParameterType.STRING,
            rooftop_names[3],
            rooftop_names),
        portal.Parameter(
            "Honors",
            "Rooftop base-station X310 #5",
            portal.ParameterType.STRING,
            rooftop_names[4],
            rooftop_names)
        # portal.Parameter(
        #     "MEB",
        #     "Rooftop base-station X310 #6",
        #     portal.ParameterType.STRING,
        #     rooftop_names[5],
        #     rooftop_names),
        # portal.Parameter(
        #     "SMT",
        #     "Rooftop base-station X310 #7",
        #     portal.ParameterType.STRING,
        #     rooftop_names[6],
        #     rooftop_names),
        # portal.Parameter(
        #     "USTAR",
        #     "Rooftop base-station X310 #8",
        #     portal.ParameterType.STRING,
        #     rooftop_names[7],
        #     rooftop_names)
    ])

# Bind and verify parameters
params = portal.context.bindParameters()

for i, frange in enumerate(params.freq_ranges):
    if frange.freq_min < 3400 or frange.freq_min > 3800 \
       or frange.freq_max < 3400 or frange.freq_max > 3800:
        perr = portal.ParameterError("Frequencies must be between 3400 and 3800 MHz", ["freq_ranges[%d].freq_min" % i, "freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["freq_ranges[%d].freq_min" % i, "freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

portal.context.verifyParameters()

# Request frequency range(s)
for frange in params.freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 100)
        
# Request PC + X310 resource pairs.
x310_node_pair(1, params.radios.Behavioral, params.nodetype, installs) # Behavioral
# x310_node_pair(2, params.radios.Browning, params.nodetype, installs) # Browning
# x310_node_pair(3, params.radios.Dentistry, params.nodetype, installs) # Dentistry
x310_node_pair(2, params.radios.Friendship, params.nodetype, installs) # Friendship
x310_node_pair(3, params.radios.Honors, params.nodetype, installs) # Honors
# x310_node_pair(6, params.radios.MEB, params.nodetype, installs) # MEB
# x310_node_pair(7, params.radios.SMT, params.nodetype, installs) # SMT
# x310_node_pair(8, params.radios.USTAR, params.nodetype, installs) # USTAR

# Request PC + b210 resource pairs.
# b210_node_pair(params.fe_radios.Bookstore, fe_names[0][0])
# b210_node_pair(params.fe_radios.Garage, fe_names[1][0])
# b210_node_pair(params.fe_radios.EBC, fe_names[2][0])
# b210_node_pair(params.fe_radios.GuestHouse, fe_names[3][0])
# b210_node_pair(params.fe_radios.Humanities, fe_names[4][0])
# b210_node_pair(params.fe_radios.Law73, fe_names[5][0])
# b210_node_pair(params.fe_radios.Madsen, fe_names[6][0])
# b210_node_pair(params.fe_radios.Moran, fe_names[7][0])
# b210_node_pair(params.fe_radios.SagePoint, fe_names[8][0])
# b210_node_pair(params.fe_radios.WEB, fe_names[9][0])

# Emit!
portal.context.printRequestRSpec()
