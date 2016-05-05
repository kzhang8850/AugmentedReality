#Kevin Zhang, Daniel Daugherty, Cedric Kim, Kevin Guo

#Augmented Reality

#Reflection and Synthesis

##Feedback and decisions
    
For post-it note tracking, we received various kinds of feedback. We learned different ways to track the post-it. We could track shapes on the corners, rather than getting the contours of the shape in order to find the object’s geometry. We also need to track the orientation of the post-it, via a different colored corner, or some other type of orientation tracking. In order to move forward, we plan on incorporating these different types of ways to track the post-it note, then attempting to optimize and choosing the best tracking type.

We also learned that OpenGL could import STLs. Using this information, we could analyze the binary geometric structure of the STL in order to reconstruct it in 3D space. The STLs should give arrays of numpy points which we could use to create the model. This means we would have to understand how to generate a 3D model with OpenGL given a set of points in 3D space and how to create planar surfaces from those points. In addition, we will still have to analyze how to change our view of these points depending on the viewing perspective.

For the virtual reality experience, we received numerous suggestions on how we could improve our code and the way we display onto the phone.  We looked into the suggested methods to get the computer screen display on the phone that would have less latency than the VNC viewer.  We feel that GStreamer is too complex of a method to try to tackle. We believe that the IOS app Duet Display is our best option.  The app connects via USB cable to the computer which means that there will be no latency for the viewer.

Some of the things we are still curious about are how to incorporate the stereoscopy effect using two cameras. We need to calculate the correct angles to orient the cameras to achieve a 3D effect.  We were also wondering about other alternatives to OpenGL, just as a point to having options to work with, since Sam said his experience with OpenGL and Pyglet was tedious and poor. Finally, given what was spoken on the tracing discussion, we were wondering what the optimal method is, given that there were so many ideas thrown around. We might hold some of these until the next technical review, but we still also do research and testing to see if we can come up with the answer ourselves.

##Review process reflection

We believe that the review was productive and helpful. We got varied answers to our key questions, but overall we received information that we can use to progress forward. We received good feedback on the contour lines and tracing from Max and Rocco, which we can use to further test and refine the tracing. We also received solid advice on alternatives for laptop-to-phone projections, as well as a good start on code structure and architecture from Paul. We did however find no answers to Stereoscopy and the quality of the image, mainly because either the audience couldn’t answer it or they just couldn’t tell.

We believe that our context was straightforward and well explained. We gave an overview of the project, an explanation on the core of the project, and then stretch goals to give them an idea of what we’re doing. We then talked about what we’ve been working on and even showed them demos. 

We feel like we were able to closely follow our agenda. Our timeline was pretty well thought out, and we moved through it quite punctually. There was a little bit of subjective marginal error on the discussion sections, so we went over time by about a minute or two and weren’t able to ask the final question about code architecture and how to structure code. However, the resource that Paul gave us included some instructions and advice on structuring code involving AR, so we basically got an answer to a question that we didn’t have time to ask. In the end, our agenda was fulfilled, in one form or another.

To improve the quality of the next technical review, we could increase interaction between us and the audience by asking more about ideation for design questions and looking at a more conceptual perspective. We found that this technical review kind of just focused on a few  interactions between certain people (mainly Max and Paul). We feel like this may have happened because people did not have the knowledge we were looking for on some questions, so some questions were asked without any point. We could ask more abstract and design-based questions so that everyone can participate with their knowledge or suggestions.  Another thing was the lack of enthusiasm from the audience, maybe due to listening and sitting for too long reducing attention spans, so we might add some flare to our next review to keep the audience interested and engaged.
