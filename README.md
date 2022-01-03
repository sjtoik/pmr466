# Receiving Personal Mobile Radio traffic

Aim of this never ending project is to build [PMR446](https://en.wikipedia.org/wiki/PMR446) traffic sniffer, that stores
the all communication to disk. The focus is on the radio interface, not that much on the traffic itself.

Ready made devices can be found like
Baofeng UV-5R or UV-5X3 or GT-5R as spectraly clean version. Good and cheap handheld radios if you can get some.

The projects plan is to:
1. Measure different components participating in the [signal chain](./nanovna-01/README.md)
2. Get and setup [antennas](https://www.rxtx.fi/paavalikko/sirio-so-437-n-uhf-antenni-430-450-mhz/p/503034/) and [filtering](https://www.mouser.fi/ProductDetail/ABRACON/AFS4460W02-TD01?qs=H8AWquzS%2FlPjLo7qRURdEw%3D%3D)
3. Build a kit that records all communication on the freq bands and stores the active traffic to disk
4. (optional) Build the TX part

PRM466 channels start from 446.00625 MHz  and ends to 446.196875 MHz
