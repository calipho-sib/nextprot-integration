Installation for developers
---------------------------

First, you will need to install `virtualenv`, a tool to create isolated Python environments.
The tool creates a folder which contains all the executables and libraries necessary that this project would need.

Install virtualenv via pip:

```
$ pip install virtualenv
```

clone our github project locally:

```
$ cd to_your_project_path/
$ clone https://github.com/calipho-sib/nextprot-integration.git
```

then inside the cloned project create and activate your isolated Python environment `venv`:

```
$ cd nextprot-integration
$ virtualenv [-p /usr/local/bin/pythonX.Y] venv
$ source venv/bin/activate
```

and finally install all bins and libs dependencies for project `nextprot-integration`:

```
$ pip install -r requirements.txt
```

