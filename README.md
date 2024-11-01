# MiEP-code

Code for my project, Multi-instrument Electric Piano, which can play multiple instruments at the same time.

This contins files for both Arduino and Raspberry Pi.

48 wires (1 per key) should be wired to digital pins 6 (C2) through 53 (B5) on an Arduino Mega, which should connect to Raspberry Pi through USB.

`main.py` should run on the Raspberry Pi.

Guitar note files are from [here](https://freesound.org/people/josefpres/) and [here](https://freesound.org/people/Kyster/packs/7398/)

Piano note files are from [here](https://freesound.org/people/jobro/packs/2489/)

Guitar and piano audio are saved in the format `[keynumber][guitar/piano].wav`, with keynumber ranging from 0 (C2) to 47 (B5)
