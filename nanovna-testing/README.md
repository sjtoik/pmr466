# Testing the refactored serial implementation
Idea is to just dump all different versions of screens, to quickly get the idea where the different measurements are at.
The screens are from different scans, as the device needs to be resumed to normal operation in order to refresh the 
screen.

![polar](testing-polar.png)

A Device Under Test (DUT) has both `R+jX` Resistive and Reactive (imaginary) components. In polar display, the magnitude
is the distance from center and the  


## Phase and delay
![smith](testing-smith.png)

Delay seems to be all over the place. Averaging that might give better characteristics.

The phase behaves as expected and is quite linear throughout the span. The flip around 480MHz is not a reflection, but 
the graph reaching -180 degrees. As the phase describes the S11 signal (forward reflection), the phase is always behind
and hence negative. The amount of phase delay in a given frequency, on can calculate the distance of the reflection.

In smith chart, everything under zero is capacitive, and on top of zero, inductive. 

![swr](testing-swr.png)


