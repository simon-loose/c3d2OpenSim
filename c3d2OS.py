import tkinter as tk
import os, sys
import scipy.signal
import opensim as osim
import numpy as np
from tkinter import filedialog

"""
Run this code to convert c3d files to trc and mot files for opensim.
Code also works for c3d files containing only mocap or force data.

If using miniconda, use the following lines to run:
conda activate *your environment*
cd *folder where this code is located*
python C3D2OS.py
"""
FilterOrder = 4
CutoffFrequency = 12


def convert_c3d(c3d_dir, c3d_file):

    FORCE_THRESHOLD = 10 # Force data will be set to zero if below threshold

    # Read c3d file
    adapter = osim.C3DFileAdapter()
    adapter.setLocationForForceExpression(1)
    tables = adapter.read(os.path.join(c3d_dir, c3d_file))

    # Get marker data from c3d file
    markers = adapter.getMarkersTable(tables)

    # Rotate marker data
    rotate_data_table(markers, [1, 0, 0], -90) # Assumes that z is pointing up vertically in Vicon
        
    # Write marker data to .trc file
    trcAdapter = osim.TRCFileAdapter()
    trcAdapter.write(markers, os.path.join(c3d_dir, c3d_file.replace('.c3d','.trc')))
            
    # Get force data from c3d file
    forces = adapter.getForcesTable(tables)
    t = forces.getIndependentColumn()
    labels = forces.getColumnLabels()

    # create index of samples where force is below threshold
    numFPs = int(forces.getNumColumns()/3)
    r = len(t)
    below = np.full((numFPs,r), False)
    for fpID in range(numFPs):
        f = forces.getDependentColumn('f' + str(fpID + 1))
        fz = np.zeros(r)
        for i in range(r):
            fz[i] = f[i][2]
        below[fpID,:]=fz<FORCE_THRESHOLD

    # set force to zero where fz < threshold
    for i in range(r):
        vec = forces.getRowAtIndex(i)
        if below[0,i]:
            for j in range(3):
                vec[j]=osim.Vec3(0,0,0)
        if below[1,i]:
            for j in range(3,6):
                vec[j]=osim.Vec3(0,0,0)
        forces.setRowAtIndex(i,vec)

     # Rotate forces (Assumes that z is pointing up vertically in QTM)
    rotate_data_table(forces, [1, 0, 0], 90)
    rotate_data_table(forces, [0, 1, 0], 180)
    rotate_data_table(forces, [0, 0, 1], 180)

    # conversion of unit (f -> N, p -> mm, tau -> Nmm)
    mm_to_m(forces, 'p1')
    mm_to_m(forces, 'p2')
    mm_to_m(forces, 'm1')
    mm_to_m(forces, 'm2')

    # interpolate and fit splines to smooth the data
    list_mat = list()
    sample_rate = 1/(t[1]-t[0])
    for label in labels:
        f = forces.getDependentColumn(label)
        list_mat.append(lowpass_filter(f, label, sample_rate, FilterOrder, CutoffFrequency, padtype="odd", output_dir=c3d_dir))

    # construct the matrix of the forces (forces, moments, torques / right and left)
    # (type opensim.Matrix)
    forces_task_np = np.array(list_mat)
    forces_task_mat = osim.Matrix(len(t), 18)
    for n in range(6):
        for j in range(3):
            for i in range(len(t)):
                forces_task_mat.set(i, 3 * n + j, forces_task_np[n, j, i])

    # export forces
    labels_list = ['L_ground_force_vx', 'L_ground_force_vy', 'L_ground_force_vz',
                'L_ground_force_px', 'L_ground_force_py', 'L_ground_force_pz',
                'L_ground_torque_x', 'L_ground_torque_y', 'L_ground_torque_z',
                'R_ground_force_vx', 'R_ground_force_vy', 'R_ground_force_vz',
                'R_ground_force_px', 'R_ground_force_py', 'R_ground_force_pz',
                'R_ground_torque_x', 'R_ground_torque_y', 'R_ground_torque_z']
    force_sto = create_opensim_storage(t, forces_task_mat, labels_list)
    force_sto.setName('GRF')
    force_sto.printResult(force_sto, c3d_file.replace('.c3d',''), c3d_dir, 0.001, '.mot')

