Kevin Zhang, Kevin Guo, Cedric Kim, Daniel Daugherty

#Augmented Reality
#Preparation and Framing Document

#Background and Context

Our project is a method of viewing conceptual objects in a 3D space using virtual reality (VR). The program (on the computer) should be able to track a post-it of a given color and project a model over the post-it. Our final product would have multiple post-its, with multiple model projections. In the end, we would also be able to manipulate the models, and possibly have a networking aspect as well where collaborators could both view and manipulate the model in real time.

We are using Google Cardboard as our source of VR and obtaining our image from a webcam. Once we read images, we augment the image in python and then output it into Google Cardboard-viewable form. 

Currently, we have worked on tracking a post-it note using openCV (masking, and using hough lines) then projecting the lines. This way, we can grab the geometry of the post-it, in order to find its orientation, and position.

On the other end, we have also worked on getting the VR experience to work. Rather than programming an app, we have decided to create our own Google Cardboard viewing algorithm and then use third party software to link our PC screen to our phones over WiFi. Using openCV, we were able to take an image and convert it to the Google Cardboard format, thus allowing us to transform any screen to a VR experience.

From now, we plan on creating our MVP (projection of a cube on a post-it). In order to move on, we need to implement different objects, using CAD files.

#Key Questions
 - Does anyone know anything about a better method to link a PC’s camera to a phone? Current method is laggy and drains a lot of battery
 - We were thinking about potentially giving our VR a better of perception of depth, and an idea we’re thinking of using two cameras with an adjusted algorithm. Anyone have an idea of how to do this or a better idea on how to give depth?
 - Are there any suggestions you would like to offer about the image?
  1. How is the offset between the eyes?
  2. Does the picture seem centered with respect to the camera?
  3. Anyone know anything about Stereoscopy?
 - Do you know a way to track the post-it in different lighting conditions?
 - Do you know how to efficiently track the corners of the rectangle?
 - Have you worked with Houghlines, specifically solving the multiple line problem?
 - Which type of CAD file is the easiest to analyze and project using OpenGL?
 - How do you create a dynamically-viewed cube using OpenGL?

#Agenda for Technical Review Session

 - 1 minute - Talk about what we hope to get out of it, general structure 

We hope to get suggestions from you guys about better methods for several components of our project, and perhaps some additional help on how to proceed forward.
 - 2 minutes - Overview of project / presentation

Talk about general background, as in what the project is and what we’re doing, how we’ve been doing it

 - 10 minutes - Demo of sticky note tracking and overview of code

Feedback,  questions, discussion on lighting, CAD files and OpenGL 

 - 10 minutes - Demo of google cardboard viewer and overview of 

Feedback, questions, discussion on better methods and how to proceed with OpenGL cube, depth perception, Google Cardboard picture quality

 - 2 minutes - Closing comments
