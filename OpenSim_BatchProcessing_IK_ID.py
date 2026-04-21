import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import os
import json
import numpy as np
import opensim
import pandas as pd

"""
This code makes IK and ID setup files and runs IK and ID in OpenSim by using template setup files.
Template file is used to take weights for marker tracking. This code only changes the timing, input
files and the output files and then runs IK and/or ID with the same settings as the template.

Steps:
- Click run to open the input dialog
- Select OpenSim model
- Select options (run IK/ID and suboptions)
- Select template xml file(s)
- Select folder with .trc files (or .mot files for ID only) to process
- Click "OK" to start processing
- Wait for code to finish and check if errors were thrown during batch processing
"""

def select_model(title, file_type):
    model_path.set(filedialog.askopenfilename(title=title, filetypes=file_type))

def select_IK_template(title, file_type):
    IK_template_path.set(filedialog.askopenfilename(title=title, filetypes=file_type))

def select_ID_template(title, file_type):
    ID_template_path.set(filedialog.askopenfilename(title=title, filetypes=file_type))

def select_ExternalLoads_template(title, file_type):
    ExternalLoads_template_path.set(filedialog.askopenfilename(title=title, filetypes=file_type))

def select_trc_folder():
    trc_path.set(filedialog.askdirectory())

def select_mot_folder():
    mot_path.set(filedialog.askdirectory())

def toggle_suboptions():
    if IK.get():
        Marker_errors_check.config(state="normal")
        trc_folder_entry.config(state="normal")
        trc_folder_button.config(state="normal")
        IK_template.config(state="normal")
        IK_template_button.config(state="normal")
        if ID.get():
            ID_template.config(state="normal")
            ID_template_button.config(state="normal")
            ExternalLoads_check.config(state="normal")
            mot_folder_entry.config(state="disabled")
            mot_folder_button.config(state="disabled")
            if ExternalLoads.get():
                ExternalLoads_template.config(state="normal")
                ExternalLoads_template_button.config(state="normal")
            else:
                ExternalLoads_template.config(state="disabled")
                ExternalLoads_template_button.config(state="disabled")
        else:
            ID_template.config(state="disabled")
            ID_template_button.config(state="disabled")
            ExternalLoads_check.config(state="disabled")
            ExternalLoads.set(False)
            ExternalLoads_template.config(state="disabled")
            ExternalLoads_template_button.config(state="disabled")
    else:
        Marker_errors_check.config(state="disabled")
        trc_folder_entry.config(state="disabled")
        trc_folder_button.config(state="disabled")
        IK_template.config(state="disabled")
        IK_template_button.config(state="disabled")
        MarkerErrors.set(False)
        if ID.get():
            ID_template.config(state="normal")
            ID_template_button.config(state="normal")
            ExternalLoads_check.config(state="normal")
            mot_folder_entry.config(state="normal")
            mot_folder_button.config(state="normal")
            if ExternalLoads.get():
                ExternalLoads_template.config(state="normal")
                ExternalLoads_template_button.config(state="normal")
            else:
                ExternalLoads_template.config(state="disabled")
                ExternalLoads_template_button.config(state="disabled")
        else:
            ID_template.config(state="disabled")
            ID_template_button.config(state="disabled")
            mot_folder_entry.config(state="disabled")
            mot_folder_button.config(state="disabled")
            ExternalLoads_check.config(state="disabled")
            ExternalLoads.set(False)
            ExternalLoads_template.config(state="disabled")
            ExternalLoads_template_button.config(state="disabled")


def submit():
    print("Batch processing with following settings:")
    print("Run IK:", IK.get())
    print("Get marker errors:", MarkerErrors.get())
    print("Run ID:", ID.get())
    print("External loads:", ExternalLoads.get())
    print("Model:", model_path.get())
    print("IK Template:", IK_template_path.get())
    print("ID Template:", ID_template_path.get())
    print("trc Folder:", trc_path.get())
    print("mot Folder:", mot_path.get())
    tkroot.destroy()

tkroot = tk.Tk()
tkroot.title("Set up OpenSim Batch Processing")

model_path = tk.StringVar()
IK_template_path = tk.StringVar()
ID_template_path = tk.StringVar()
ExternalLoads_template_path = tk.StringVar()
trc_path = tk.StringVar()
mot_path = tk.StringVar()
IK = tk.BooleanVar()
MarkerErrors = tk.BooleanVar()
ID = tk.BooleanVar()
ExternalLoads = tk.BooleanVar()

