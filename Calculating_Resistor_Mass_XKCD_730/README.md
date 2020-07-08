# Calculating the Resistor Mass featured in XKCD #730 #

Would I call it [nerd-sniping](https://xkcd.com/356/) that I couldn't resist solving this?  I have to say maybe, because to be honest, it wasn't that bad so maybe I had time to dodge the truck.

## The Problem

### Given
As you can see in the [original post](https://xkcd.com/730/), there is a resistor mass off to the center-right of the image with a nice challenge "Oh, so you think you're such a whiz at EE 201?"  As an additional incentive, the alt-text of the image states, "I just caught myself idly trying to work out what that resistor mass would actually be, and realized I had self-nerd-sniped."

### Find
Needless to say, I had to reduce that resistor mass to a single equivalent value.  Of course, I wanted to see if someone had beaten me to the punch and they problem have, but perhaps they haven't posted it or I wasn't able to find their post.  Therefore, I decided to solve it myself and post my approach to the problem.  BTW, I was able to find [PSPICE simulations](https://www.reddit.com/r/xkcd/comments/7wchnq/value_of_resistor_network_in_730/), but being a "whiz at EE 201" doesn't mean just plugging stuff into PSPICE.

## The Solution

### Reduce
The very first thing is to look for "freebies" in the diagram, such as resistors in series or parallel, but alas, there were none that I could spot!  [Randall](https://xkcd.com/about/) knows what he's doing.

### Label
The next thing to do is to start labeling - labeling nodes (red) and currents (blue) are all that's required.
<img src="./resistor_mass_labeled.png" alt="Labeled Resistor Mass" width="600"/>

### Extract Equations

Two formulas can be used to start writing down equations:  [Ohm's Law](https://en.wikipedia.org/wiki/Ohm%27s_law) and [Kirchhoff's Current Law](https://en.wikipedia.org/wiki/Kirchhoff%27s_circuit_laws#Kirchhoff's_current_law).

Ohm's Law states that the voltage across a resistor (V) = current through the resistor (I) multiplied by the resistance (R).  **V=IR**
Kirchhoff's Current Law states that the sum of current going into a node equals zero.  This is why there are arrows drawn for current - because directionality matters in these equations.

So given these two laws of electrical engineering, we can come up with a plethora of equations.

For each node (except nodes A and Z), there is Kirchhoff's Law:
A:  i = i1 + i2 + i3 + i4 = i18 + i25 + i26
B:  i1 = i5 + i6 + i7
C:  i2 + i7 + i9 + i16 = i17 + i18 + i19 + i20
D:  i3 + i11 = i8 + i9 + i10
E:  i4 = i11 + i12
F:  i5 = i13 + i14
G:  i8 + i14 = i21
H:  i13 + i21 = i24
I:  i6 = i15 + i16
J:  i20 + i22 = i27
K:  i10 + i12 = i22 + i23
L:  i15 + i17 + i24 = i25
M:  i19 + i23 + i27 = i26
Z:  i = i18 + i25 + i26

Really, we need to combine the equations at nodes A and Z, because we only want to focus on what's between nodes A and Z:
A/Z:  i1 + i2 + i3 + i4 = i18 + i25 + i26

