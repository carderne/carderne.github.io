---
layout: single
title: "Get hibernate working with LUKS"
date: "2021-03-21"
excerpt: "Workarounds abounds"
---

As with many of my blog posts, sharing this to get it out of my notes, and on the off-chance that it proves useful to future-me or anyone else.

Hibernate doesn't work on Ubuntu by default with a LUKS-encrypted drive, and it takes some work to get it going...
This is mostly because LVM introduces several layers of obfuscation between the physical drive and partitions (that I've been playing with since I was 14) and the mounted decrypted volume.

## Install Ubuntu
1. Make sure BIOS is set to UEFI (so install will default to GPT not MBR).
2. Don't enable SecureBoot, it breaks hibernate.
3. Install with default Ubuntu settings, encryption enabled.

## Resize swap partition
We want a bigger swap partition, so that hibernate can work, and because I have a big hard drive and swap is great.

Source: [Resizing LVM-on-LUKS](https://wiki.archlinux.org/index.php/Resizing_LVM-on-LUKS)

Ubuntu by default installs with the partition structure below. We want to make `vgubuntu-root` smaller so that we can make `vgubuntu-swap_1` bigger. So we don't need to resize the crypt, the LUKS volume or the physical partition!
```bash
NAME                  MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINT
nvme0n1               259:0    0 931.5G  0 disk
├─nvme0n1p1           259:1    0   512M  0 part  /boot/efi
├─nvme0n1p2           259:2    0   732M  0 part  /boot
└─nvme0n1p3           259:3    0 930.3G  0 part
  └─nvme0n1p3_crypt   253:0    0 930.3G  0 crypt
    ├─vgubuntu-root   253:1    0 909.3G  0 lvm   /
    └─vgubuntu-swap_1 253:2    0    21G  0 lvm   [SWAP]
```

Boot from Ubuntu live media. Open a root terminal session:
```bash
sudo su -
```

Decrypt the LUKS volume:
```bash
cryptsetup luksOpen /dev/nvme0n1p3 nvme0n1p3_crypt
```

Resize the `root` and `swap` volumes:
```bash
lvresize -L -20G --resizefs /dev/vgubuntu/root
lvresize -l +20G --resizefs /dev/vgubuntu/swap_1
```

Check that all went well
```bash
e2fsck -f /dev/vgubuntu/root
```

## Enable deep sleep
Source: [Enable deep sleep](https://askubuntu.com/questions/1029474/ubuntu-18-04-dell-xps13-9370-no-longer-suspends-on-lid-close)

Suspend, then wake and type: `journalctl | grep "PM: suspend" | tail -2`. If it returns `suspend entry (s2idle)` then need to change to type. `cat /sys/power/mem_sleep` will return `[s2idle] deep`.

Temporary fix: `sudo echo deep > /sys/power/mem_sleep`. And `cat` should return `s2idle [deep]`. Then suspend, then wake, check journalctl again and it should say `suspend entry (dep)`.

Then edit bootloader config at `/etc/default/grub` with the default sleep parameter:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash mem_sleep_default=deep"
```

Then rebuild grub config: `sudo update-grub`.

## Enable hibernate
Source: [Enable hibernate](https://gist.github.com/tjvr/f82004565139a5b13031af1ce5a50a02)

Check the path to the swap partition: `cat /etc/fstab | grep swap`:
```bash
dev/mapper/vgubuntu-swap_1 none            swap    sw              0       0
```

Edit `/etc/initramfs-tools/conf.d/resume`:
```bash
RESUME=/dev/mapper/vgubuntu-swap_1
```

Edit `/etc/default/grub`:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash resume=/dev/mapper/vgubuntu-swap_1"
```

Then update configs:
```bash
sudo update-initramfs -u -k all
sudo update-grub
```

## Use keyfile for LUKS
Source: [Use a keyfile](https://www.howtoforge.com/automatically-unlock-luks-encrypted-drives-with-a-keyfile) (this source just a reference, some stuff wrong).

Note: this process makes the encryption close to useless for an even slightly switched-on attacker (including anyone who's read this).

Can consider using `—keyfile-offset` in `cryptsetup` and in `/etc/crypttab` for some security through obscurity (not implemented below). Sources: [cryptsetup ref](https://wiki.archlinux.org/index.php/Dm-crypt/Device_encryption#Preparation), [crypttab ref](https://www.freedesktop.org/software/systemd/man/crypttab.html).

Create a keyfile and place it on `/boot` and make it read-only to root:
```bash
sudo dd if=/dev/urandom of=/boot/keyfile bs=1024 count=4
sudo chmod 0400 /boot/keyfile
```

Add the key to LUKS:
```bash
sudo cryptsetup luksAddKey /dev/nvme0n1p3 /boot/keyfile
```

Add the keyfile to `/etc/crypttab`. Shouldn't need to change `/etc/fstab`.
```bash
# from
nvme0n1p3_crypt UUID=... none           luks,discard
# to
nvme0n1p3_crypt UUID=... /boot/keyfile  luks,discard
```

Now need to tell `initramfs` how to find the keyfile. Edit `/etc/cryptsetup-initramfs/conf-hook`:
```bash
KEYFILE_PATTERN="/boot/keyfile"
```

Then update:
```bash
update-initramfs -c -k
# or only update the latest to not break everything!
```

## Fix broken initramfs
(Because the above process is relatively likely to go wrong.)
Source: [Fix broken initramfs](https://feeding.cloud.geek.nz/posts/recovering-from-unbootable-ubuntu-encrypted-lvm-root-partition/)

Open a root terminal: `sudo su -`. Make sure to use the exact partition paths that crypttab, fstab etc use, otherwise things will break more.
```bash
cryptsetup luksOpen /dev/nvme0n1p3 nvme0n1p3_crypt
vgchange -ay
mount /dev/vgubuntu/root /mnt  # might also be /dev/mapper/vgubuntu-root
mount /dev/sda2 /mnt/boot
mount -t proc proc /mnt/proc
mount -o bind /dev /mnt/dev
mount -t sysfs sys /mnt/sys  # otherwise will get errors later!
```

Enter the partition and rebuild the initramfs:
```bash
chroot /mnt
update-initramfs -c -k all
```

When done, close LUKS vg and the crypt:
```bash
vgchange -a n vgubuntu
cryptsetup close nvme0n1p3_crypt
```

## Sleep then hibernate
Source: [sleep-then-hibernate](https://askubuntu.com/questions/12383/how-to-go-automatically-from-suspend-into-hibernate)

Gnome tweaks should be set to suspend on close lid. None of settings, gnome-tweaks, dconf-editor or logind.conf could mae power button hibernate. Which of these has priority?

Edit `/etc/systemd/sleep.conf`:
```bash
[Sleep]
HibernateDelaySec=3600
```

Test it:
```bash
sudo systemctl suspend-then-hibernate
```

If it works, change lid close action in `/etc/systemd/logind.conf`:
```bash
HandleLidSwitch=suspend-then-hibernate
```

Then restart the service:
```bash
sudo systemctl restart systemd-logind.service
```