# Model selection
tk.Label(tkroot, text="Select scaled OpenSim model:").pack()
tk.Entry(tkroot, textvariable=model_path, width=100).pack()
tk.Button(tkroot, text="Browse File", command=lambda: select_model("Select scaled OpenSim model",[("OpenSim model file", "*.osim")])).pack()

# IK Template file selection
tk.Label(tkroot, text="Select template IK Setup file:").pack()
IK_template = tk.Entry(tkroot, textvariable=IK_template_path, width=100, state="disabled")
IK_template.pack()

IK_template_button = tk.Button(
    tkroot,
    text="Browse File",
    command=lambda: select_IK_template("Select template IK setup file",[("IK setup file", "*.xml")]),
    state="disabled")
IK_template_button.pack()

# ID Template file selection
tk.Label(tkroot, text="Select template ID Setup file:").pack()
ID_template = tk.Entry(tkroot, textvariable=ID_template_path, width=100, state="disabled")
ID_template.pack()

ID_template_button = tk.Button(
    tkroot,
    text="Browse File",
    command=lambda: select_ID_template("Select template ID setup file",[("ID setup file", "*.xml")]),
    state="disabled")
ID_template_button.pack()

# External Loads template file selection
tk.Label(tkroot, text="Select template ExternalLoads file:").pack()
ExternalLoads_template = tk.Entry(tkroot, textvariable=ExternalLoads_template_path, width=100, state="disabled")
ExternalLoads_template.pack()

ExternalLoads_template_button = tk.Button(
    tkroot,
    text="Browse File",
    command=lambda: select_ExternalLoads_template("Select template ExternalLoads file",[("ExternalLoads file", "*.xml")]),
    state="disabled")
ExternalLoads_template_button.pack()

# trc folder selection
tk.Label(tkroot, text="Select a folder containing .trc files for processing:").pack()
trc_folder_entry = tk.Entry(tkroot, textvariable=trc_path, width=100, state="disabled")
trc_folder_entry.pack()

trc_folder_button = tk.Button(
    tkroot,
    text="Browse Folder",
    command=select_trc_folder,
    state="disabled"
)
trc_folder_button.pack()

# mot folder selection
tk.Label(tkroot, text="Select a folder containing IK output .mot files (should end with /OpenSim/IK) for processing:").pack()
mot_folder_entry = tk.Entry(tkroot, textvariable=mot_path, width=100, state="disabled")
mot_folder_entry.pack()

mot_folder_button = tk.Button(
    tkroot,
    text="Browse Folder",
    command=select_mot_folder,
    state="disabled"
)
mot_folder_button.pack()

# IK check button
IK_check = tk.Checkbutton(
    tkroot,
    text="Run IK",
    variable=IK,
    command=toggle_suboptions
)
IK_check.pack()

# Marker errors (starts disabled)
Marker_errors_check = tk.Checkbutton(
    tkroot,
    text="Compute IK marker errors",
    variable=MarkerErrors,
    state="disabled"
)
Marker_errors_check.pack()

# ID check button
ID_check = tk.Checkbutton(
    tkroot,
    text="Run ID",
    variable=ID,
    command=toggle_suboptions
)
ID_check.pack()

# External Loads (starts disabled)
ExternalLoads_check = tk.Checkbutton(
    tkroot,
    text="Include External loads",
    variable=ExternalLoads,
    command=toggle_suboptions,
    state="disabled"
)
ExternalLoads_check.pack()

# Submit button
tk.Button(tkroot, text="OK", command=submit).pack()

tkroot.mainloop()


model_path = model_path.get()

if IK.get():
    trc_path = trc_path.get()
    mot_path = trc_path
    IK_template_path = IK_template_path.get()
    IK_output_path = os.path.join(trc_path, "OpenSim/IK")
    if not os.path.exists(IK_output_path):
        os.makedirs(IK_output_path)
        os.makedirs(os.path.join(IK_output_path, "setup"))

elif ID.get():
    mot_path = mot_path.get()
if ID.get():
    ID_template_path = ID_template_path.get()
    if IK.get():
        ID_output_path = os.path.join(trc_path, "OpenSim/ID")
    else:
        ID_output_path = os.path.join(mot_path, "../ID")
    if not os.path.exists(ID_output_path):
        os.makedirs(ID_output_path)
        os.makedirs(os.path.join(ID_output_path, "setup"))



