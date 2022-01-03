#!/usr/bin/env python3
# Adapted from https://github.com/ttrftech/NanoVNA/blob/master/python/nanovna.py
# Removed functions with references to python 2.7 only libraries like `def smithd3(self, x):` using twoport.
# Removed script command line interface.

# Commands: version reset freq offset dac saveconfig clearconfig data frequencies bandwidth port stat gain power
# sample scan sweep test touchcal touchtest pause resume cal save recall trace marker edelay capture vbat vbat_offset
# transform threshold help info color

import serial
from serial.tools import list_ports
import numpy as np
from matplotlib import pylab as pl
import struct
import skrf
import PIL


class NanoVNA:
    VID = 0x0483  # 1155
    PID = 0x5740  # 22336

    def __init__(self, dev=None):
        self.dev = dev or self.get_port()
        self.serial = None
        self._frequencies = None
        self.points = 101

    @staticmethod
    def get_port() -> str:
        device_list = list_ports.comports()
        for device in device_list:
            if device.vid == NanoVNA.VID and device.pid == NanoVNA.PID:
                print(f'Using {device}')
                return device.device
        raise OSError("USB device not found")

    def open(self):
        if self.serial is None:
            self.serial = serial.Serial(self.dev)

    def close(self):
        if self.serial:
            self.serial.close()
        self.serial = None

    # Command promt doesn't always return a single line. Some commands return a help text, if the input is not formatted
    # correctly.
    def send_command(self, cmd):
        self.open()
        self.serial.write(cmd.encode())
        self.serial.readline()  # discard empty line

    def fetch_data(self):
        result = ''
        line = ''
        while True:
            c = self.serial.read().decode('utf-8')
            if c == chr(13):
                continue  # ignore CR
            line += c
            if c == chr(10):
                result += line
                line = ''
                continue  # newline found
            if line.endswith('ch>'):
                # stop on prompt
                break
        return result

    @property
    def frequencies(self):
        if not self._frequencies:
            self.fetch_frequencies()
        return self._frequencies

    def fetch_frequencies(self):
        self.send_command("frequencies\r")
        data = self.fetch_data()
        x = []
        for line in data.split('\n'):
            if line:
                x.append(float(line))
        self._frequencies = np.array(x)
        return self._frequencies

    # trace man
    # trace {0|1|2|3|all} [logmag|phase|delay|smith|polar|linear|swr|real|imag|r|x|q|off] [src]
    # trace {0|1|2|3} {scale|refpos} {value}

    def set_sweep(self, start, stop):
        if start is not None:
            self.send_command("sweep start %d\r" % start)
        if stop is not None:
            self.send_command("sweep stop %d\r" % stop)

    def set_port(self, port):
        if port is not None:
            self.send_command("port %d\r" % port)

    def set_gain(self, gain):
        if gain is not None:
            self.send_command("gain %d %d\r" % (gain, gain))

    def set_offset(self, offset):
        if offset is not None:
            self.send_command("offset %d\r" % offset)

    def set_strength(self, strength):
        if strength is not None:
            self.send_command("power %d\r" % strength)

    # I don't know what this is doing.
    def set_frequency(self, freq):
        if freq is not None:
            self.send_command("freq %d\r" % freq)

    def fetch_array(self, sel):
        self.send_command("data %d\r" % sel)
        data = self.fetch_data()
        x = []
        for line in data.split('\n'):
            if line:
                x.extend([float(d) for d in line.strip().split(' ')])
        return np.array(x[0::2]) + np.array(x[1::2]) * 1j

    def resume(self):
        self.send_command("resume\r")

    def pause(self):
        self.send_command("pause\r")

    def data(self, array=0):
        self.send_command("data %d\r" % array)
        data = self.fetch_data()
        x = []
        for line in data.split('\n'):
            if line:
                d = line.strip().split(' ')
                x.append(float(d[0]) + float(d[1]) * 1.j)
        return np.array(x)

    def send_scan(self, start=1e6, stop=900e6, points=None):
        if points:
            self.send_command("scan %d %d %d\r" % (start, stop, points))
        else:
            self.send_command("scan %d %d\r" % (start, stop))

    def scan(self):
        segment_length = 101
        array0 = []
        array1 = []
        if self._frequencies is None:
            self.fetch_frequencies()
        freqs = self._frequencies
        while len(freqs) > 0:
            seg_start = freqs[0]
            seg_stop = freqs[segment_length - 1] if len(freqs) >= segment_length else freqs[-1]
            length = segment_length if len(freqs) >= segment_length else len(freqs)
            # print((seg_start, seg_stop, length))
            self.send_scan(seg_start, seg_stop, length)
            array0.extend(self.data(0))
            array1.extend(self.data(1))
            freqs = freqs[segment_length:]
        self.resume()
        return (array0, array1)

    def capture(self) -> PIL.Image:
        self.send_command("capture\r")
        b = self.serial.read(320 * 240 * 2)
        x = struct.unpack(">76800H", b)
        # convert pixel format from 565(RGB) to 8888(RGBA)
        arr = np.array(x, dtype=np.uint32)
        arr = 0xFF000000 + ((arr & 0xF800) >> 8) + ((arr & 0x07E0) << 5) + ((arr & 0x001F) << 19)
        return PIL.Image.frombuffer('RGBA', (320, 240), arr, 'raw', 'RGBA', 0, 1)


