# Labeling
A simple, efficient tool for multiuser detection task labeling

![UI](https://github.com/wirustea/labeling/blob/master/introduction/ui.png)

## Introduction
This tool is designed for multiuser detection task labeling (Windows,Linux,MacOs)
- **Convient** Annotate **rotated rectangles** by three points
- **Efficient**  labeling task are divided into many sub-tasks by classes, user just need to label one class one time
- **Friendly UI**  

## Requirements
- PyQt5
- PyInstaller (option, if you want to pack as a executable file, very recommand)

## Quick start
0. Clone this project
> ```` bash
> git clone https://github.com/wirustea/labeling
> cd labeling
> ````
1. Specify your classes and weights. There is a json dict in **params.py**, key indicates class name, value indicates weight. Weight means the estimated frequence this class appeared in all images. You can set them for fair assignment or just simply set to a same number.

> ```` python
> # for example:
> labels = {
>     "class one":1,
>     "class two":1,
>     ...
> }
> ````

2. (option but recommand) Pack them as an executable file (support Windows,Linux,MacOs)

> ```` bash
> python pack.py
> ````

Then a folder create, include run.exe(Windows), run(MacOs,Linux), you need to add folder **images** and put all images in it

> ````bash
> # pack as an executable file (recommand)
> ├──PROJECT_ROOT
> │   ├──dist
> │   │   ├──run
> │   │   ├──images
> │   │   │   ├──IMAGE_NAME_ONE
> │   │   │   ├──...
>
> # use source code (not recommand)
> ├──PROJECT_ROOT
> │   ├──run.py
> │   ├──...
> │   ├──images
> │   │   ├──IMAGE_NAME_ONE
> │   │   ├──...
> ````

3. Run **run.py** or **run.exe(Windows) /run(Linux,MacOs)**.

> ```` bash
> python run.py
> ````

4. If you are the orgnizer, you can type "labeling" as super user name to specify labeling users, then it will automatically assign tasks by weights (the assignment infomation is writen in **config.json**)

<!-- ![orgnizer login](https://github.com/wirustea/labeling/blob/master/introduction/orgnizer.png) -->
<img src="https://github.com/wirustea/labeling/blob/master/introduction/orgnizer.png" width="300">
<img src="https://github.com/wirustea/labeling/blob/master/introduction/add.png" width="300">

5. Then, you can copy this folder (**dist** if you pack them, **PROJECT_ROOT** if not) to other users

6. Finally, collect all **result** folder and summary them

> ```` python
> # class_one.json
> {
>    "image_name_one":[
>         [[12,35],[35,46],[24,36],[36,46]],
>         [[22,35],[32,46],[26,46],[56,76]]
>     ],
>     "image_name_two":[
>         # no object
>     ]
>     ...
> }
> ````

## Tips
- If you work on laptop, please use mouse (some operations may not adapt to touch pad )
