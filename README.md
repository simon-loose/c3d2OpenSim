In order to code in Python with OpenSim, you need a properly set up Python environment to run your code. Below you can find a step-by-step guide on how to set up this environment.

# Option 1: PyCharm IDE
1. Download and install PyCharm: https://www.jetbrains.com/pycharm/download/

2. In PyCharm, start a new project. This will give you the following screen:
<img width="1676" height="438" alt="image" src="https://github.com/user-attachments/assets/ff9c99b5-d024-46c5-8494-79bae469b616" />

3. Select the location of your choosing and select Project venv. Under Python version, click Python 3.8 (NOT NEWER, as this might cause compatibility issues). You might have to wait for PyCharm to download and install Python 3.8.

4.  Your new project should now look something like this:
<img width="1913" height="1140" alt="image" src="https://github.com/user-attachments/assets/74b2c177-39b9-4bd0-9bd1-14afa812fad2" />

5. On the bottom left of the screen, select the Terminal. Enter the following lines to install numpy and scipy packages:
```
pip install numpy==1.23.5
pip install scipy==1.10.1
```

6. To install, go to the folder where the OpenSim link to Python is located (in this case C:\OpenSim 4.5\sdk\Python) and enter the following lines to install the opensim package:
```
cd "C:\OpenSim 4.5\sdk\Python"    %Change folder location if necessary
pip install .
```

7. You can now run python code with the opensim package. To test, open and run C3D2OS.py on some c3d files and check if it runs without errors.

# Option 2: Anaconda Prompt
1. Install Miniconda as per the instructions on this site: https://www.anaconda.com/docs/getting-started/miniconda/install

2. Open Anaconda Prompt from the Windows start menu. It should look like this:
<img width="1467" height="742" alt="image" src="https://github.com/user-attachments/assets/dccf19e5-2c87-4517-b4db-5ca443350598" />

3. In the prompt window, create a new conda environment by running the following code. If necessary, enter "y" to continue and install packages:
```
conda create -n opensim_env python=3.8
```

4. Once it's done, activate using the following command. 
```
conda activate opensim_env
```

5. Install the opensim and scipy package with the code below. Again, if necessary, enter "y" to continue and install packages:
```
conda install -c opensim-org opensim
pip install scipy==1.10.1
```

6. You can now run python code with the opensim package. To test, navigate to the directory where c3d2OS.py is located and run with the following commands:
```
cd C:\Users\simlo\Documents\c3d2OpenSim> %your c3d2OS.py location
python c3d2OS.py
```
