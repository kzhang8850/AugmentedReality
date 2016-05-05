# #GetReal

##Viewing CAD models in real life without having to fabricate

The Repository for the Final Project done in Software Design, Spring 2016. 

#####Authors: Kevin Zhang, Cedric Kim, Daniel Daugherty, and Kevin Guo


##What is #GetReal?

Creators and Developers often like to tinker and make things. For more software-oriented people, testing out a new idea is as easy as the push of a keyboard button. But for hardware and mechanical-oriented enthusiasts, experimentation is time consuming and difficult, requiring either a drawn out repetitive fabrication of a singular object or a pain-staking scrutinization on ensuring perfection on a first-pass construction. 

Using the power of augmented reality, #GetReal levels the playing field. Now you can load up an stl file of a CAD, put on some Virtual Reality Goggles, and see what your CAD would look like in 3D space, all before you even had to touch a single piece of material. Users can have access to the same kind of quick testing that software engineers do, simply making some tweaks in the CAD, re-uploading, and seeing the changes in the real world. #GetReal allows for rapid prototyping and efficient iterations, streamlining the process of development for aspiring mechanical and electrical engineers.

##Getting Started

Using #GetReal requires some extra hardware in addition to software dependencies in order to run the code. For external hardware, you will need: 

 - Google Cardboard (or some other VR headset)
 - High Performance Webcam
 - A smartphone (ios or android)
 - Splashtop Streamer (from app store)
 - Four blue post-it notes in a square, with one blue post-it colored black in the center.
 
Once you have all your hardware, you will also need to download Python and the following python packages:
 
 - Pip `$sudo install pip`
 - OpenCV `$sudo pip install opencv`
 - OpenGL (download from website http://pyopengl.sourceforge.net/documentation/installation.html)
 - sudo `$pip install numpy-stl`
 - Numpy `$pip install numpy`
 - other stuff TBD

##Usage

After you have your environment configured, take the CAD file you want to view and save it as a binary .stl. Copy it into the folder that contains our Github repository. Once you have everything set up, first, set up the computer to phone connection. Run Splashtop on your computer and phone, and pair them together. Once you see your computer screen on your phone, run GetReal.py, and insert the name of the .stl. You are all ready to view the CAD model! From your Google Cardboard, you should see your CAD model augmented into 3D space where your post it notes are. Try walking around it and viewing it from different angles. You should see the CAD model in its entirety, as if it was right in front of you. Have fun prototyping!


##Acknowledgements

The team would like to thank Software Design Teachers Paul Ruvolo, Ben Hill, and Oliver Steele for their guidance and expertise. We would also like to thank the NINJAs Sophia Li, Patrick Huston, Rocco Diverdi, and Lucy Wilcox for their assistance in bugs and roadblocks along the way. Finally, a big thanks from the team to its individuals for sticking it out and accomplishing such an ambitious project in a 6 week time frame.

##License

MIT License

Copyright (c) 2016 #GetReal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.