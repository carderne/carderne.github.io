---
layout: single
title: "iCloud calendars in Evolution Mail"
date: "2020-04-20"
excerpt: "Bit of a horror, but it works."
---

[Main source for this.](https://ar.al/2018/08/05/using-icloud-calendars-on-gnu-linux/)

## A. Install the required software.
Install the following apps if you don’t already have them:

Install [Evolution](https://wiki.gnome.org/Apps/Evolution/) and [Gnome Calendar](https://wiki.gnome.org/Apps/Calendar):
```
sudo apt install evolution gnome-contacts
```

We will be using Evolution to set up the iCloud accounts but you will most likely want to use Gnome Calendar as your daily calendar as it offers a minimal, beautiful experience.

## B. Set up an app-specific password on iCloud.
1. Sign into your Apple account at [https://appleid.apple.com/](https://appleid.apple.com/)
2. Scroll down to the _App-Specific Passwords_ area in the _Security_ section and select the _Generate Password…_ link.
3. In the resulting pop-over, enter a descriptive name for this password.
4. Copy the password onto the clipboard.

## C. Set up your calendar(s) in Evolution.
1. Select the _Calendar_ section in the main navigation.
2. Open the drop-down menu next to the _New_ button and select _Calendar_[3](#fn:3).
3. In the resulting _New Calendar_ window, select _CalDAV_ from the _Type_ drop-down.
4. In the _URL_ field, enter _[https://caldav.icloud.com](https://caldav.icloud.com/)_
5. In the _User_ field, enter your Apple ID
6. Press the _Find Calendars_ button.
7. In the resulting password entry pop-up, paste the app-specific password you copied onto the clipboard in the last section.
8. In the resulting _Choose a Calendar_ window, select the calendar you want to set up[4](#fn:4).
9. Back in the _New Calendar_ window, choose a colour to match the one you use on iCloud.
10. Set your options: I select _Copy calendar contents locally for offline operation_, as I want to be able to access the calendar even if I don’t have an Internet connection, and _Server handles meeting invitations_.[5](#fn:5)
11. If you want this to be your default calendar, also check _Mark as default calendar_.
12. Set the _Refresh every_ setting[6](#fn:6) to decide how frequently your calendars should synchronise.
13. Press the _OK_ button to create the calendar when you’re happy with your choices.

## This _should_ be easier…
That’s it! If all goes well, you should see your calendar entries begin to pop up in Evolution. If you want to set up additional calendars, rinse and repeat the instructions in this section. Once you’ve set up your accounts, fire up Gnome Calendar and enjoy your synchronised calendars in a beautifully minimal interface. Any entries you make in Gnome Calendar will sync to iCloud and, from there, to all of your Apple toys, and vice-versa.
