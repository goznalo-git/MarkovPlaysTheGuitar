# Markovian walks on guitar tablatures

This project consists on the automatic generation of tablatures for guitar using Markov chains obtained by the accumulation of other already existing tablatures. These Markov chains can then be traversed, finding the resulting tablatures.

The current status of this project is: despite the caveats (see below), it does not take too much effort to generate the Markov chain associated to a series of .gp5 files, provided they have a single track. Random walks and their corresponding tabs are more straightforwardly implemented. Therefore, I would say this is ``usable''.

Note: There are still many caveats (note dynamics, lengths, effects, silences) and things to improve. In any case, this should serve as an inspiration to a musician rather than written-in-stone melodies.


## Organization

The code is currently structured in notebooks (yes, I know this is far from optimal, at some point I will refactor it).   

There are three "development" ones
- DataInspection.ipynb can be used to probe a single dataset, displaying some relevant information (number of tracks, keys, beats, etc)
- MarkovChains.ipynb contains the functions used to create the Markovian chains (both the standard and memory-aware ones)
- RandomWalks.ipynb defines functions to traverse the chain, which can then be used to print their corresponding tabs

There is one batch processing notebook
- Process_datasets.ipynb reads the files in the `Data/` folder, loading them into different graphs graph based on the key they're in.

There WILL BE a notebook loading the processed network (saved in `TrainedNetworks/`) where 


Note: in the memory-aware cases, multiple cases can be defined. First order memory means awareness of the previous note(s), second order means that it is aware of the last two note(s) where it has been, and so on. When walking through these memory aware ones, one must provide a starting "node" which is not a note, but a sequence of `n` notes, where `n` is the awareness level. For these reasons, both the functions generating the memory graphs and their random walks are different to those of the standard markovian graphs.   