class NanoVNAPlotting:
    REF_LEVEL = (1 << 9)

    def __init__(self, vna: NanoVNA):
        self.vna = vna
        self.frequencies = vna.fetch_frequencies()

    def logmag(self, x):
        pl.grid(True)
        pl.xlim(self.frequencies[0], self.frequencies[-1])
        pl.plot(self.frequencies, 20 * np.log10(np.abs(x)))

    def linmag(self, x):
        pl.grid(True)
        pl.xlim(self.frequencies[0], self.frequencies[-1])
        pl.plot(self.frequencies, np.abs(x))

    def phase(self, x, unwrap=False):
        pl.grid(True)
        a = np.angle(x)
        if unwrap:
            a = np.unwrap(a)
        else:
            pl.ylim((-180, 180))
        pl.xlim(self.frequencies[0], self.frequencies[-1])
        pl.plot(self.frequencies, np.rad2deg(a))

    def delay(self, x):
        pl.grid(True)
        delay = -np.unwrap(np.angle(x)) / (2 * np.pi * np.array(self.frequencies))
        pl.xlim(self.frequencies[0], self.frequencies[-1])
        pl.plot(self.frequencies, delay)

    def groupdelay(self, x):
        pl.grid(True)
        gd = np.convolve(np.unwrap(np.angle(x)), [1, -1], mode='same')
        pl.xlim(self.frequencies[0], self.frequencies[-1])
        pl.plot(self.frequencies, gd)

    def vswr(self, x):
        pl.grid(True)
        vswr = (1 + np.abs(x)) / (1 - np.abs(x))
        pl.xlim(self.frequencies[0], self.frequencies[-1])
        pl.plot(self.frequencies, vswr)

    def polar(self, x):
        ax = pl.subplot(111, projection='polar')
        ax.grid(True)
        ax.set_ylim((0, 1))
        ax.plot(np.angle(x), np.abs(x))

    def tdr(self, x):
        pl.grid(True)
        window = np.blackman(len(x))
        NFFT = 256
        td = np.abs(np.fft.ifft(window * x, NFFT))
        time = 1 / (self.frequencies[1] - self.frequencies[0])
        t_axis = np.linspace(0, time, NFFT)
        pl.plot(t_axis, td)
        pl.xlim(0, time)
        pl.xlabel("time (s)")
        pl.ylabel("magnitude")

    def skrf_network(self, x):
        network = skrf.Network()
        network.frequency = skrf.Frequency.from_f(self.frequencies / 1e6, unit='mhz')
        network.s = x
        return network

    def smith(self, x):
        network = self.skrf_network(x)
        network.plot_s_smith()
        return network
