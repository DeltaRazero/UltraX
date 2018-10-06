
<h1 align="center">
    <a href="#">
        <img src=".\doc\rsrc\img\UltraX_Logo_temp2.png" alt="UltraX_logo" width="110"></a>
    <br>
    <a href="#">
        <img src=".\doc\rsrc\img\ultrax_text.png" alt="UltraX" width="210"></a>
    <br>
</h1>

<h4 align="center">
    Object-oriented MDX compiler for MXDRV2 made with Python3.
</h4>

<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.5 | 3.6 | 3.7-blue.svg?style=flat-square"
            alt="python"></a>
    <img src="https://img.shields.io/badge/version-v0.1_(incomplete)-red.svg?style=flat-square"
        alt="version">
    <a href="https://github.com/DeltaRazero/UltraX/issues">
        <img src="https://img.shields.io/github/issues/deltarazero/UltraX.svg?style=flat-square"
            alt="github_issues"></a>
    <a href="https://opensource.org/licenses/LGPL-3.0">
        <img src="https://img.shields.io/badge/license-LGPL_v3-blue.svg?style=flat-square"
            alt="license"></a>
</p>

<p align="center">
    <a href="#about">About</a> •
    <a href="#features">Features</a> •
    <a href="#download">Download</a> •
    <a href="#credits">Credits</a> •
    <a href="#related">Related</a> •
    <a href="#License">License</a>
    <br/>
    [ <a href="#License">日本語版はこちら</a> ]
</p>


## About

UltraX is a compiler that creates MDX performance files for the Sharp X680x0 music driver 'MXDRV2' made with Python3. 

UltraX is developed with object-oriented programming (OOP) and modularity in mind. UltraX also includes its own small library for MDX creation so that future use and creation of other compilers are made easier.


## Overview

UltraX is split up into the following scripts:
- `UltraX.py`: the main compiler to generate .MDX performance files.
- `UltraX_Tool.py`: a toolbox featuring 


Globally, the following features are supported:
- Native Python compiling to .MDX performance files
- Native Python converting PCM to OKI/DIALOGIC ADPCM
- Supports all commands of the MXDRV v2.06+16/02EX specification
- Sample support for:
    - Single channel ADPCM mode
    - EX-PCM mode (PCM-4, PCM-8, Rydeen, Mercury-Unit, etc.)
- MML text file compiling
    - Macros and pattern macros
    - PPMCK styled envelope macros
    - Extended compile time macros and commands
- DefleMask .dmf file (YM2151+SPCM mode) compiling
    - YM2151 + ADPCM support
    - Support for almost every tracker command
    - Automatic SPCM --> OKI ADPCM --> PDX conversion

UltraX's core compiling system and toolset ("pymdx") is written in a modular manner so that everybody could write their own compiler specialised in whatever way is desired.

pymdx can create and export the following:
- MDX object
    - Header object
    - Tone definition object
    - Track data (MDX commands), individually per channel
- OKI ADPCM sample (4 bit)
- PDX object

*See the [documentation](#) for an indepth explanation of all functions included in pymdx.*


## Dependencies

UltraX relies on Python's standard library (3.x), libPyFMT.
* Python standard library:
`ntpath, os, struct, sys, wave`

* libPyFMT※:
`opmn`

    ※ *"libPyFMT" is a library for FM patch creation/manipulation, **it will be added later**.*


## Goals

The following list presents the current ambitions of the project and if they are reached yet:

- [ ] Provide a MXDRV2 compiler on a modern operating system
- [ ] Provide additional toolset for MXDRV2
- [ ] Provide a way to convert DefleMask .dmf files to .MDX (+ .PDX)


## Changelog

*See [CHANGELOG.md](#).* 


## Contribution

Contributing to this project to improve it is always welcome. I highly recommend to submit pull requests instead of maintaining your own fork.

*See [CONTRIBUTING.md](#) for details on the process for submitting pull requests.*


## Credits

I would like to thank the following people for making UltraX possible:

- YURAYSAN, for the MXDRV2 file format documentation.
- Tetsuya Isaki, for the fast OKI/DIALOGIC ADPCM encoding implementation.
- ValleyBell, the MAME team and David Lindecrantz (Optiroc), for the fast OKI/DIALOGIC ADPCM decoding implementation.
- Vampirefrog, for additional documentation.
- milk., K.MAEKAWA, Missy.M and Yatsube, for making MXDRV. :)


## License

All included scripts, modules, etc. are licensed under the LGPL v3 license, unless stated otherwise in sourcecode files.

*See [LICENSE.md](#) or [Opensource.org – LGPL3](https://opensource.org/licenses/LGPL-3.0).*

&nbsp;
