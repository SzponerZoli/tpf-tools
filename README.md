# TPF Tools
## What is TPF?
TPF is a file extension made with ChatGPT, called **T**ext **P**icture **F**ormat. It stores every pixel's color in a line.
The formatting looks like this when there is a 100x100 picture and the (0,1) coordinates are white:
```
1 100x100
2 (0,1) (255, 255, 255)
3 ...
```
## What's included in TPF Tools?
There is a TPF file viewer with you can view TPF pictures.
There is a TPF Converter that can convert TPF to PNG and JPG and vice versa.
There is a TPF Paint there you can save pictures in .tpf format.

## Requirements
- Python 3
  - PyQt6
  - Pillow
  - Qtawesome
### Installing requirements
- Windows
  - Download and install Python from www.python.org/downloads
  - open terminal at the TPF Tools folder and type: ```python -r requirements.txt```
- Linux
  - Install python with your package manager. e. g. ```sudo apt install python3```
  - open terminal at the TPF Tools folder and type: ```python -r requirements.txt```
