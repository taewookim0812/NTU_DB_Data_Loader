# NTU DB Data Loader

* Please refer to the link below for more detailed information about NTU DB:
(http://rose1.ntu.edu.sg/datasets/actionrecognition.asp)
(https://github.com/shahroudy/NTURGB-D)
<br />

* This python code provides a NTU DB data loader which loads the data from the hard disk 
and make them a structured object. The folder structure of your NTU DB
should be organized as described in the following section, but if you want to use
your own folder, you can modify the part of the setting path of this code and use it.

* We also provide a function for marking exception file. 
There are some errors in data which the skeleton and the performer are not matched or missing.
These data can be excluded by marking them and putting on a list.
After making the exception file list, you can utilize it to separate the error data from the original.          

## Data Loading  

***Notice

Before you use this code, Your NTU database files should be organized as following.

Example) <br />
/*your own path */NTU_DB/Daily_Actions/A022 <br />
/*your own path */NTU_DB/Mutual_Conditions/A050
...

The pairs of video clip and skeleton file corresponding to each action class should be in each subfolder.<br />

Example)<br />
In /*your own path */NTU_DB/Daily_Actions/A022, it contains..
S001C001P001R001A022_rgb.avi, S001C001P001R001A022.skeleton, ...

After data loading, the skeleton data information will be transformed to the python object which consisting of
3D location, 2D location of RGB/Depth/IR, orientation of each joint and etc. for every frame and every body.


## Drawing Skeleton

In each frame, the skeleton data corresponding to the performer's body is drawn with each joint and the lines connecting the joints.
This code only provides skeleton drawing for RGB, not for Depth or IR yet.


## Quick View  

You can quickly search the video and skeleton data at once by quick view function. 
While you are watching the video, press the button 'e' to move next video immediately, 
press the 'q' button to move previous video. 'ESC' button can make you close the program. 

<p align="center">
    <img width="824" height="458" src=img/control.png>
</p>


## Making Error Data

If you found the error data which the unmatched or missing skeleton in the process of checking videos,  
you can simply mark the current video and skeleton by pressing 'x' button. 
Once you finish the checking process by reaching the end of the class's file or 'ESC', 
then the name list of the marked data is generated and saved as a text file after deduplication.     