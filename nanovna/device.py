# Available commands: version reset freq offset dac saveconfig clearconfig data frequencies bandwidth port stat gain
# power sample scan sweep test touchcal touchtest pause resume cal save recall trace marker edelay capture vbat
# vbat_offset transform threshold help info color

import serial
from serial.tools import list_ports
import time


class NanoVNA:
    VID = 0x0483  # 1155
    PID = 0x5740  # 22336

    def __init__(self):
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
                print(f'Using {device}')
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
        It is users responsibility to handle the output. The output can be:
        * <cmd>\r\n
        * <cmd>\r\n + <data_lines>\r\n
        * <cmd>? for unrecognized input
        * <cmd>\r\n + help text explaining the syntax of the <cmd>
        * <cmd>\r\n + <binary> for transmitting the capture
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
        print(f'Sending: {cmd.encode()}')
        self.serial.write(cmd.encode())
        data = self._read_line()
        print(f'Result: {data}')

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

    def _read_lines(self) -> bytearray:
        result = bytearray()
        while True:
            line = self._read_line()
            if line == b'':
                break
            result += line
        return result

    # marker [n] [on|off|{index}]
    # marker numbering starts from 1
    # the index is the point what value the marker should display from 0 to 100 (101) points by default
    def set_marker(self, n: int, index):
        self._send_command('marker %d %s' % (n, index))

    # trace {0|1|2|3|all} [logmag|phase|delay|smith|polar|linear|swr|real|imag|r|x|q|off] [src]
    # trace {0|1|2|3} {scale|refpos} {value}
    def set_trace(self, trace, trace_format, channel):
        self._send_command('trace %s %s %s' % (trace, trace_format, channel))

    def pause(self):
        self._send_command('pause')

    def resume(self):
        self._send_command('resume')
