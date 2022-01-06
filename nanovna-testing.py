import numpy

import nanovna
import time
import logging

DIR = 'nanovna-testing'
PREFIX = 'testing'
vna = nanovna.NanoVNA(loglevel=logging.DEBUG)


# On device reset, the buffer has multiple prompts and 'NanoVNA Shell' text in it
def reset_testing():
    vna._open()
    print(f'lines: {vna._read_lines()}')
    print(f'lines: {vna._read_lines()}')
    print(f'lines: {vna._read_lines()}')


def pause_resume_test():
    vna.set_marker(1, 73)  # index 73 is 446MHz with 101 points
    vna.pause()
    time.sleep(2)
    vna.resume()


def full_pull():
    vna.set_trace(0, 'swr', 0)
    vna.set_trace(1, 'delay', 0)
    vna.set_trace(2, 'q', 0)
    vna.set_trace(3, 'smith', 0)
    time.sleep(0.1)

    capture = vna.capture()
    capture.save(f'{DIR}/{PREFIX}-swr.png', 'PNG')


def snapshot_test():
    measurements = nanovna.Measurements(vna, DIR, PREFIX)
    measurements.clear_screen()

    vna.set_trace(0, 'polar', 0)
    vna.set_trace(1, 'linear', 0)
    vna.set_trace(2, 'real', 0)
    vna.set_trace(3, 'imag', 0)
    vna.set_marker(1, 73)

    start, stop, points = vna.get_sweep()
    vna.set_scan(start, stop, points)

    data0 = vna.get_data()
    logging.debug('Got one array, waiting for a hot second for the second retrieval.')
    time.sleep(2)
    data1 = vna.get_data()
    assert numpy.array_equal(data0, data1)

    vna.resume()


#capture = vna.capture()
#capture.save(f'{DIR}/{PREFIX}-smith.png', 'PNG')
#vna.set_sweep(300e6, 500e6, 101)
#vna.set_marker(1, 73)
#full_pull()
snapshot()
