# FreeCAD-BIM-Window-Door
BIM Window and Door features for Vers.1.1.4

The following is an extension of the method for creating doors and windows in the BIM Workbench, originally developed by Jorik van Havre.
It works with the current stable version 1.1.4.
Installation instructions:
After backing up the original files, replace them with the attached files:

In Mod/BIM/bimcommands:

•	BimWindow.py

In Mod/BIM:

•	ArchWindow.py

•	ArchWindowPresets.py

•	Additionally, include the three attached SVG file.


New features:
The selection menus for windows and doors now include options for arched windows and doors.
An opening for the door handle has been added to the door leaves to ensure that subsequent handle positioning works correctly, even when the door leaves are not aligned orthogonally.
To ensure the correct vertical positioning of the door frame and door, depending on the selected floor build-up, the height can be adjusted afterwards using the ScreedHeight parameter.
The SubVolume used for the subtraction geometry is then automatically enlarged accordingly.
