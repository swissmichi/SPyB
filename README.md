
![The SPyB Logo](etc/logo-spyb.png)
# Simple Python Browser 24.01
**SPyB** *(**S**imple **Py**thon **B**rowser)* is a simple python-based browser.

## Installation

To install SPyB, run:
```bash
make install
```
This will create a python virtual environment and install all dependencies for you. 

Afterwards, you can run:
```bash
make run
```
This will open SPyB.

## How to use

Once you open SPyB, you will be greeted by the URL bar. Just type in a url and the website will open. Once you open a website, the controls will be displayed. 


### Control modes
The **default** control mode is **Vim mode**

|Action                 | Vim mode      | Nano mode     | Emacs mode    |             
| --------------------- | ------------- | ------------- | ------------- |
| Scroll Up/Down        | j/k           | Arrow keys    | ^P/^N         |
| Quit program          | q             | ^X            | ^X^C          |
| Open URL              | o             | ^W            | ^X^F          |
| Show Terminal         | t             | ^T            | ^T            |
| Find in Page          | /             | ^W            | ^S            |
| Next/Prev Match       | n/N           | n/N           | n/N           |
