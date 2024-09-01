#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FileWrite_RX
# Author: Jose Sanchez
# GNU Radio version: 3.8.5.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time


class FileWrite_RX(gr.top_block):

    def __init__(self, modulationID):
        gr.top_block.__init__(self, "FileWrite_RX")
        self.modulationID = modulationID

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(3.555e9, 0)
        self.uhd_usrp_source_0.set_gain(36, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_bandwidth(0.5e6, 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())

        modulationTypes = ['8PSK', '16QAM', '64QAM', 'B-FM', 'BPSK', 'CPFSK', 'DSB-AM', 'GFSK', 'PAM4', 'QPSK', 'SSB-AM']

        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/tmp/'+modulationTypes[self.modulationID]+'.iq', False)
        self.blocks_file_sink_0.set_unbuffered(True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_file_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

def main(top_block_cls=FileWrite_RX, options=None, modulationID=0):
    
    tb = top_block_cls(modulationID)
    print("Starting RX")
    modulationTypes = ['8PSK', '16QAM', '64QAM', 'B-FM', 'BPSK', 'CPFSK', 'DSB-AM', 'GFSK', 'PAM4', 'QPSK', 'SSB-AM']
    tb.start()
    print("Starting RX for modulation: ", modulationTypes[modulationID])
    timer = 10
    for i in range(timer):
        time.sleep(1)
        print("RX timer: ",i)
    print("Stopping RX")
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    print("Modulation ID: ")
    modulationID = int(input())
    main(modulationID=modulationID)
