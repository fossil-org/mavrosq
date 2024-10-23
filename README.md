# Mavro (mavrolang)

## Info

### What is Mavro
Mavro is a simple language built from Python.
It is lightweight and flexible.

### Installation
```commandline
pip install mavro
```

### Start using Mavro
1. Open an IDE or text editor (PyCharm Community Edition or PyCharm Professional Edition is recommended)
2. Open a terminal
3. Run the following snippet in your terminal:
    ```commandline
    mavro -c
    ```
4. You can navigate to the main.mav file in your IDE or text editor, and start coding!
5. When you want to run your project, use one of the following commands:
    ```commandline
    mavro # Runs ./main.mav
    mavro path/to/my/directory/ # Runs ./path/to/my/directory/main.mav
    mavro my_mavro_file.mav # Runs ./my_mavro_file.mav
    mavro path/to/my/mavro_file.mav # Runs ./path/to/my/mavro_file.mav
    ```

## Keyword list (57: 30 imported from python, 27 new)
- and - imported from python. Only returns true if both the left-hand AND right-hand conditions are true.
- as - imported from python. Gives something an alias, like an import or context manager.
- assert - imported from python. Raises an AssertionError if the condition is false.
- async - imported from python. Creates an asynchronous function.
- await - imported from python. Wait for a function to complete in an asynchronous function.
- break - imported from python. Breaks out of a loop.
- case - imported from python. Works hand in hand with the `match` keyword to create a `match-case` structure.
- catch - NEW. Works basically identically to python's `except` keyword.
- class - imported from python. Create a class.
- const - NEW. Defines a constant variable.
- constructor - NEW. Create a constructor for an object. Python equivalent: `def __init__`
- continue - imported from python. Skip to the next iteration of a loop.
- del - imported from python. Delete something.
- else - imported from python. Defines what happens if an `if` statement fails.
- else if - NEW. An `if` statement that only runs if the previous `if` statement fails. Python equivalent: `elif`
- end - NEW. Breaks out of indentation.
- entrypoint - NEW. Define the entrypoint function of a Mavro file.
- enumeration - NEW. Defines an Enum. Python equivalent: `class Foo(enum.Enum)`
- extends - NEW. Defines inheritance in a class definition. Python equivalent: `class Foo(Bar)`
- false - NEW. A wrapper for python's `False`
- finally - imported from python. Paired with the `try` keyword. ALWAYS runs, no matter what.
- for - imported from python. Creates a loop that iterates over an iterable object.
- from - imported from python. Has two usages: 1. Import a specific object from a module. 2. Define from what an exception is raised.
- function - NEW. Defines a function. Python equivalent: `def`
- global - imported from python. Finds a global variable and places it in the local scope.
- if - imported from python. Run a block of code if a condition is met.
- import - imported from python. Import a **python** module or package. It is not compatible with Mavro modules and packages.
- in - imported from python. Checks if an iterable object contains a value.
- is - imported from python. Compare the IDs of two objects.
- lambda - imported from python. Create an anonymous function.
- let - NEW. Defines a variable that can be changed.
- manager - NEW. Create a context manager for an object. Python equivalent: `with`
- match - imported from python. Works hand in hand with the `case` keyword to create a `match-case` structure.
- method - NEW. Create a method.
- nonlocal - imported from python. Creates a nonlocal variable.
- not - imported from python. Inverts a boolean value.
- null - NEW. A wrapper for python's `None`
- only private - NEW. The following code (until a usage of `end`) can only be run if the file was built directly, not as a requirement.
- only public - NEW. The following code (until a usage of `end`) can only be run if the file was built as (or as part of) a requirement by the `requiry` package, not directly.
- openfile - NEW. Opens a file with customizable permissions. Python equivalent: `with open`
- or - imported from python. Returns true if the left-hand OR right-hand values are true.
- package - NEW. Imports a Mavro package. These packages include for. ex. `requiry`, which is used to import Mavro files.
- pass - imported from python. Does absolutely nothing. It is practically useless since Mavro doesn't require anything after an indent.
- public - NEW. Makes the function, class, method, or constant public.
- raise - imported from python. Raises a fatal error.
- return - imported from python. Returns a value from a function.
- require - NEW. Retrieve a Mavro module. Wrapper for `mavro.pkg.requiry::findService`
- savelocation - NEW. Save all global and local variables in the current location to a variable called `here`. Required to access `public` stuff.
- starter - NEW. Create a function that runs when the object is run using `startprocess`
- startprocess - NEW. Run an object's starter method.
- static - NEW. Makes function static.
- true - NEW. A wrapper for python's `True`
- try - NEW. Try a block of code for errors, etc.
- until - NEW. Loops until a condition is true. Python equivalent: `while not`
- while - imported from python. Loops while a condition is true.
- yield - imported from python. Yields a value from a generator function.# mavro