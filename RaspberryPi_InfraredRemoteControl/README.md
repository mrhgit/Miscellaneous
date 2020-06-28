## Using the Raspberry Pi as a Remote Controller

So the basic plan is send out IR signals from a Raspberry Pi to control a device that I normally control with a common handheld remote control.  At my disposal, I had a RaspPi 3, a Rasp Pi Wireless, and a Rasp Pi 4 all just lying around begging to be used.  If it weren't the case that I had a Raspberry Pi, I'd probably have gone with the [ESP8266](https://www.sparkfun.com/products/13678), but that's a project for another time, because frankly, I like the hyper-convenience of using a Raspberry Pi.

This method is for people who don't have a [USB IR Toy v2](http://dangerousprototypes.com/docs/USB_IR_Toy_v2) to use with [LIRC](https://www.lirc.org/) because they would rather just use the extra IR LED that's laying around (or can be picked up for about 3/$1 or cheaper in bulk).  I had something arguably inbetween those two, but in truth far closer to raw IR LED:  a combo IR TX/RX module that came with my [kit](https://jetpackacademy.com/shop/digital-electronics-kit/) that's meant to accompany Ian Juby's [Digital Electronics for Robotics](https://jetpackacademy.com/shop/digital-electronics-kit/) course on [Udemy](http://www.udemy.com) (I can't recommend Ian highly enough).

To use this approach, you need to figure out what remote control code waveform you'd like to mimic.  There are easy searchable databases out there for remote controller codes and there are devices such as the USB IR Toy that can help you grab some IR signals, but I preferred a more straightforward and fool-proof way:  looking at the transmitted waveform on an oscilloscope.  To do this, I simply hooked up an IR LED directly to my oscilloscope, set the vertical to 500mV/div and set the horizontal to 5ms/div.



I had run into issues with infrared remote control routines available on the internet for the raspberry pi.  The main issue:  getting interrupted by the Linux kernel all the time!  Check out the [details](./RaspberryPi_InfraredRemoteControl) for how I did it.
