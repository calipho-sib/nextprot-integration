Installation for developers
---------------------------

First, you will need to install `virtualenv`, a tool to create isolated Python environments.
The tool creates a folder which contains all the executables and libraries necessary by that this project would need.

Install virtualenv via pip:

```
$ pip install virtualenv
```

clone our github project locally:

```
$ cd to_your_project_path/
$ clone https://github.com/calipho-sib/nextprot-integration.git
$ cd nextprot-integration
```

then inside the clones project, create a `venv/` folder to install all bins and libs needed for `nextprot-integration`:

```
$ virtualenv [-p /usr/local/bin/pythonX.Y] venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

