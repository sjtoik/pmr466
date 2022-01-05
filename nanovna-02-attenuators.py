import nanovna
import time

DIR = 'nanovna-02'
PREFIX = 'attenuators-straight'
vna = nanovna.NanoVNA()
vna.set_marker(1, 73)  # index 73 is 446MHz with 101 points


def polar():
    vna.set_trace(0, 'polar', 0)
    vna.set_trace(1, 'linear', 0)
    vna.set_trace(2, 'real', 0)
    vna.set_trace(3, 'imag', 0)
    time.sleep(3)

    capture = vna.capture()
    capture.save(f'{DIR}/{PREFIX}-polar.png', 'PNG')


def smith():
    vna.set_trace(0, 'logmag', 0)
    vna.set_trace(1, 'phase', 0)
    vna.set_trace(2, 'delay', 0)
    vna.set_trace(3, 'smith', 0)
    time.sleep(3)

    capture = vna.capture()
    capture.save(f'{DIR}/{PREFIX}-smith.png', 'PNG')


def swr():
    vna.set_trace(0, 'swr', 0)
    vna.set_trace(1, 'r', 0)
    vna.set_trace(2, 'x', 0)
    vna.set_trace(3, 'q', 0)
    time.sleep(3)

    capture = vna.capture()
    capture.save(f'{DIR}/{PREFIX}-swr.png', 'PNG')


def test():
    vna.set_trace(0, 'swr', 0)


#polar()
#smith()
#swr()
#test()
arr1 = vna.fetch_array(0)
arr2 = vna.data()
