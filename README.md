# cptool
A competitive programming tool to automate downloading of test cases and creation of code files.

## What can you do with this?
1. This program can generate test cases for problems from **atcoder.jp** and **codeforces.com** including **gym**.
2. Parse a whole contest -> will save the sample input/output and generate code for selected languages.
```
# format: cf [-g|-gen] <contest/problem id>
> cf -gen 1345
or
> cf -g 1345
```
3. Parse a single problem.
```
> cf -gen abc160_d
```
4. Test a code against parsed input-output.
```
# format: cf [-j|-c[-d]] [-r] <problem>

# test java code
> cf -j a

# test cpp code
> cf -c a

# test cpp code with debug options enabled
> cf -c -d a
> cf -cd a
```
5. Run the code for a specific problem and input custom test case from console.
```
# java
> cf -jr b

# cpp
> cf -c -r
```
6. Add custom input/output to the problem. It will be used to test against next time.
```
> cf -a d
Enter input:
<Enter custome input here>
<Press Enter>

Enter output:
<Enter corresponding correct ouput here>
<Press Enter>
```

## How to use?

#### Make
1. Install dependencies using the below command
```
pip3 install -r requirements.txt
```
2. Make changes in the `settings.yaml` file according to your needs
    - set which languages you need (supports only java acd cpp)
    - set template path for the languages required
3. Run the following command
```
make
```
or
```
make create
make copy
```
This will first create the `cf` excecutable and will then copy it to `/usr/local/bin/`. So that it is available in `path` and can be used from anywhere.

#### Commands
Use `cf -h` to see the help message:
Note: `-d` can only be used with `-c|-cpp|--cpp` cpp options.
```
usage: cf [-h] [-g] [-p] [-m] [-a] [-r] [-j] [-c] [-d] problem

CF Helper Tool

positional arguments:
  problem              Problem link/id

optional arguments:
  -h, --help           show this help message and exit  
  -g, -gen             Generate source code and parse IO
  -p, -parse, --parse  Parse IO for the problem
  -m, -make, --make    Creates a dir with code files
  -a, -add, --add      Add more IO to probelm
  -r, -run, --run      Runs the problem code, and allows you to give input
  -j, -java, --java    Test or run java code
  -c, -cpp, --cpp      Test or run cpp code
  -d, -debug, --debug  Test/run cpp code in debug mode

```
