#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import readspec_mod

noise_off = readspec_mod.readSpec('test_220_0_noise_off0.log')
noise_on = readspec_mod.readSpec('test_220_0_noise_on0.log')

fc = 1272.4+150

f_range = np.linspace(fc-6, fc+6, noise_off.shape[0])

plt.plot(f_range, np.mean(noise_off,1), label="Noise Off")
plt.plot(f_range, np.mean(noise_on,1), label="Noise On")
plt.title('Galactic Coordinates: long=$220^{\circ}$ lat=$0^{\circ}$\nLO=1272.4MHz 04/22 at 21:40 PDT')
plt.xlabel('MHz')
plt.legend()
plt.show()
