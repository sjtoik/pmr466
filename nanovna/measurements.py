import time
import os


class Measurements:

    def __init__(self, vna, directory, prefix):
        self.vna = vna
        self.directory = directory
        self.prefix = prefix
        if not os.path.isdir(directory):
            raise AttributeError(f'{directory} is not a directory')

    def clear_screen(self):
        self.vna.pause()
        self.vna.set_trace('all', 'off', 0)
        self.vna.set_trace('all', 'off', 1)
        self.vna.set_marker(1, 'off')
        self.vna.set_marker(2, 'off')
        self.vna.set_marker(3, 'off')
        self.vna.set_marker(4, 'off')
        self.vna.resume()  # refresh the screen to show the blanking
        time.sleep(0.5)

    def polar(self):
        self.vna.set_trace(0, 'polar', 0)
        self.vna.set_trace(1, 'linear', 0)
        self.vna.set_trace(2, 'real', 0)
        self.vna.set_trace(3, 'imag', 0)
        time.sleep(0.5)

        capture = self.vna.capture()
        capture.save(f'{self.directory}/{self.prefix}-polar.png', 'PNG')

    def smith(self):
        self.vna.set_trace(0, 'logmag', 0)
        self.vna.set_trace(1, 'phase', 0)
        self.vna.set_trace(2, 'delay', 0)
        self.vna.set_trace(3, 'smith', 0)
        time.sleep(0.5)

        capture = self.vna.capture()
        capture.save(f'{self.directory}/{self.prefix}-smith.png', 'PNG')

    def swr(self):
        self.vna.set_trace(0, 'swr', 0)
        self.vna.set_trace(1, 'r', 0)
        self.vna.set_trace(2, 'x', 0)
        self.vna.set_trace(3, 'q', 0)
        time.sleep(0.5)

        capture = self.vna.capture()
        capture.save(f'{self.directory}/{self.prefix}-swr.png', 'PNG')


