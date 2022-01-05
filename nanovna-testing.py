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


def clear_screen():
    vna.pause()
    vna.set_trace('all', 'off', 0)
    vna.set_trace('all', 'off', 1)
    vna.set_marker(1, 'off')
    vna.set_marker(2, 'off')
    vna.set_marker(3, 'off')
    vna.set_marker(4, 'off')
    vna.resume()  # refresh the screen to show the blanking
    time.sleep(1)
    vna.pause()
    vna.set_trace(0, 'smith', 0)
    vna.set_marker(1, 73)
    time.sleep(2)
    vna.resume()


#capture = vna.capture()
#capture.save(f'{DIR}/{PREFIX}-smith.png', 'PNG')
full_pull()
full_pull()
full_pull()
full_pull()
