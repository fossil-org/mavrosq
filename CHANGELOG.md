# 0.14

- new init keyword
  - creates an object based on the type of the variable
  - example:
```
const Person person = init name="Bob", age=21
const Main main = init
const Number number = init 100
```
- new `types` package with some simple types
  - example:
```
package types

const Any value = 20
function main
end
const Function main_function = main
# Method, Class and Object types also exists
```
- new `Ht` system merge and syntax
  - code between `<<` and `>>` will be treated as a function clause
  - example:
```
const Function greet = <<
    function inner name
        Console::print "Hello, {name}!"
    return inner
>>

<<Console::print "hi">>

const int age = <<return 21>
const bool adult = <<
    if age >= 18
        return true
    else
        return false
>>
```
- fixed `requiry` package
- changed `root` keyword to `deco`
- `System` merge is now `String` and `BaseString` with `method=ORIGIN` instead of `string` with `method=SPARSE`
- many qol changes
- many bug fixes
- removed the `program ended successfully (returned code 0)` text when your program is finished
- replaced the `press return to submit a report, ctrl-c to exit` prompt when your program encounters an error with a simple hint and a url to get help
- single-quoted strings (`'`) are no longer automatically mapped to double-quoted strings (`"`)
- `paint` function from `paint` package now adds `$reset$` at the end of your string automatically

# 0.15

- `Ht` is no longer packaged and system merged by default
- - to use `<<` and `>>` syntax, add `package ht` then `initpkg Ht` to your program
- new package `workspace`
- - not packaged by default, use `package workspace` to package
- - not system merged by default, use `System::merge workspace.Workspace(), method=System.ORIGIN` to merge
- - allows you to quickly manage files and paths in your project
- new `initpkg` keyword
- - info in `README.md`
- updated keyword list in `README.md`

# 0.16

- `initpkg` keyword removed
- `package` keyword reworked
- - use `package hello` to get a package (just like before)
- - use `package hello init` to get a package and create a local variable for it's main object (`package hello init` translates to
```
package hello
const type[hello.Hello] Hello = hello.Hello
```
and `package hello init value=1` translates to
```
package hello
const hello.Hello Hello = hello.Hello(value=1)
```
)
- - to pass no arguments to the `init` variant of `package`, use `pass` as the first parameter.
- new package `arrow` with syntax `->`
- - typecasts a value
- - example:
```
package arrow init pass

Console::print type(21 -> String)
# output: String
```
- - this allows for this syntax too: `remark 21 -> Console::print`
- - or: `remark "Enter your name: " -> Console::input -> Console::print`
- many qol changes