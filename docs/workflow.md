# Integration workflow refactoring documentation

neXtProt data model is a combination of external resources with internal ones.
We've got an `integration` task that is executed each time our model has to change because of external resource updates.
This operation is obviously `core` and `critical` for neXtProt and it must not break the integrity of our database.

Original state (until 2016/01)
------------------------------

Historically, this process is executed from an excel file from which the human operator copy/paste/run bash commands sequencially
in a terminal then checks that everything run as expected (check bash exit code, looking to output(s) and/or database (if state changes)).

This manual approach is prone to error because this process has not been automated and errors could be complicate to figure out.

This complicated procedure is time consuming, error-prone and painful for human resource in charge.

Refactoring
-----------

A refactoring of this process should be done with the following features:

1. automatic: the workflow should be launched once
2. modularity: common codes should be grouped together and launched in Extract/Transform/Load layer (as much as possible)
3. error detection/handling: error should be detected as early as possible
4. break points: check points, recovery points and resuming points to trace all workflow steps

1 - Categorizing commands
-------------------------

- Categorize each command by type + exit type (ant task, bash command)
- group commands by ETL
- categorize each command block by Prepare/Extract/Transform/Load categories

One of the first step is command categorisation

- pure bash: cd, setvar,...
- ant tasks
- psql

Use/case ?
Once the categorisation has been done, we can generate a graph of command dependencies.
Knowing how a specific command affect the workflow is valuable.

2 - Break points
----------------

We want to set points in our workflow:

- validation of key commands (check point)
- reverting from any point (recovery point)
- resuming from any point (resume point)

2.1 - Proposal: Tree data structure

We would like to identify uniquely any point in the workflow to be able to revert/resume to/from anywhere.

To add those features we want:

- to identify each command uniquely.
- to have orderable ids depending on the sequence of processed command

Those points should be set depending on kind of event:

-	on error: set resume point in command that crashed (see if internal changed)
-	on recovery: resume from the last resume point

A tree is a natural data structure that have those characteristics:

-	each node is a script
-	each leave is a command

2.2 - Algorithm

  2.2.1. Parse hierarchy of workflow scripts and generate a code tree

  2.2.1. Navigate this tree with cursors for current command id

    Note: 'build-code' block particularity
       - 'build-code' block is totally independent from the rest
       - all other commands are all dependent on 'build-code'

    This piece should not be added to the tree: each time the source change (fix for example), 'build-code'
    should be run again and the resuming should be done right from the failing command.



3. Integration Workflow

Here are the steps to execute:

Preparing exec system:

-A check host system (softs + envs) [always run]
-B update all git repos (w/ scripts + libs + apps that will run to fullfill integration) [run if local branch behind remote branch]
-B.a check status/update np_loaders git repo (linked with building code)
-B.b check status/update np_perl_parsers git repo
-B.c check status/update np_cv git repo
-C loading java properties (needed by scripts and ant tasks) [always run]
-D checking np_annot_uat database (the integration db) [always run]

Building and installing code

-E integration perl [rerun if git repo 'np_perl_parsers' pulled]
-F integration jars [rerun if git repo 'np_loaders' pulled]
-G np_mappings jar [rerun if git repo 'np_loaders' pulled]

Updating np_annot_uat schemas

-H np_annot_uat.np_mappings schema
-I np_annot_uat.nextprot schema



