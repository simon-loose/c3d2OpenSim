import opensim
import numpy as np, os
from tkinter import filedialog
import tkinter as tk

"""
This code scales all muscles based on (mass/original_mass)^(2/3),
as described in Clemente et al (2024):
https://www.nature.com/articles/s41467-024-52924-z#Abs1. 
The new model is saved as "{YourModel}_scaled_muscles.osim" in
the same directory as your scaled model.
"""

#set model input and output paths
root = tk.Tk()
root.withdraw()
model_path = filedialog.askopenfilename(title="Select scaled OpenSim model", filetypes=[("OpenSim model file", "*.osim")])
orig_model_path = filedialog.askopenfilename(title="Select unscaled OpenSim model", filetypes=[("OpenSim model file", "*.osim")])
Scaled_muscles_path = model_path.replace(".osim", "_scaled_muscles.osim")
#load unscaled model to get original mass
model = opensim.Model(orig_model_path)
state = model.initSystem()
m_orig = model.getTotalMass(state)
#load scaled model and set scale factor
model = opensim.Model(model_path)
muscles = model.getMuscles()
state = model.initSystem()
model_mass = model.getTotalMass(state)
scale_factor = (model_mass/m_orig)**0.67    #From clemente et al. (2024) https://www.nature.com/articles/s41467-024-52924-z#Abs1

# Loop through all muscles and modify the max_isometric_force
for i in range(muscles.getSize()):
    muscle = muscles.get(i)
    print(f"Before: {muscle.getName()} - Max Force: {muscle.getMaxIsometricForce()}")
    # Scale muscle forces by scale factor defined above
    muscle.setMaxIsometricForce(scale_factor * muscle.getMaxIsometricForce())
    print(f"After: {muscle.getName()} - Max Force: {muscle.getMaxIsometricForce()}")

print(f"All muscles scaled by {scale_factor}")

# Finalize the connections and save the updated model for muscle simulations
model.finalizeConnections()
model.printToXML(Scaled_muscles_path)

print(f"Edited model for muscle sim saved to {Scaled_muscles_path}")