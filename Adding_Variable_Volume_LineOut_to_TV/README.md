# Adding Variable Volume Line Out to TV

## The Problem
I had a SONY Bravia HDTV (KDL46EX500) that allowed you to switch the audio output between the built-in speakers and a fixed-level RCA-style line out and an optical out (no headset output on this one).  The fixed-level line out and optical line out are options meant for A/V Receiver-based setups, which are controlled by their own remote control.  The idea is the audio gets sent at the proper, known level and amplified later with the volume controlled by a separate system presumably with its own remote control.  *But* I had a set of computer speakers - the Logitech Z323 2-way + subwoofer speaker system - that only had RCA inputs and a 3mm headphone jack input and only a volume control knob.

## Door #1 - Trying to hack firmware
The first thing to consider, obviously, is if there was a new firwmare available for the TV that would offer this option.  Unfortunately, there was not.  Despite this being the case, it's technically still somewhat possible to download a copy of the latest firmware and modify it to do my bidding (NOT what I ended up doing).  This would require reading through the possibly-zipped/packaged assembly code meant to be installed on the destination hardware.  Ok, let's see what other options we have...

## Door #2 - Hacking into the Sony TV's OS
It turns out that Sony Bravia TV's run Linux.  I found very much information at https://hackaday.com/2012/06/20/getting-root-on-a-sony-tv/ including a walkthrough of using a buffer overflow hack to log in as root (really it's available at https://github.com/CFSworks/nimue) , which is then used to open a port for remote telnet access.  Sadly, this approach didn't work with my model - possibly because I had updated the firmware after 2012 in order to get rid of an annoying startup sound that couldn't be turned off by any option!  This truly would have been awesome and I believe was my way "in" to really get at those menus and the commands they run.

## Door #3 - Borrowing the Signal from the Speakers

