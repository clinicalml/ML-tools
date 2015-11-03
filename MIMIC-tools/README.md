# MIMIC related scripts

A collection of scripts to make dealing with MIMIC3 easier.

- MIMIC 3 is a bit too big, so SplitMimicText.py and SplitMimicOthers.py split the data into groups
of less than 100 patients
- ParseMimicIII.py then reads all information related to a patient into a tree structured object 
(dictionary of dictionaries / lists)

