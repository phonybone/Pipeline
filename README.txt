This package faciliatates the construction and running of command
pipelines.  It works under the assumption that each step in the
pipeline can be invoked as a shell command, taking zero or more files
as inputs and emitting zero or more files as outputs.

It supports the following features:
- Pipelines are composed of steps, or "commands";
- Pipelines may invoke other pipelines;
- Each pipeline, and each command, may use python code to determine
  how (or if) it is invoked;
- For each step, or command, the stdout and stderr of the process is
  captures and stored;
- logging of commands is suppported

To implement a new pipeline:
- Create a new class that is derived from
  Pipeline.Pipeline.Pipeline (package.module.class, all named "Pipeline")
- For each command you wish to run, implement a class derived from
  Pipeline.run_cmd.RunCmd.  This class must override get_cmd(),
  get_args(), get_environ(), inputs(), and outputs()
- Implement the run(self) method of your pipeline class to call the
  run() method of each of your commands.  Alternatively, use the
  Pipeline._run_cmds(*cmds) method to run them linearly and handle
  some basic error handling.
- create a Pipeline.Host object, using a config file.  This can be
  empty, but it's a good place to store the locations of your
  executables and other necessary information.  The structure of the
  config file requires one section for each host that the pipeline may
  run on.

fixme: needs examples, or a better API, or both



