# 561-Code

## Program usage

This program is used by call the main function with 3 arguments: the number of times steps you wish to run a simulation for, the name of a configuration file with the simulation parameters, and the name of the output file.

The output of the program is written in a format that is compatible with Python's configparser module. The ProcessOutput.py module can be used to convert the output file data into an easy-to-use Python dictionary for analysis.

The learning and optimization strategy described in our project report is currently the only available stategy. However, new strategies could be implemented and used by modifying the Strategies.py file. Instructions on how to implement a new strategy are included in that file.

## Creating a configuration file

An example configuration file ("example.conf") is included in the repository.