def write_to_trc(markers, marker_names, time, filename):
    # This function writes a trc file from the markers and time data, this is the format for labelled markers used in the OpenSim workflow
    # INPUT
    # markers: np.array, shape (n_samples, n_markers, 3)
    # marker_names: list of strings, length n_markers
    # time: np.array, shape (n_samples,)
    # filename: string

    markers = markers.reshape(
        markers.shape[0], -1)

    trc_marker_data_full = np.concatenate((np.arange(markers.shape[0]).reshape(-1, 1), time.reshape(-1, 1),markers),axis=1)

    header0 = ['PathFileType', '4', '(X/Y/Z)', filename]
    header1 = ['DataRate', 'CameraRate', 'NumFrames', 'NumMarkers', 'Units', 'OrigDataRate', 'OrigDataStartFrame',
               'OrigNumFrames']
    header2 = [str(100), str(100), str(trc_marker_data_full.shape[0]), str(len(marker_names)), 'mm', str(100), str(1), str(trc_marker_data_full.shape[0])]
    header3_1 = ['Frame#', 'Time']
    header3_2 = marker_names
    header4 = ['', '']
    for i in range(len(marker_names)):
        header4.append('X' + str(i+1))
        header4.append('Y' + str(i+1))
        header4.append('Z' + str(i+1))
    header4 = [' ', ' '] + header4
    with open(filename, 'w') as f:
        header0 = '\t'.join(header0)
        header1 = '\t'.join(header1)
        header2 = '\t'.join(header2)
        header3_1 = '\t'.join(header3_1)
        header3_2 = '\t\t\t'.join(header3_2)
        header3 = header3_1 + '\t' + header3_2
        header4 = '\t'.join(header4)
        f.write(header0)
        f.write('\n')
        f.write(header1)
        f.write('\n')
        f.write(header2)
        f.write('\n')
        f.write(header3)
        f.write('\n')
        f.write(header4)
        f.write('\n')
        for i in range(trc_marker_data_full.shape[0]):
            f.write(''.join([str(int(trc_marker_data_full[i, 0])), '\t', str(trc_marker_data_full[i, 1]), '\t', '\t'.join(
                [str(trc_marker_data_full[i, j]) for j in range(2, trc_marker_data_full.shape[1])]), '\n']))
        f.close()
    print('TRC file generated at path:', filename)
    return


