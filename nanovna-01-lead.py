import numpy

import nanovna
import time

vna = nanovna.NanoVNA()
vna.open()


def polar():
    vna.set_trace(0, 'polar', 0)
    vna.set_trace(1, 'linear', 0)
    vna.set_trace(2, 'real', 0)
    vna.set_trace(3, 'imag', 0)
    time.sleep(3)

    capture = vna.capture()
    capture.save('nanovna-01-lead-polar.png', 'PNG')


def smith():
    vna.set_trace(0, 'logmag', 0)
    vna.set_trace(1, 'phase', 0)
    vna.set_trace(2, 'delay', 0)
    vna.set_trace(3, 'smith', 0)
    time.sleep(3)

    capture = vna.capture()
    capture.save('nanovna-01-lead-smith.png', 'PNG')


def swr():
    vna.set_trace(0, 'swr', 0)
    vna.set_trace(1, 'r', 0)
    vna.set_trace(2, 'x', 0)
    vna.set_trace(3, 'q', 0)
    time.sleep(3)

    capture = vna.capture()
    capture.save('nanovna-01-lead-swr.png', 'PNG')


def problems():
    vna.set_trace(0, 'smith', 0)
    vna.set_trace(1, 'delay', 0)
    vna.set_trace(2, 'phase', 0)
    vna.set_trace(3, 'q', 0)
    print('Sleeping 5')  # These traces takes a bit time to settle. Command crashes the board, if sent too soon.
    time.sleep(5)

    capture = vna.capture()
    capture.save('nanovna-01-lead-problems.png', 'PNG')

    print('Sleeping 2')
    time.sleep(2)
    data = vna.data()
    numpy.save('nanovna-01-lead-problems.npy', data)


# polar()
# smith()
# swr()
problems()
vna.close()
