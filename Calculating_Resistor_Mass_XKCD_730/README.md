# Calculating the Resistor Mass featured in XKCD #730 #

Would I call it [nerd-sniping](https://xkcd.com/356/) that I couldn't resist solving this?  I have to say maybe, because to be honest, it wasn't that bad so maybe I had time to dodge the truck.

## The Problem

As you can see in the [original post](https://xkcd.com/730/), there is a resistor mass off to the center-right of the image with a nice challenge "Oh, so you think you're such a whiz at EE 201?"  As an additional incentive, the alt-text of the image states, "I just caught myself idly trying to work out what that resistor mass would actually be, and realized I had self-nerd-sniped."

Needless to say, I had to reduce that resistor mass to a single equivalent value.  Of course, I wanted to see if someone had beaten me to the punch and they problem have, but perhaps they haven't posted it or I wasn't able to find their post.  Therefore, I decided to solve it myself and post my approach to the problem.  BTW, I was able to find [PSPICE simulations](https://www.reddit.com/r/xkcd/comments/7wchnq/value_of_resistor_network_in_730/), but being a "whiz at EE 201" doesn't mean just plugging stuff into PSPICE.

## The Solution

The very first thing is to look for "freebies" in the diagram, such as resistors in series or parallel, but alas, there were none that I could spot!  [Randall](https://xkcd.com/about/) knows what he's doing.

The next thing to do is to start labeling - labeling nodes and currents are all that's required.
