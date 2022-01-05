import nanovna
import time

DIR = 'nanovna-testing'
PREFIX = 'testing'
vna = nanovna.NanoVNA()


# On device reset, the buffer has multiple prompts and 'NanoVNA Shell' text in it
def reset_testing():
    vna._open()
    print(f'lines: {vna._read_lines()}')
    print(f'lines: {vna._read_lines()}')
    print(f'lines: {vna._read_lines()}')


vna.set_marker(1, 73)  # index 73 is 446MHz with 101 points
vna.pause()
time.sleep(2)
vna.resume()
