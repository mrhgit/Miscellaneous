# Miscellaneous
Various topics of interest... to me, at least!

## Turn Your Raspberry Pi into an [IR/Infrared Remote Control](./RaspberryPi_InfraredRemoteControl/)
**UPDATE**: For lower cost, I've also implemented this on the Raspberry Pi Pico W using uasyncio.  See bottom of post for details.

I had run into issues with infrared remote control routines available on the internet for the Raspberry Pi.  The main issues:  being forced to use some specialized hardware that cost as much as a Raspberry Pi or getting interrupted by the Linux kernel all the time when controlling pins myself!  Check out the [details](./RaspberryPi_InfraredRemoteControl) for how I overcame those issues.

## Adding a [Variable-Volume Line Out](./Adding_Variable_Volume_LineOut_to_TV/) to my Sony Bravia TV
My Sony Bravia HDTV has built-in speakers and a fixed-level line out.  I had a Logitech Z323 2-way + subwoofer speaker system with a volume knob.  This is how I merged the two and kept my remote volume control!

## [Calculating](./Calculating_Resistor_Mass_XKCD_730/) (instead of PSPICE'ing) the value of the Resistor Mass in [XKCD #730](https://xkcd.com/730/)
I couldn't find anyone who had simply calculated the value of the resistor mass, vs [finding it via simulation in PSPICE](https://www.reddit.com/r/xkcd/comments/7wchnq/value_of_resistor_network_in_730/), so I thought I'd go ahead and [do that](./Calculating_Resistor_Mass_XKCD_730/).  Hint:  there are 27 unknowns.

## [Trimming Silence](./Trimming_Silence_In_Audio_Files) in Audio Files
FFMPEG's silenceremove functionality is a bit cryptic and unwieldy.  This substitute was done as a quick project just to see how simply I could code it using Python, while still maintaining performance.  It ended up being able to process 2 hours of audio in 5.7 seconds on my midrange, 2020 machine!  Not bad for Python!  I also put in a lot of nice features like auto-thresholding and blip ignoring.

## Making [Movies from tinySA Captures](./tinySA_Ultra_Movie_Capture)
The [tinySA](https://www.tinysa.org/wiki/) is a small spectrum analyzer that lets you send commands over [serial/USB](https://tinysa.org/wiki/pmwiki.php?n=Main.USBInterface), one of which is to retrieve a 'capture' (screenshot).  This script uses [moviepy](https://zulko.github.io/moviepy/index.html) to periodically capture images and combine those images into movies every frame-count frames.  This is useful when using the spectrum analyzer to monitor activity over a long period of time.  The max-hold functionality can be activated and reset at the beginning of every movie.
