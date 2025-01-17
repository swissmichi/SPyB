
![The SPyB Logo](etc/logo-spyb.png)
# Simple Python Browser 24.01
**SPyB** (***S**imple **Py**thon **B**rowser*, pronounced [/ɛs.'paɪ.biː/]) is a simple python-based browser.

## Installation
**If you use a Debian based system (i.e. Ubuntu, Linux Mint), you'll first have to install ``python3.12-venv``**
```bash
apt install python3.12-venv # You may have to run this through sudo
```

To install SPyB, run:
```bash
make install
```
This will create a python virtual environment and install all dependencies for you. <br>

Afterwards, you can run:
```bash
make run
```
This will open SPyB.

### Manual installation

If ``make install`` doesn't work for some reason, follow these instructions.

Create a python virtual environment and install all dependencies using this command:
```bash
python3 make venv .venv && source .venv/bin/activate && .venv/bin/pip3 install -r etc/pyDEPENDENCIES.txt
```

Afterwards, create the configuration file.
```bash
printf "{\n\n}" >> etc/config.conf
```
You may [configure](#configuration) it now.

Then you can open the program by running:
```bash
make run
```
or
```bash
stty -ixon && .venv/bin/python3 src/main.py
```


## How to use

Once you open SPyB, you will be greeted by the URL bar. Just type in a url and the website will open. Once you open a website, the controls will be displayed. 


### Control modes
The **default** control mode is **Vim mode**
You can change the control mode by editing the `controls` value in `etc/config.conf`

| Action                | Vim `vim`     | Nano `nano`   | Emacs `emacs` |             
| --------------------- | ------------- | ------------- | ------------- |
| Scroll Up/Down        | j/k           | Arrow keys    | ^P/^N         |
| Quit program          | q             | ^X            | ^C            |
| Open URL              | o             | ^O            | ^O            |
| Follow link           | f             | ^J            | ^J            |
| Show Terminal         | t             | ^T            | ^T            |
| Find in Page          | /             | ^W            | ^S            |
| Next/Prev Match       | n/N           | n/N           | n/N           |


## Compatability

This program is expected to be able to run on all Linux distributions with Bash and Make. <br>
**This program hasn't ever, does not, and won't ever support Windows** <br>

Currently tested on:
- **Arch Linux with Bash (Fully working)**
- **Linux Mint with Bash (Fully working after installing ``python3.12-venv``)**
- *MacOS with Bash (Requires manual installation)*

## Configuration
| Option                | Value         | Default       |
| --------------------- | ------------- | ------------- |
| ``max_log_size``      | ``int`` Bytes | ``1048576``   | 
| ``max_log_backups``   | ``int``       | ``10``        |
| ``terminal_logger_level`` | [see below](#logger-levels) | ``INFO``      |
| ``file_logger_level`` | [see below](#logger-levels) | ``DEBUG``     |
| ``controls``          | [Control Mode](#control-modes)| ``vim`` |
| ``colors``            | ``dark/bright`` | ``dark``    |

### Logger levels

There are following logger levels:
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

## Make targets

``make install``: Configures ``.venv`` and creates ``config.conf`` <br>
``make run``: Opens SPyB <br>
``make uninstall``: Removes ``.venv`` and ``config.conf`` <br>
``make resetenv``: Removes and reconfigures ``.venv`` <br>
``make updatelibs``: Runs pip3 to update python libraries <br>
``make configdefaults``: Empties ``config.conf``, which makes SPyB use the default configuration