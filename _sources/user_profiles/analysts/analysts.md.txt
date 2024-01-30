# Analysts Documentation

This documentation is for people who just want to run the software on preconfigured machines. 

Spack-Manager deploys software through modules.
Typically this will be done by system-administrators, but anyone building software can create custom modules that can be shared.

To use modules you need to add the location of the module files to your `MODULEPATH` environment variable.
The project developers will give you a path to where these modules reside.
You can execute the command

``` console
module use [path/to/modules]
```

to add the Spack generated modules to the list of available modules in your environment.
