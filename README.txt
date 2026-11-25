Suspect Statements Solver
Author: Brendan McClurg

1. PURPOSE
   SuspectStatements.py enumerates the 32 possible guilt assignments for
   Paul, Quinn, Rob, Sid, and Todd. It checks whether every suspect whose
   statement is enforced is innocent and truthful or guilty and lying.
   It writes every valid assignment and, when more than one is valid,
   a cross-solution determination for each suspect.

2. PYTHON VERSION AND DEVELOPMENT ENVIRONMENT
   Development IDE: Eclipse IDE 2026-03 (4.39.0).
   Eclipse build ID: 20260305-0817.
   Python development extension: PyDev.
   PyDev version: 13.1.0.202509210817.
   Registered Python interpreter: Python 3.12.
   Minimum Python compatibility: Python 3.10.

   Eclipse provides the integrated development environment, while PyDev
   provides Python development support. The configured Python interpreter
   executes the program independently of the Java Development Kit (JDK)
   used by Eclipse.

   Python 3.10 or later is required because the program uses structural
   pattern matching through match/case statements.

   The program uses only standard Python libraries, including sys, enum,
   and typing. No third-party libraries are required.

3. FILES
   SuspectStatements.py          Python source code.
   README.txt                   Technical and operating documentation.
   suspects_out.txt             Generated program output.

   The program is self-contained and does not require external input
   files or third-party libraries.

   An optional suspects_in.txt file may be created to specify which
   statements are enforced. Alternatively, the active statement set
   may be supplied through command-line arguments.

   If neither input source provides a specification, the program
   defaults to enforcing all five statements.

   Every successful execution creates or overwrites suspects_out.txt
   in the current working directory.

4. COMPILATION AND SYNTAX VERIFICATION
   Open a terminal or command prompt in the folder containing the source.

   Verify the installed Python interpreter version with:

       python --version

   Verify source-code syntax and bytecode compilation with:

       python -m py_compile SuspectStatements.py

   Successful execution of py_compile generates Python bytecode within
   the __pycache__ directory. These generated files are not required
   for distribution or normal program execution.

   Alternatively, open the project in Eclipse using PyDev and execute
   SuspectStatements.py with the configured Python interpreter.

   The program does not require a separate compilation step before
   execution. Python performs bytecode compilation automatically when
   executing the source file.

5. INPUT SELECTION AND EXECUTION
   The program accepts an optional list of command-line arguments:

       python SuspectStatements.py COUNT NAME1 NAME2 ...

   COUNT is the number of supplied suspect names. Valid names are Paul,
   Quinn, Rob, Sid, and Todd (case-insensitive). Each name may appear at
   most once. Command-line arguments override suspects_in.txt.

   Without command-line arguments, the program reads the first nonblank
   line of suspects_in.txt in the current working directory. For example:

       4 Paul Rob Sid Todd

   To execute the program using the optional input file:

       python SuspectStatements.py

   If the input file is absent, unreadable, or empty, the program enforces
   all five statements. If supplied input is malformed, the output explains
   the rejection and the program uses all five statements instead. An invalid
   input therefore does NOT produce an answer for the rejected selection.

   Every run overwrites suspects_out.txt in the current working directory.
   Save or rename that file before starting the next run.

   ECLIPSE CONFIGURATION

   Configure the Python interpreter through:

       Window > Preferences > PyDev > Interpreters > Python Interpreter

   Run the program using the PyDev Python Run configuration.

   Command-line arguments may be supplied through:

       Run Configurations > Python Run > Arguments

   The working directory must contain suspects_in.txt when the optional
   input file is used. The generated suspects_out.txt file is written
   to the configured working directory.

6. SAMPLE AND ADDITIONAL RUNS
   All five statements; expected result: one valid assignment:

       python SuspectStatements.py 5 Paul Quinn Rob Sid Todd

   Quinn declines to make a statement; expected: two assignments:

       python SuspectStatements.py 4 Paul Rob Sid Todd

   Additional named-subset run; expected: four assignments:

       python SuspectStatements.py 3 Paul Rob Todd

   Validation run - incorrect count; expects a rejection note and fallback:

       python SuspectStatements.py 4 Paul Rob Sid

   Validation run - unknown name; expects a rejection note and fallback:

       python SuspectStatements.py 3 Paul Rob Bob

   Validation run - repeated name; expects a rejection note and fallback:

       python SuspectStatements.py 3 Paul Sid Sid

   Boundary run - no statements enforced; expected: 32 valid assignments:

       python SuspectStatements.py 0

   The saved output files corresponding to the first six commands are
   identified by their matching filenames listed in Section 3.
   The three validation examples each report one solution for the
   fallback five-statement scenario, not a solution to the rejected
   specification.

7. OUTPUT
   All solution output is written as a labeled .txt file. Each solution
   gives a guilty or innocent verdict for every suspect in the order
   Paul, Quinn, Rob, Sid, Todd. Runs with multiple valid assignments
   also summarize whether each suspect is definitely guilty, definitely
   innocent, or undetermined across the complete solution set.

   Console output reports successful file creation or applicable input
   and file-processing errors.