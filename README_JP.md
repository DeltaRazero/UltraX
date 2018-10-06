
<h1 align="center">
    <a href="#">
        <img src="D:\Programming\UltraX\temp\UltraX_Logo_temp2.png" alt="UltraX_logo" width="110"></a>
    <br>
    <a href="#">
        <img src="D:\Programming\UltraX\temp\ultrax_text.png" alt="UltraX" width="210"></a>
    <br>
</h1>

<h4 align="center">
    Python3で作られたMXDRV2用のオブジェクト指向MDXコンパイラ。
</h4>

<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.5 | 3.6 | 3.7-blue.svg?style=flat-square"
            alt="python"></a>
    <img src="https://img.shields.io/badge/バージョン
-v0.1_(incomplete)-red.svg?style=flat-square"
        alt="version">
    <a href="https://github.com/DeltaRazero/UltraX/issues">
        <img src="https://img.shields.io/github/issues/deltarazero/UltraX.svg?style=flat-square&label=%e5%95%8f%e9%a1%8c"
            alt="github_issues"></a>
    <a href="https://opensource.org/licenses/LGPL-3.0">
        <img src="https://img.shields.io/badge/ライセンス-LGPL_v3-blue.svg?style=flat-square"
            alt="ライセンス"></a>
</p>

<p align="center">
    <a href="#説明">説明</a> •
    <a href="#概要">概要</a> •
    <a href="#download">Download</a> •
    <a href="#特別な感謝">特別な感謝</a> •
    <a href="#related">Related</a> •
    <a href="#ライセンス">ライセンス</a>
    <br/>
    [ <a href="#">English version here</a> ]
</p>


## 説明

UltraXは、Python3で作成されたSharp X680x0音楽ドライバ「MXDRV2」のMDXパフォーマンスファイルを作成するコンパイラです。

UltraXは、オブジェクト指向プログラミング（OOP）とモジュール性を念頭に開発されています。 UltraXにはMDX作成用の独自の小さなライブラリが含まれているため、将来の使用や他のコンパイラの作成が容易になります。


## 概要

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


## 特別な感謝

以下の人々にUltraXを現実としたことに対して礼を言いたいです:

- YURAYSAN、MXDRV2ファイル形式のドキュメント用。
- Tetsuya Isaki、迅速なOKI / DIALOGIC ADPCMエンコーディングの実装。
- ValleyBell、MAMEチームのとDavid Lindecrantz (Optiroc)、迅速なOKI / DIALOGIC ADPCMデコードの実装。
- Vampirefrog、追加のドキュメント。
- milk.、K.MAEKAWA、Missy.M、Yatsube、MXDRV製作用。 :)


## License

含まれているすべてのスクリプト、モジュールなどは、ソースコードファイルに別段の記載がない限り、「LGPL v3」ライセンスの下で使用許諾されます。

*[LICENSE.md](#)または[Opensource.org – LGPL3](https://opensource.org/licenses/LGPL-3.0)を参照してください。*

&nbsp;
