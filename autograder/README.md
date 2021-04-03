## Autograder instructions

-------------------

This archive contains the autograder code used to evaluate solutions submitted for the first lab assignment.

The archive contains two python scripts (`autograder.py` and `grader_lab1.py`) and two folders (`solutions/` and `test_suites/`).

In the `solutions/` folder, you should insert your archived solution for the first lab, formatted as described in the instructions. 
Additional details for adding your solution in the "solutions/" folder are given below.

The `test_suites/` folder contains JSON files with tests for three state search descriptors provided along with the lab assignment: `ai`, `istra`, and `3x3 puzzle`.
The autograder will evaluate your solution on these three files and their corresponding heuristic descriptors.
You are welcome to come up with your own test cases, just make sure that they follow the format of the provided JSON files in order to be evaluated properly.
**NOTE:** In the final evaluation of your solution, we will test your solution with maps which are not publicly available.

The autograder will perform three steps when evaluating your solution in the following order:
1. validating that the folder structure is as requested,
2. attempting to compile the solution,
3. evaluating the solution against the provided test cases.
If steps 1 or 2 fail, the subsequent step(s) are not executed.

The autograder's general output will be printed in a single file for all solutions provided inside the `solutions/` folder.
In addition, a detailed output for each provided solution will be printed inside another folder (which will be created during run).

-------------------

Steps for obtaining autograder output for archived solution:

1. Place the zip archive with solution in a folder named after your JMBAG, and place that folder inside `solutions/` folder. 
For example, if your JMBAG is `0123456789`, you should first create a zip archive titled `0123456789.zip` following the instructions for the assignment, 
and then place that archive inside `01234566789/` folder, which should finally be placed in the `solutions/` folder. 
The full path to the zip archive should then be: `solutions/0123456789/0123456789.zip`.
An example folder with a zip archive containing (non-working) solution is given in the `solutions/` folder.

2. Run the following command to obtain the results for tests placed inside `test_suites/` folder:

```python
python autograder.py --solutions solutions --test_suites test_suites --evaluation_log full.log --student_log_dir student_logs
```
3. Check out the general output in `full.log` file and a more detailed output (in case of failed tests) in the log files inside "student_logs/" folder.

-------------------

The code for autograder was tested with Python 3.8.

We suggest you use `conda` for creating a virtual environment with that specific version of Python. 
Instructions for installing conda are available here: https://docs.conda.io/en/latest/miniconda.html

Once you install conda, you can run the following command to create a Python 3.8 environment:

```bash
conda create -n autograder_env python=3.8
```

Once the environment is created, you can activate it using:

```bash
conda activate autograder_env
```

Then you can run the above given command for obtaining autograder's output.

-------------------

For C++ solutions on Windows: autograder assumes that you are using `mingw32-make` as a compiler and that it is defined in the PATH variable. 
If you are using some other compiler, make sure that you replace `mingw32-make` with the name of your compiler in the line 66 of `autograder.py` (and that your compiler is defined in the PATH variable).