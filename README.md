# arcade-asteroids
Python arcade library asteroids clone

![Screenshot](https://i.imgur.com/MlZTOFx.png "Screenshot")

# About
Shooting an asteroid will make its number of sides decrease to the next smallest prime, stopping at 3, where it will stay at 3. Asteroids will bounce, except if their radius is less than 9 pixels, in which case they will fly off the screen and despawn. Your ship's position will wrap (pos % screen dimensions). 

# Controls
WSAD or arrow keys (choose at startup) to move  and space to shoot. You move automatically, but W/Up will speed up your ship and turning. 

# Requirements
Requires Python 3.6, Arcade library, and AVBin. 

# Credits
To see credits for sounds, look in the comments in the main python file. 
