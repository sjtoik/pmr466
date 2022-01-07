# Adapted from https://github.com/ttrftech/NanoVNA/blob/master/python/nanovna.py
# The implementation needed a full rewrite due to implementation style and python 3 differences

# Available commands: version reset freq offset dac saveconfig clearconfig data frequencies bandwidth port stat gain
# power sample scan sweep test touchcal touchtest pause resume cal save recall trace marker edelay capture vbat
# vbat_offset transform threshold help info color

import serial
from serial.tools import list_ports
import time
import logging
import PIL
import struct
import numpy as np


class NanoVNA:
    VID = 0x0483  # 1155
    PID = 0x5740  # 22336

    def __init__(self, loglevel=logging.INFO):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=loglevel)
        self._tty = self.get_tty()
        self.serial = None
        self._frequencies = None
        self.points = 101

    def __del__(self):
        self._close()

    @staticmethod
    def get_tty() -> str:
        device_list = list_ports.comports()
        for device in device_list:
            if device.vid == NanoVNA.VID and device.pid == NanoVNA.PID:
                logging.info(f'Using {device}')
                return device.device
        raise OSError("USB device not found")

    def _open(self):
        if self.serial is None:
            self.serial = serial.Serial(self._tty)
            time.sleep(0.2)  # On device reset, the buffer has multiple prompts and 'NanoVNA Shell' text in it
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

    def _close(self):
        if self.serial:
            self.serial.close()

    def _send_command(self, cmd):
        """
        Users is responsible on the output handling. Calling _read_lines after execution also acts as a synchronization
        point for the connection. A new command is not sent to buffer before previous one has outputted a newline or a
        promt. _send_command reads only the current line up to the next newline, no further.
        Rest of the output can be:

        * <data_lines>\r\n
        * <cmd>? for unrecognized input
        * <help>\r\n text lines explaining the syntax of the <cmd>
        * <binary> for transmitting the capture
        * b'ch> ' without newline

        It is advisable to pause and resume when making data captures, as there is no guarantee that the memory is not
        overwritten during the capture. It also saves cycle times from the microcontroller being busy updating
        the screen.

        pyserial.readlines() is unusable because of how the prompt behaves. The readlines hangs on prompt and waits for
        newline forever. Read timeouts can't be used, because of the capture binary takes forever to transfer over.

        :param cmd: Command to be sent to the serial device
        :return: None
        """
        if not cmd.endswith('\r'):
            cmd += '\r'

        self._open()
        logging.debug(f'Sending: {cmd.encode()}')
        self.serial.write(cmd.encode())
        data = self._read_line()
        logging.debug(f'Result: {data}')

    def _read_line(self) -> bytearray:
        line = bytearray()
        while True:
            b = bytes(self.serial.read())
            line += b
            if b == b'\n':
                return line
            if line == b'ch> ':
                line = bytearray()
                break
        return line

    def _read_lines(self) -> [str]:
        result = []
        while True:
            line = self._read_line()
            if line == b'':
                break
            result.append(line.decode('utf-8').strip())
        return result

    # marker [n] [on|off|{index}]
    # marker numbering starts from 1
    # the index is the point what value the marker should display from 0 to 100 (101) points by default
    def set_marker(self, n: int, index):
        self._send_command('marker %d %s' % (n, index))
        self._read_lines()

    # trace {0|1|2|3|all} [logmag|phase|delay|smith|polar|linear|swr|real|imag|r|x|q|off] [src]
    # trace {0|1|2|3} {scale|refpos} {value}
    def set_trace(self, trace, trace_format, channel):
        self._send_command('trace %s %s %s' % (trace, trace_format, channel))
        # the device output buffer contains the command, and the next prompt
        self._read_lines()

    # pause doesn't return anything but the 'ch> ' prompt, but as there is a \n\r and that prompt in the buffer
    # it's important to read them both, so the next command doesn't get confused
    def pause(self):
        self._send_command('pause')
        self._read_lines()

    def resume(self):
        self._send_command('resume')
        self._read_lines()

    def get_frequencies(self):
        self._send_command('frequencies')
        return self._read_lines()

    def capture(self) -> PIL.Image:
        self._send_command("capture")
        b = self.serial.read(320 * 240 * 2)
        x = struct.unpack(">76800H", b)
        arr = np.array(x, dtype=np.uint32)  # convert pixel format from 565(RGB) to 8888(RGBA)
        arr = 0xFF000000 + ((arr & 0xF800) >> 8) + ((arr & 0x07E0) << 5) + ((arr & 0x001F) << 19)
        image = PIL.Image.frombuffer('RGBA', (320, 240), arr, 'raw', 'RGBA', 0, 1)
        self._read_lines()  # clear out the remaining buffer
        return image

    # data {0|1|2|3|4|5|6}
    # 0: S11
    # 1: S21
    # 2: /* error term directivity */
    # 3: /* error term source match */
    # 4: /* error term reflection tracking */
    # 5: /* error term transmission tracking */
    # 6: /* error term isolation */
    def get_data(self, array=0) -> np.array:
        if not 0 <= array <= 6:
            raise AttributeError('There are data arrays only from 0 to 6')

        self._send_command('data %d' % array)
        lines = self._read_lines()
        x = []
        for line in lines:
            if line:
                d = line.split(' ')
                x.append(float(d[0]) + float(d[1]) * 1.j)
        return np.array(x)

    def get_info(self) -> [str]:
        self._send_command('info')
        return self._read_lines()

    def get_sweep(self) -> (int, int, int):
        self._send_command('sweep')
        lines = self._read_lines()
        values = lines[0].split(' ')
        values = [int(n) for n in values]
        return values[0], values[1], values[2]

    # you should really recalibrate after changing the sweep
    def set_sweep(self, start, stop, points):
        self._send_command('sweep %d %d %d' % (start, stop, points))
        self._read_lines()

    # sending scan command seems to call pause implicitly
    def set_scan(self, start, stop, points):
        self._send_command('scan %d %d %d' % (start, stop, points))
        self._read_lines()
