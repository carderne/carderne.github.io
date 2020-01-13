---
layout: single
title: "Making a Raspberry Pi Wake-Up Light"
date: "2019-11-25"
excerpt: "Winter is coming, and with it, short days. I decided to make a bright, pleasing sunrise wake-up light to help us get up in the morning."
tags:
- inside
---

We need help getting up in the morning. I was moments from buying a [Philips Wake-up Light](https://www.usa.philips.com/c-p/HF3500_60/-), but the cheap one doesn't seem bright enough, and the expensive ones are expensive. So I decided to build one instead! I probably ended up spending more, but the money went to fun and learning rather a plastic thing on the shelf (plus I now have a soldering iron and a breadboard and bits of plastic).

{% include image.html url="/assets/images/2019/wake-up-light.jpg" description="The nearly completed wake-up lighting giving off a warm glow." %}

The basic idea is to have a light that automatically turns on in the morning, and slowly gets brighter and whiter like a sunrise. So: some kind of RGB lights and a timing system. My first thought was to use an Arduino, but this would require buttons and some kind of screen for a UI, which sound difficult and more expensive. So instead I decided to get a [Raspberry Pi Zero W](https://www.raspberrypi.org/pi-zero-w/). Whereas an Arduino runs a single script over and over, a Raspberry Pi is basically just a small computer, which can run a full Linux OS. This means instead of directly handling WiFi connections or button presses, I can just install Flask and create a simple web page to control the lights from a phone.

Apart from a sunrise effect at the configured time every morning, I decided to add one simple button that triggers a sunset effect that slowly fades as we go to sleep. This setup makes sense to me, as the web page will only be used on the occasion that we want to change when we wake up (in theory), whereas the button will be used every night.

What follows is basically the notes I took (so that I wouldn't forget which pin went were) with some buffer so its legible.

## What's needed?
Basic computer knowledge on Linux, a soldering iron, a breadboard and bits of wire, and the following components:
- Raspberry Pi: any one that has WiFi built-in
- micro-SD card: above 8 GB or so (the OS and scripts go here)
- micro-USB power adapter: at least 2 A, preferably more
- RGB LED: I used something like [this](https://www.adafruit.com/product/2530)
- 3x MOSFETs: one for each colour channel, needed because you can't drive a high-power LED directly from a logic pin; I used [these](https://www.adafruit.com/product/2530)
- resistors: a couple of 100 Ω and 10 kΩ logic-level (1/4 W) resistors are needed to go with the MOSFETs; you'll also need some higher-power (2W or so) resistors for the LEDs, the value of which will depend on the LED voltage ([this](https://ledcalculator.net/) may be useful)
- button: any clicky momentary button
- heat-sink: a chunk of metal to help the LED dissipate heat

## Setting up the Raspberry Pi
Before playing with the electronics, we need to get the Pi working. Most of the following comes from [this](https://ivancarosati.com/raspbian-stretch-headless-setup-for-raspberry-pi/) very useful post. The first thing is to get an operating system onto the SD card. Start by downloading the [Raspbian Buster Lite image from here](https://www.raspberrypi.org/downloads/raspbian/). Then install and run [balenaEtcher](https://www.balena.io/etcher/) and point it at the zip file you just downloaded and the SD card you just inserted.

This done, there are some quick configuration options to change before you power up your Pi. With the SD card still in your laptop, open the `boot` mount. To enable SSH, you need to create an empty file called `ssh` (no extension) at the top level of the `boot` drive:

```shell
touch /path/to/boot/ssh
```

Then, since this device will live at home and connect to one network, we want to pre-configure it with the network details. Still at the top level of `boot`, create a filed called `wpa_supplicant.conf` with the following contents (being sure to edit the country, SSID and PSK):

```
country=ES
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid=...
    psk=...
    key_mgmt=WPA-PSK
}
```

Then you're ready to safely remove your SD card and insert it into the Pi!

## Basic configuration
Once you've powered on your Raspberry Pi, you may need to wait a long time (go make a cup of tea and come back when it's done, in my case) for it to be ready for action. Once it's ready, you should be able to SSH in:

```shell
ssh pi@raspberrypi.local
```

with the default password `raspberry`. If this doesn't work, start Googling and good luck. As soon as you're in, run `passwd` and create a new password.

Then we're going to use the configuration tool to set some basic options, so run

```shell
sudo raspi-config
```

at the Pi terminal. This should bring up a menu with a couple of options.

{% include image.html url="/assets/images/2019/raspi-config.png" description="raspi-config and its menu options" %}

We want to make the following changes:

- Localisation Options -> Change Locale -> select en_US.UTF-8 (hit space) and any others needed (e.g. what you use on the connecting machine) -> Ok
- Localisation Options -> Change Timezone -> Choose your timezone (important for a wake-up light!)
- Advanced Options -> Expand Filesystem
- Advanced Options -> Memory Split -> assign minimum possible to GPU (as we're running headless)
- Network Options -> Hostname -> I used `wake` (giving the URL `wake.local`) but use whatever makes you happy

A good idea is also to use a key rather than a password for connecting -- this is both more secure and faster. To do that, run the following  from your laptop (i.e. not SSH'd into the PI):

```shell
ssh-copy-id -i ~/.ssh/your-key.pub pi@wake.local`
```

and enter password when prompted. This assumes you already have a key to use; if you don't, run `ssh-keygen` and use the key created.

Lastly, I decided to disable the Pi's built-in LED so that I don't have it blinking in our bedroom at night. For the Pi Zero, add the following lines to `/boot/config.txt` and reboot:

```
# Disable the ACT LED on the Pi Zero.
dtparam=act_led_trigger=none
dtparam=act_led_activelow=on
```

## Creating the app!
With the boring stuff out of the way, we're ready to create our app and get it running over the network! First, let's install some needed packages. Normally, it's preferable to use virtual environments for managing Python packages, but we're doing it differently because we won't have anything else running on the device. Run the following to get the required packages:

```shell
sudo apt update
sudo apt upgrade
sudo apt install git
sudo apt install python3-setuptools
sudo apt install python3-flask python3-crontab python3-rpi.gpio
```

We use [PWM](https://en.wikipedia.org/wiki/Pulse-width_modulation) (pulse width modulation) to control the LED brightness; that is, instead of altering the current to each LED, we simply flicker it on and off fast enough (hopefully) that our eyes don't notice, and the proportion of on- versus off-time controls the brightness. I first used the standard `RPi` package to do this, but found that [pigpio](http://abyz.me.uk/rpi/pigpio/index.html) offers better performance and control for PWM with LEDs. Run these [official installation instructions](http://abyz.me.uk/rpi/pigpio/download.html) to get pigpio installed:

```shell
wget abyz.me.uk/rpi/pigpio/pigpio.tar
tar xf pigpio.tar
cd PIGPIO
make
sudo make install
```

Then run the `pigpio` daemon (which is connected to by scripts to make the PWM magic happen):

```shell
sudo pigpiod
```

I've shared my code for the app in a [GitHub repo called wake-up-light](https://github.com/carderne/wake-up-light). Feel free to browse the code or clone it:

```shell
git clone https://github.com/carderne/wake-up-light.git
```

In the meantime I'll quickly go over the main bits of code. First is `lights.py`, which controls the LED colour and brightness. First we need to import `pigpio` and set up the pins:

```python
import pigpio

pi = pigpio.pi()  # not super Pythonic!

# these are the pin numbers I chose
pins = {
    "red": 5,
    "green": 6,
    "blue": 13
}
for pin in pins.values():
    pi.set_PWM_frequency(pin, 400)
```

This imports `pigpio` and sets all the pins to use a PWM frequency of 400 Hz. (Too low and you'll notice flicker; too high and you might push the limits of your little CPU.) At this stage I got some cheap LEDs that I could drive straight from the pins (don't forget to use a resistor!) so I could make sure the code was doing what it was supposed to. Then, still in `lights.py`, we have some code to create the 'sunrise' effect:

```python
import time

for x in range(101):
    pi.set_PWM_dutycycle(pins["red"], 2.55 * (x))
    if x > 33:
        pi.set_PWM_dutycycle(pins["green"], 2.55 * (1.5*x - 50))
    if x > 66:
        pi.set_PWM_dutycycle(pins["blue"], 2.55 * (3*x - 200))
    time.sleep(0.05)  # pause 50 mS between steps
```

The `2.55 * ` is because `pigpio` by default has 255 steps of brightness, so we scale from the `0-100` range of the `for` loop. This is a super simple colour effect that starts at red, gets brighter and oranger, through yellow and to a bright white. Feel free to create any effect you want. This file also contains the code for the sunset effect, which is basically the reverse of the above, minus the blue. To test it, it's easiest if you add a shebang at the top of the script `#!/usr/bin/env python3` and run `sudo chmod +x lights.py` to make it executable. The you can run `sudo ./lights.py` to see if it works!

Note: if you're driving LEDs directly (i.e. without MOSFETs), and depending on how they're wired (common-anode or common-cathode), you may need to reverse all of the duty cycles; e.g. `2.55 * (1-x)`. Experiment and figure it out.

Next up is `button.py`, which simply listens for a button press and fires the sunset sequence when it detects one. For this I used the standard `RPi` Python library, as it doesn't require the more advanced `pigpio` PWM timing. As above, this is just enough to get going; the full code is in the repo.

```python
import RPi.GPIO as GPIO

def button_callback(channel):
    print("Button pushed")
    # call sunset function

pin = 26  # change to what you're using for the button
# use BCM board numbers - check the diagram below
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(pin, callback=button_callback)

input()  # pause until user input
```

You can test this out with a basic button and see if the callback works. Normally you'll wire it from `+3.3 V` through the button and a resistor, into a GPIO pin. Don't forget to shebang and chmod your script before running `sudo ./app.py`.

Finally, there is the little Flask app which serves a basic HTML page on our local network and updates the sunrise schedule. To makes things easy for myself, I'm just using [cron](https://en.wikipedia.org/wiki/Cron) for scheduling. The important bits of the Flask app `app.py` are as follows. Firstly, basic imports and instantiate the Flask app:

```python
from flask import Flask, render_template, request, jsonify
from crontab import CronTab

app = Flask(__name__)
```

Then a simple function to display an HTML file at the website index. You'll need to create `template/index.html` -- more on that below.

```python
@app.route("/")
def index():
    return render_template("index.html")
```

Then this function will allow some JavaScript running on the website to update the cron schedule. `time` contains the lights start time in 24h format (e.g. `07:15`).

```python
@app.route("/update", methods=["POST"])
def update():
    time = request.get_json().get("time")
    hour, minute = time.split(":")

    cron = CronTab(user="root")
    cron.remove_all(comment="wake")  # easier to remove all than update

    # add the full path to the script
    # the comment lets the remove command find it again
    job = cron.new(
        command=f"/home/pi/wake-up-light/lights.py",
        comment="wake",
    )
    job.dow.every(1)       # every day of the week
    job.hour.on(hour)      # only on the specified hour
    job.minute.on(minute)  # and only on the specified minute
    cron.write()

    return jsonify("Updated")
```

Finally, we add the standard Flask code to run the app at the bottom. 

```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
```

Be careful where you run this -- this setup is normally a bad idea! Running with `debug=True` can give potential attackers much more information, so disable it once everything is working. Using `host="0.0.0.0"` potentially means your server is open to the wide web -- make sure your router firewall is configured to block this from happening. And finally, running with `port=80` requires the app to be run with `sudo` privileges, which really completes the insecure soup. In this case `sudo` is needed anyway, as the cron schedule and lights scripts need to be run as sudo. This is all terrible practise, but for a simple light on a local network I feel it's a fine trade-off over the complications of doing it properly. Hopefully, the consequences of a hacked wake-up light aren't huge!

We need a quick bit of HTML and JavaScript for the web page. This just has an input form and a button to submit what is entered. In the full version, I've styled this nicely and used restricted drop-downs instead of a bare text box. I also made it so that your previous choice is displayed on the website so you aren't guessing what the current setting is! For now just place this in `templates/index.html`:

```html
<html>
<head>
    <title>Wake-up Light</title>
</head>
<body>
    <input name="time" type="text" maxlength="5" id="time">
    <button onclick="update()">Update</button>
    <script src="static/main.js"></script>
</body>
</html>
```

And create the following in `static/main.js` to provide the logic:

```javascript
async function update() {
  let time = document.getElementById("searchTxt").value;
  try {
    const response = await fetch("/update", {
      method: 'POST',
      body: JSON.stringify({
        time: time
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
  console.error('Error:', error);
  }
}
```

Now you can run the following:

```shell
sudo ./app.py
```

and hopefully it works! To test it, go to `http://wake.local/` on a device connected to the network and you should get a simple page with wake-up options. Try changing the values, then come back to your Pi to check them. You can type `sudo crontab -l` to get a list of scheduled cron jobs. You should see an entry with the time and duration you just selected on the website. In the full script I used, you can also configure which days it runs on, and how long it should run for.

And again, feel free to just clone my code from [the GitHub repo](https://github.com/carderne/wake-up-light) to save yourself some time.

## Make it all start up automatically
We don't want to have to SSH in re-start everything any time we unplug the device, so let's add them as services to systemd. Navigate to `/etc/systemd/system/` create `app.service`:

```
[Unit]
Description=Flask app
After=network.target

[Service]
ExecStart=/home/pi/wake-up-light/app.py
WorkingDirectory=/home/pi/wake-up-light/
Restart=on-failure
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Make another file called `button.service` with the same contents, but with the following changes:

```
Description=Button listener
After=pigpio.service
ExecStart=/home/pi/wake-up-light/button.py
```

And finally, `pigpio.service` with:

```
Description=Pigpio daemon
ExecStart=/usr/local/bin/pigpiod
```

Notice that we force `button.service` to only fire once the `pigpio` daemon is already running. Then run the following to enable these services:

```shell
sudo systemctl enable app button pigpio
```

Now restart the Pi (`sudo shutdown -r now`) and if all goes well, the app, the button listener and pigpio should all be running automatically!

## The fun part!
Now for the hardware, which is much more exciting! (I managed to break 6 of my 40 GPIO pins getting it going...) The pins on the 40 pin Pis are configured according to the image below. Important for this project are the `+5V` in red, `+3.3V` in yellow, `ground` in black, and `GPIO` pins in green. Note that these are the BCM numbers -- remember in `button.py` I set `RPi` to use BCM numbering.

{% include image.html url="/assets/images/2019/raspberry-pi-pinout.png" description="BCM numbering scheme for 40-pin Pis" %}

The easiest way to get everything going is to get a reasonably sized breadboard (mine is way too small), a big handful of different coloured male-male and male-female jumper wires and a decent variety of resistors. If you can get a low-current RGB LED working, it will be easier to then move to the higher current one, which needs to be driven by MOSFETs.

My circuit diagram is shown below, and you can click [here](https://crcit.net/c/6a70f01efec64144a5f891bd44966b72) to get an editable copy for yourself. The left side is the LED setup, and the simple bit on the right is for the button. The MOSFET's are the bits in the middle, with each one have Gate on the left (where they're 'controlled'), Source on top and Drain to earth on the bottom. Note that three LEDs are typically on physical object, but are electrically separate. Some LEDs are either common-anode (+ together) or common cathode (- together); mine was all separate but I wired the anodes (+ side) together, as that was how the low-current LED I played with was wired. If yours is common-cathode, you'll need to put it on the Drain rather than source side of the MOSFETs.

The 100 Ω and 10 kΩ resistors on the Gate side of the MOSFETs are something I read about<sup>[citation needed]</sup> and are to prevent high current from leaking into the GPIO pins, and to make sure the Gates properly close, respectively. Be careful that you have everything wired correctly, as pumping 300 mA+ (needed for bright LEDs) into your GPIO pins will quickly fry them (and potentially more).

{% include image.html url="/assets/images/2019/circuit.svg" description="Final circuit diagram (ignoring the fact that I had two of each LED)" %}

When I put this together, it came out looking like this. Does it look anything like the neat diagram above? Not exactly professional but it seems to work. By the way, I've got *two* RGB LEDs, because it didn't seem bright enough with just one (they're 3W each). So, for example, the bottom MOSFET drives both red LEDs, but they each get their own resistor (the big maroon ones). I swapped out for a bigger button once I'd checked that it all worked.

{% include image.html url="/assets/images/2019/circuit-prototype.jpg" description="And the not-as-pretty real-world result" %}

I then decided to ditch the breadboard and, as far as possible, solder everything together directly, to save space in the little cardboard box I found. This was super fiddly, so I think I'll probably get a little [prototype board](https://duckduckgo.com/?q=prototype+board&ia=images&iax=images) for my next project.

Check the sped-up video below to get a rough idea of what it looks like. Unfortunately neither my phone nor my camera skills are up to capturing it properly, but it actually looks pretty great in real life!

<video width="100%" height="500" controls>
    <source src="/assets/videos/wake-up-light.mp4" type="video/mp4">
    Your browser does not support the video tag.
    </source>
</video>