def read_trc(filename):
    """Reads a TRC file and returns marker data, time, labels, and units."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Extract units (4th line in TRC typically)
    units_line = lines[2]
    if 'mm' in units_line:
        units = 'mm'
    else:
        units = 'm'

    # Extract labels
    labels_line = lines[3]
    labels = labels_line.strip().split('\t')[2:]  # First two columns are Frame# and Time
    marker_labels = [label[:-2] if label.endswith(('_X', '_Y', '_Z')) else label for label in labels[::3]]

    # Load numeric data starting from line 6 (0-indexed)
    data = pd.read_csv(filename, sep='\t', skiprows=4)
    time = data.iloc[:, 1].to_numpy()  # Second column is 'Time'
    marker_data = data.iloc[:, 2:].to_numpy()

    return marker_data, time, marker_labels, units

def compute_distances_from_displacements_xyz(errors):
    """Compute Euclidean distance from XYZ displacements."""
    reshaped = errors.reshape(errors.shape[0], -1, 3)  # (frames, markers, 3)
    distances = np.linalg.norm(reshaped, axis=2)  # (frames, markers)
    return distances

def compute_marker_errors(exp_markers_file, model_markers, time_ik, ik_marker_labels):
    # Read experimental TRC data
    markers_exp, time_exp, labels_exp, units_exp = read_trc(exp_markers_file)

    if units_exp == 'mm':
        markers_exp = markers_exp / 1000.0

    names = labels_exp
    used_names = []
    for name in names:
        if name in ik_marker_labels:
            used_names.append(name)
    names_indices = np.where(np.isin(names, used_names))[0]
    used_indices_exp = []
    for index in names_indices:
        used_indices_exp.append(3*index)
        used_indices_exp.append(3*index+1)
        used_indices_exp.append(3*index+2)

    markers_exp = markers_exp[:, used_indices_exp]
    nm_exp = len(used_indices_exp)

    # Read IK model marker results
    model_markers = model_markers[:, 1:]
    markers_ik = model_markers
    nt_ik, mcols_ik = markers_ik.shape
    assert mcols_ik % 3 == 0, "Number of marker columns must be divisible by 3."
    nm_ik = mcols_ik // 3

    # Align experimental data to model times
    start_ix = np.where(time_exp == time_ik[0])[0][0]
    end_ix = np.where(time_exp == time_ik[-1])[0][0]

    assert nt_ik == end_ix - start_ix + 1, "Time mismatch between experimental and IK data."

    markers_exp = markers_exp[start_ix:end_ix+1, :mcols_ik]
    errors = markers_exp - markers_ik
    RMSEcomps = np.sqrt(np.nanmean(errors**2, axis=0))
    distances = compute_distances_from_displacements_xyz(errors)
    errors = distances
    RMSEmarker = np.sqrt(np.nanmean(distances**2, axis=0))
    RMSEdistance = np.sqrt(np.nanmean(distances**2))

    return errors, RMSEcomps, RMSEmarker, RMSEdistance, names

def generate_ik_xml(IK_template_file, model_file, trc_folder, output_xml, trial_name, mot_filepath, ik_marker_locs):

    # Load the template XML file
    tree = ET.parse(IK_template_file)
    root = tree.getroot()
    ik_tool = root.find("InverseKinematicsTool")

    # Add model file
    model_file_found = False
    for elem in ik_tool.iter("model_file"):
        elem.text = model_file
        model_file_found = True
    if not model_file_found:
        model_file_elem = ET.Element("model_file")
        model_file_elem.text = model_file
        ik_tool.insert(0, model_file_elem)

    # Modify marker file (TRC file)
    for elem in ik_tool.iter("marker_file"):
        elem.text = os.path.join(trc_folder, f"{trial_name}.trc")

    # Modify output motion file
    for elem in ik_tool.iter("output_motion_file"):
        elem.text = mot_filepath

    # Modify time range
    for elem in root.iter("time_range"):
        elem.text = "0 9999"

    # Report marker locations to compute errors per marker
    report_marker_locs_found = False
    for elem in ik_tool.iter("report_marker_locations"):
        elem.text = "true"
        report_marker_locs_found = True
    if not report_marker_locs_found:
        report_marker_locs = ET.Element("report_marker_locations")
        report_marker_locs.text = "true"
        ik_tool.insert(3, report_marker_locs)

    # Set name to save marker positions
    ik_tool.set("name", ik_marker_locs)

    #Save modified setup file
    tree.write(output_xml, encoding="utf-8", xml_declaration=True)
    print(f"Saved: {output_xml}")
    return

## RUN IK FOR EACH FILE
def run_inverse_kinematics(IK_setup_file):
    print(f"Running IK on: {IK_setup_file}")
    ik_tool = opensim.InverseKinematicsTool(IK_setup_file)
    ik_tool.run()

    print(f"Finished IK for {IK_setup_file}")

## COMPUTE ERRORS FOR EACH RUN
def run_markerErrors(exp_trc, ik_trc, trial_name):
    model_markers = np.loadtxt(ik_trc, skiprows=7)
    with open(ik_trc, 'r') as f:
        lines = f.readlines()
        labels = lines[6].strip().split('\t')

    ikNoSuffix = []
    for name in labels:
        if name.endswith("_tx"):
            ikNoSuffix.append(name[:-3])

    time_ik = model_markers[:, 0]

    errors, RMSEcomps, RMSEmarker, RMSEdistance, names = compute_marker_errors(exp_trc, model_markers, time_ik, ikNoSuffix)

    # Write errors and RMSE to file
    folder = os.path.dirname(ik_trc)
    errors_path = os.path.join(folder, f"{trial_name}_errors.txt")
    print(f"Writing errors to {errors_path}")
    with open(errors_path, "w") as f:
        f.write("RMSEdistance: " + str(RMSEdistance))
        f.write("\n")
        f.write("Marker names\n")
        np.savetxt(f, np.array(names).reshape(1, -1), fmt="%s", delimiter="\t")
        f.write("\n")
        f.write("RMSEmarker\n")
        np.savetxt(f, RMSEmarker[None], fmt="%.6f")
        f.write("\n")
        f.write("RMSEcomps\n")
        np.savetxt(f, RMSEcomps[None], fmt="%.6f")
        f.write("\n")
        f.write("Errors\n")
        np.savetxt(f, errors, fmt="%.6f")
    return


def generate_id_xml(ID_template_file, model_file, mot_path, output_xml, ID_output_path, trial):
    """
    Generates multiple ID setup XML files from a template.

    Parameters:
        - template_file: Path to the template XML file.
    """

    # Load the template XML file
    tree = ET.parse(ID_template_file)
    root = tree.getroot()
    id_tool = root.find("InverseDynamicsTool")

    # Add model file
    model_file_found = False
    for elem in id_tool.iter("model_file"):
        elem.text = model_file
        model_file_found = True
    if not model_file_found:
        model_file_elem = ET.Element("model_file")
        model_file_elem.text = model_file
        id_tool.insert(0, model_file_elem)

    # Change results directory
    for elem in id_tool.iter("results_directory"):
        elem.text = ID_output_path

    # Modify coordinates file (mot file)
    for elem in id_tool.iter("coordinates_file"):
        elem.text = os.path.join(mot_path, f"{trial}_coordinates.mot")

    # Modify output storage file
    for elem in id_tool.iter("output_gen_force_file"):
        elem.text = f"ID_results_{trial}.sto"

    # Modify time range
    for elem in root.iter("time_range"):
        elem.text = "0 9999"

    # Modify External loads file
    for elem in root.iter("external_loads_file"):
        elem.text = output_xml.replace(f"setup/{trial}_ID_setup.xml", f"setup/{trial}_ExternalLoads.xml")

    # Save the modified XML file
    tree.write(output_xml, encoding="utf-8", xml_declaration=True)
    print(f"Saved: {output_xml}")


def generate_loads_xml(Loads_template_file, output_xml, mot_filepath):
    """
    Generates multiple ID setup XML files from a template.

    Parameters:
        - template_file: Path to the template XML file.
    """

    # Load the template XML file
    tree = ET.parse(Loads_template_file)
    root = tree.getroot()
    ex_loads = root.find("ExternalLoads")

    # Change force file (sto file)
    for elem in ex_loads.iter("datafile"):
        elem.text = os.path.join(mot_filepath, f"{trial}.mot")

    # Save the modified XML file
    tree.write(output_xml, encoding="utf-8", xml_declaration=True)
    print(f"Saved: {output_xml}")

def run_inverse_dynamics(xml_file):
    print(f"Running ID on: {xml_file}")
    id_tool = opensim.InverseDynamicsTool(xml_file)
    id_tool.run()
    print(f"Finished ID for {xml_file}")

if IK.get():
    for folderfile in os.listdir(trc_path):
        if folderfile.endswith(".trc"):
            trial = os.path.splitext(os.path.basename(folderfile))[0]
            IK_xml_file = os.path.join(IK_output_path, f"setup/{trial}_IK_setup.xml")
            mot = os.path.join(IK_output_path, f"{trial}_coordinates.mot")
            ik_output_trc = os.path.join(IK_output_path, f"setup/IK_Markers_{trial}_ik_model_marker_locations.sto")
            generate_ik_xml(IK_template_path, model_path, trc_path, IK_xml_file, trial, mot, f"IK_Markers_{trial}")
            model = opensim.Model(model_path)
            try:
                run_inverse_kinematics(IK_xml_file)
            except Exception as e:
                print(f"❌ Error: IK failed for {IK_xml_file}")
                print(f"   Reason: {e}")
                continue
            if MarkerErrors.get():
                trc_file_path = os.path.join(trc_path, folderfile)
                run_markerErrors(trc_file_path, ik_output_trc, trial)
    if ID.get():
        for folderfile in os.listdir(trc_path):
            if folderfile.endswith("_coordinates.mot"):
                trial = os.path.splitext(os.path.basename(folderfile))[0][:-12]
                ID_xml_file = os.path.join(ID_output_path, f"setup/{trial}_ID_setup.xml")
                if ExternalLoads.get():
                    ExternalLoads_xml_file = os.path.join(ID_output_path, f"setup/{trial}_ExternalLoads.xml")
                    generate_loads_xml(ExternalLoads_template_path.get(), ExternalLoads_xml_file, mot_path)
                generate_id_xml(ID_template_path, model_path, mot_path, ID_xml_file, ID_output_path, trial)
                # model = opensim.Model(model_path)
                try:
                    run_inverse_dynamics(ID_xml_file)
                except Exception as e:
                    print(f"❌ Error: ID failed for {ID_xml_file}")
                    print(f"   Reason: {e}")
                    continue
    else:
        print("Skipped ID")
else:
    print("Skipped IK")
    if ID.get():
        for folderfile in os.listdir(mot_path):
            if folderfile.endswith("_coordinates.mot"):
                trial = os.path.splitext(os.path.basename(folderfile))[0][:-12]
                ID_xml_file = os.path.join(ID_output_path, f"setup/{trial}_ID_setup.xml")
                if ExternalLoads.get():
                    ExternalLoads_xml_file = os.path.join(ID_output_path, f"setup/{trial}_ExternalLoads.xml")
                    force_mot_path = os.path.join(mot_path, "../..")
                    generate_loads_xml(ExternalLoads_template_path.get(), ExternalLoads_xml_file, force_mot_path)
                generate_id_xml(ID_template_path, model_path, mot_path, ID_xml_file, ID_output_path, trial)
                # model = opensim.Model(model_path)
                try:
                    run_inverse_dynamics(ID_xml_file)
                except Exception as e:
                    print(f"❌ Error: ID failed for {ID_xml_file}")
                    print(f"   Reason: {e}")
                    continue
    else:
        print("Skipped ID")