def rotate_data_table(table, axis, deg):
    """
    Efficiently rotate data in an OpenSim Table.
    """
    R = osim.Rotation(np.deg2rad(deg), osim.Vec3(axis[0], axis[1], axis[2]))
    for i in range(table.getNumRows()):
        vec = table.getRowAtIndex(i)
        vec_rotated = R.multiply(vec)
        table.setRowAtIndex(i, vec_rotated)

def mm_to_m(table, label):
    """
    Convert measurements from millimeters to meters in an OpenSim Table.
    """
    c = table.updDependentColumn(label)
    for i in range(c.size()):
        c[i] = osim.Vec3(c[i][0] * 0.001, c[i][1] * 0.001, c[i][2] * 0.001)

def get_valid_padlen(signal, A, B):
    """ if signal is too short the defaultpadlen needs to change in order for the scipy filtfilt to work with padding """
    padlen = 3 * max(len(A), len(B))  # from scipy default
    signal_length = len(signal)
    if signal_length <= padlen:
        padlen = signal_length - 1
    return padlen

def lowpass_filter(signal, label, sampling_freq, FilterOrder, CutoffFrequency, padtype="odd", output_dir='.'):
    order = FilterOrder
    cutoff = CutoffFrequency
    # instantiate variables
    n_frames = signal.nrow()
    signal_np = np.zeros((n_frames))
    smooth_signal_list = []
    # filter settings
    nyq = 0.5 * sampling_freq
    # The double filter should have 1/sqrt(2) transfer at cutoff, so we need correction for filter order
    cutoff = cutoff / (np.sqrt(2) - 1) ** (0.5 / order)
    Wn = cutoff / nyq
    B, A = scipy.signal.butter(order, Wn, output="ba")
    # convert Vec3 into np.array
    for i in range(3):
        for j in range(n_frames):
            signal_np[j] = signal[j][i]  # extract component at each time step
        
        # padding
        padlen = get_valid_padlen(signal_np, A, B)

        # smoothing
        smooth_signal_list.append(scipy.signal.filtfilt(B, A, signal_np, padtype=padtype, padlen=padlen))


    return np.array(smooth_signal_list)

def create_opensim_storage(time, data, column_names):

    sto = osim.Storage()
    sto.setColumnLabels(list_to_osim_array_str(['time'] + column_names))
    for i in range(data.nrow()):
        row = osim.ArrayDouble()
        for j in range(data.ncol()):
            row.append(data.get(i, j))

        sto.append(time[i], row)

    return sto

def list_to_osim_array_str(list_str):
    """Convert Python list of strings to OpenSim::Array<string>."""
    arr = osim.ArrayStr()
    for element in list_str:
        arr.append(element)

    return arr
# start convert_c3d when running directly from command line

def main_gui():
    def select_file_type(selected_type):
        root.destroy()
        main(selected_type)

    root = tk.Tk()
    root.title("Select File Type")
    tk.Label(root, text="Choose the file or folder you want to process:").pack(pady=10)

    tk.Button(root, text="File", command=lambda: select_file_type("file"), width=20).pack(pady=5)
    tk.Button(root, text="Folder", command=lambda: select_file_type("folder"), width=20).pack(pady=5)

    root.mainloop()


def main(file_type):
    root = tk.Tk()
    root.withdraw()

    if file_type == 'file':
        c3d_file = filedialog.askopenfilename(title="Select a c3d file", filetypes=[("c3d only", "*.c3d")])
        convert_c3d(os.path.dirname(c3d_file), os.path.basename(c3d_file))

    if file_type == 'folder':
        # c3d_dir = args.c3d_dir
        c3d_dir = filedialog.askdirectory(title="Select a folder containing c3d files")
        # Your existing code to process C3D files
        for file_name in os.listdir(c3d_dir):
            if file_name.endswith('.c3d'):
                convert_c3d(c3d_dir, file_name)

    sys.exit()

# Ensure your existing functions like convert_c3d are included here


if __name__ == '__main__':
    main_gui()