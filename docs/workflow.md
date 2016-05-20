# neXtProt integration

neXtProt data model is a combination of external resources with internal ones.
We've got this `integration` task that we execute when our model needs to change because of external resource updates.
This operation is obviously extremely `core` and `critical` for neXtProt and it must not break its database integrity.

Original state (until 2016/01)
------------------------------

Historically, this process is executed from an excel file from which the human operator copy/paste/run bash commands sequencially
in a terminal then checks that everything run as expected with no error (check bash exit code, looking to output(s) and/or database (if state changes)).

This complicated procedure is time consuming, error-prone and painful for the human resource in charge.

The natural idea of workflow
----------------------------

We should automatize this process in a workflow with the following features:

1. automatic: the workflow should be launched once and resumable
2. modular: every logically linked tasks should be grouped together and launched in Extract/Transform/Load layer (as much as possible)
3. error detection/handling: error should be detected as early as possible and should be understandable as much as possible
4. break points: some check points, recovery points and resuming points should be created to control and trace key steps of this workflow
5. persistent task state: every running task state should be saved and accessible to enable resumability.

###### Break points

    We want to set points in our workflow for:

    - validation of key commands (check point)
    - reverting from any point (recovery point)
    - resuming from any point (resume point)

The chosen one: `taskflow`
--------------------------

```
TaskFlow is a Python library for OpenStack (and other projects) that helps make task execution easy, consistent, scalable and reliable.
It allows the creation of lightweight task objects and/or functions that are combined together into flows (aka: workflows) in a declarative manner.

It includes engines for running these flows in a manner that can be stopped, resumed, and safely reverted.
Projects implemented using this library can enjoy added state resiliency, natural declarative construction, easier testability
(since a task does one and only one thing), workflow pluggability, fault tolerance and simplified crash recovery/tolerance (and more).
```

Here is a link to their wiki for more informations: https://wiki.openstack.org/wiki/TaskFlow.

This library provides all that is needed to create our own tasks and workflows.


Converting commands (from data-load.xls) into tasks graph
---------------------------------------------------------

A task should:

- execute an action (in execute())
- be able to recover from this action in case of error (in revert())
- optionally required/receive 1 or many input(s)
- produces/declare 1 or many output(s) (at least stdout and stderr)
- notify any side effects at the level of any persistent volume (database or filesystem)

###### Side effects

    a file could be produced that could contain
    - the volume type (db or fs)
    - the list of logical unit affected

    for example, lets take the example of a simple task that create a file in a specific path
    we could produce the following file:

    type: fs
    path: /tmp/my_file

###### [Tips](https://wiki.openstack.org/wiki/TaskFlow/Best_practices)
    create reuseable tasks that do one thing well in their execute method;
      if that task has side-effects undo those side-effects in the revert method.
    ...

One of the major effort is to group commands found in the excel in tasks and determine what define a Task.
And then compose them into useful structure like workflow and subflows and impose some definition of order
onto the running of our tasks or subflows.

The execution through engine should be controlled, monitored and recoverable.

Subflow 1: init
---------------

    1. the filesystem (FS) on which the workflow is launched has to be checked.
    1.1. check/load environment variables correctly
    1.2. check/load java properties (needed by scripts and ant tasks (see sf 2))
    1.3. check required external softwares (with minimal versions) correctly installed
         jdk, ant, maven, psql, [python, virtualenv]
    2. the database (DB) and schema has to be checked too.
    2.1. database connectable ? schema exists ?
    2.2. init database to initial backup (the dump of the latest release)

Any error is not recoverable and should lead to engine failure.

- building-tools.md
- updating_schemas_task

