import nanovna
vna = nanovna.NanoVNA()
vna.open()
capture = vna.capture()
capture.save('nanovna-01-lead.png', 'PNG')
vna.close()
