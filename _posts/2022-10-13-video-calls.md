---
layout: single
title: "My quest for a reasonable video call setup"
date: "2022-10-13"
excerpt: "Much harder than it should be..."
---

This post mostly inspired by [a similar one by Be Kuhn](https://www.benkuhn.net/vc/). It adds a bit, ignores a bit and is generally much less thorough. My main advice would be to read his post, and come back here if you're still bored.

My goals are as follows:
1. Look decent.
2. Sound better.
3. Zero [faff](https://www.google.com/search?hl=en&q=define%20faff).
4. High confidence in the on/off-ness of my inputs and outputs.
5. My job is mostly _not_ calls, so I will only sacrifice a certain amount of tidiness in this pursuit.

## Working space
Ideally we'd all work in sound-proof chambers, but I currently don't, I somewhat enjoy being around other people, and I'd like a solution that is somewhat flexible on this point.

## Network
No Bluetooth! Too much faffing with connections, too much audio lag and stuff going on. WiFi is more of a mixed bag, and, as the proud owner of a [FRITZ!Box](https://en.avm.de/products/fritzbox/), mine isn't too bad. Pinging the router from my desktop consistently shows a round-trip time of below 4ms, so that's fine. I'd prefer a fully wired connection, but the BT/OpenReach broadband box is at the opposite end of the house.

## Current setup
One of the reasons I bought a desktop computer was to remove the built-in microphone and webcam. They're generally garbage (Apple might finally have changed that, but I don't use macOS) and they're just two more devices for your VC software to accidentally use.
Where I've ended up is as follows:
- **Video out**: A nice big ultra-wide Philips monitor.
- **Audio out**: Logitech 2.0 speakers plugged into the audio-out jack of my motherboard. Useful for occasionally watching stuff on the ultra-wide monitor, and listening to music when I'm alone. Also they give me a big tactile volume knob that clicks off, so I know.
- **Audio out**: A pair of basic Apple EarPods (3.mm wired) plugging into the speakers. These are the only things that I find comfortable enough to wear for many hours, and don't interfere with my glasses.
- **Audio in**: A [USB lapel microphone](https://fifinemicrophone.com/products/lavalier-microphone-for-pc-recording-k053) with a modified lapel thing to make it super easy to take on and off. This _doesn't_ have a hardware off button, so I had to resort to software (see below).
- **Video in**: A Logitech C922 with a little slider so I know it can't see me. It annoyingly also has a built-in microphone (which is too echo-ey to be useful), so that also needs software to turn off. The video quality isn't amazing, but it works, is always there, and is neatly placed on top of the monitor.

That is the full list of things connected to my computer that can interact visually and sonically (?) with the physical world. (Actually I lie: the monitor also has speakers (permanently muted) and sometimes offers itself to my OS as a juicy audio sink.) It's not perfect, but it has the right balance of trade-offs for me. I look fine, I sound pretty good, I always know at a glance exactly what the status of my webcam/mic/speakers/earphones is, and I never have to mess around changing devices because there aren't many and they're all locked down.

Before I go into the software, a quick digression into some of the other things I've tried.

## Other things I tried
This is where I did a bunch of experiments, and was mostly amazed at how hard this still is to get a decent setup at a decent price. No wonder everyone sounds and looks terrible, and is always plugging stuff in and out!

1. iPad Air: for a while I toyed with using this for calls (also as a way of getting away from the desk and saving my [wrist](./wrist)) but I can't share my screen and just isn't a reasonable solution.
2. I was briefly the custodian of a [Yeti](https://www.bluemic.com/en-gb/products/yeti/) microphone, a big heavy metal thing with satisfying buttons. I loved the audio quality, I love being able to turn off both the microphone and earphones output with physical knobs. But it was too much desk real estate, and too in the way of my actual work.
3. [Rode Lavalier Go](https://rode.com/en/microphones/lavalier-wearable/lavalier-go), which also had great audio quality. It needed a [discrete ADC](https://focusrite.com/en/usb-audio-interface/scarlett/scarlett-2i2) and was fussy about playing nicely with my motherboard's mic jack (voltage stuff that I've thankfully forgotten) so that was more real estate given up. I mostly investigated this in the context of using [Talon](https://talonvoice.com/) for voice control.
4. Using my iPhone as a webcam. Incredible quality, too much effort getting it into position and making sure the feed is coming through.
5. [Jabra Evolve2 40](https://www.jabra.co.uk/business/office-headsets/jabra-evolve/jabra-evolve2-40##24089-889-899) wired headset. Uncomfortable, mediocre microphone, weird audio feedback (maybe only on Linux). Not great.
6. [Philips SHP9500](https://www.usa.philips.com/c-p/SHP9500_00/hifi-stereo-headphones) open back headphones (this is what Ben recommends). By far the most comfortable headphones I've ever tried, and really wonderful sound quality for how cheap they are. Not as comfortable for me, and still a big _thing_ that I need to have lying on my desk ready to jam onto my head at a moment's notice.
7. [V-Moda BoomPro](https://www.v-moda.com/us/en/products/boompro-microphone) microphone (also what Ben recommends) that pairs wonderfully with the headset, and results in only a single cable. It's an omni-directional mic, so picks up sound from all over the show, but the quality is really great. Has an inline switch on the cable to turn the mic on/off and headphone volume control. Just about perfect, but for me it didn't quite outweigh the need to have a big headset on my head for calls.
8. [V-Moda BoomPro X](https://www.v-moda.com/eu/en/products/boom-pro-x) is a cardioid (directional) version of the above, but the audio quality was garbage. I also tried it with a [Creative Sound Blaster Play!3](https://uk.creative.com/p/sound-cards/sound-blaster-play-3), which improved things a little.
9. Bonus: Bose QC45. I have these for cutting out noise and focusing, but they're not comfortable enough (especially with glasses) to wear for very long, and they are bluetooth and the microphone is crap and you can't hear yourself and I hated it.

NB: In case you think I'm some kind of hoarder/Prime-aholic, all of these were second hand (or refurbished) and all were sold on (or returned).

## Software
The solution I settled on has no hardware switch for the C922 microphone or the lapel microphone that I actually use, and (with the monitor) there is more than one audio output.

So I wrote a little script that uses PulseAudio (will I have to rewrite this when I switch to [PipeWire](https://pipewire.org/)?) to enforce the setup that I want.
The first thing to do is get the "cards" and their available profiles:
```bash
pactl list cards
```

From there you can see the available cards, what their "name" is (as far as PulseAudio is concerned, eg my microphone is called `alsa_card.usb-0c76_USB_PnP_Audio_Device-00`), what their Active Profile is, and what other profiles they have available.
After playing around a bit, my script looks something like this:
```bash
pacmd set-card-profile $MONITOR        off
pacmd set-card-profile $C922           off
pacmd set-card-profile $AUDIO_JACK     output:analog-stereo
pacmd set-card-profile $USB_MIC        input:mono-fallback
```

I mapped `Super-Shift-A` to run that script, so I can mash that from time to time and be confident that all is as it should be. But it still doesn't mute or unmute the microphone, which needs another step (thanks to [this blog](https://shallowsky.com/linux/pulseaudio-command-line.html) for some example snippets).
First find out what PulseAudio calls the microphone "source":
```bash
pactl info | grep "Default Source"
```

Which gives me `alsa_input.usb-0c76_USB_PnP_Audio_Device-00.mono-fallback`: just a liiitle different from the card name up above.
Then I added the following line to my script, and every time I hit the shortcut, the world is set right, and the mic's mute status is toggled.
```bash
pactl set-source-mute $USB_MIC_SOURCE toggle
```

And then! Because I'm using [i3](https://i3wm.org/) and i3blocks (well, actually [Regolith](https://regolith-desktop.com/) and i3xrocks), I can easily get this status into my task bar thing. This is how it works:
```bash
# get the active profile; I also do this for the audio jack, usb mic etc
PATTERN='s/.*: \(.*\)/\1/p'
LIST=$(pactl list cards)
P_C922=$(echo "$LIST" | grep -A50 "$C922" | grep -m1 Active \
    | sed -n "$PATTERN" | cut -c1-3)

# get the current muted-ness of the microphone
MUTED=$(pactl get-source-mute "$USB_MIC_SOURCE" | sed -n "$PATTERN")

# basically asserting that the devices are in the state that I want them to be
[[ $P_C922 = off ]]  && CAM=""        || CAM="WARNING cam: $CAMS"
[[ $MUTED = yes ]]   && MUTED="MUTE"  || MUTED="LIVE"

# print all the stuff, which should just be either "MUTED" or "LIVE"
echo $ACTIVE_C922 $MUTED
```

And now I have this flashing at me in my system tray whenever I mute or unmute the mic (and generally being loud <span style="color:red">RED</span> when the mic is hot).

<img src="/assets/videos/mic.gif" alt="mic status changing" style="width:51px;height:25px;">
