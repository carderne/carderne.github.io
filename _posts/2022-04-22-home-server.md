---
layout: single
title: "Home server setup"
date: "2022-04-22"
excerpt: "Bits and pieces cobbled together setting up a Raspberry Pi home server"
---

These are notes I've gathered setting up my Raspberry Pi home server, together with some apps and services that I use on it. I'm putting it here (instead of the jumble of Markdown files whence it came) for my own personal use; it's not intended to be useful to anyone else. That said, there might be snippets that are useful if some search engine led you here trying to figure out how to secure your SSH or something...

## Installation
This assumes that the Raspberry Pi (RPi from here on) will be connected over a wired connection. If it will _only_ connect over WiFi, there are some [additional instruction here](https://rdrn.me/wake-up-light/#setting-up-the-raspberry-pi).
1. Get an Ubuntu image [from here](https://ubuntu.com/download/raspberry-pi).
2. Install `sudo apt install rpi-imager`.
3. Use `rpi-imager` to write the downloaded `.img.xz` file to the microSD card.
4. It will give some options about setting up default users etc, which you can use and skip the below.
5. Insert into the Raspberry Pi and boot it.

## First login
Log in as ubuntu (unless you created a different user and login method already):
```bash
ssh ubuntu@192.168.whatever.whatever  # set ip address to whatever it is
# password is ubuntu
```

And create a new user:
```bash
useradd -m -U -s /bin/bash -G sudo your-username
passwd your-username
```

Change host name by editing `/etc/hostname` to contain:
```
box
```
Restart, then log in as new user:
```bash
ssh username@box.local  # your network might not do the .local thing nicely
```

Set `vim` as editor:
```bash
sudo update-alternatives --config editor
```

Stop SSH login message:
```bash
touch ~/.hushlogin
```

Set hostname. Add the following to `/etc/hosts` (or edit if there's a similar line there):
```
127.0.1.1 box.local box
```

## Firewall
First open the new port in UFW!
```bash
# use the appropriate subnet mask
sudo ufw allow from 192.168.178.0/24 to any port 22 proto tcp comment "SSH"
sudo ufw enable

# check your work
sudo ufw status
```

## SSH login
Do these steps on your local machine (the place from where you log into the RPi).
Put in `~/.ssh/config`:
```
Host box
  HostName 192.168.whatever.whatever
  User username
```

Copy SSH key if needed:
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub user@ip_address
```

Make sure you can now log in:
```bash
ssh box
```

## Securing SSH
[Following this](https://linuxhandbook.com/ssh-hardening-tips/) and [this](https://securitytrails.com/blog/mitigating-ssh-based-attacks-top-15-best-security-practices).
Make the following changes to `/etc/ssh/sshd_config`. You can't just copy-paste these in, as they might be set already, so search through and change/uncomment them one by one.

Note the changed port number. This is mostly to reduce the number of failed attempted logins you see in your logs. By setting this to a random number, you'll sleep more easily knowing nobody is getting in!
```bash
PermitRootLogin no
PermitEmptyPasswords no
PasswordAuthentication no
X11Forwarding no
# MaxAuthTries 1  # rather use Fail2Ban

# not used yet
# ClientAliveInterval 300
# ClientAliveCountMax 2

# this number is an example, choose your own!
Port 38473
```

**NB**: Make up your own port number above, and then make sure to open it in UFW!
```bash
# Replace the number with whatever you chose
sudo ufw allow from 192.168.178.0/24 to any port 38473 proto tcp comment "SSH"
```

Then:
```bash
sudo systemctl restart ssh sshd
```

You can use these commands to keep an eye on SSHD logs:
```bash
tail -n 50 /var/log/auth.log | grep sshd

# follow
tail -f -n 10 /var/log/auth.log | grep sshd
```

## Fail2Ban
A nifty tool to make your SSH logs less annoying and keep unwanted script-kiddes from messing around with your SSH.
[Following this](https://linuxhandbook.com/fail2ban-basic/) and the [main docs](https://www.fail2ban.org/wiki/index.php/Commands). [Reference for adding "Failed publickey"](https://github.com/fail2ban/fail2ban/issues/2188#issuecomment-407427943).

```bash
sudo apt install fail2ban
```

Don't edit the main conf. Rather edit `/etc/fail2ban/jail.local`:
```
[sshd]
bantime = 1d  # can increase this later
findtime = 1d # can increase this later
maxretry = 5  # can lower this once you're sure you're good!
failregex = %(known/failregex)s
            ^Failed publickey for <F-USER>.+</F-USER> from <HOST>
             ^Connection closed by authenticating user <F-USER>.+</F-USER> <HOST> port \d+ \[preauth\]
```

Then:
```bash
systemctl start fail2ban
systemctl enable fail2ban
```

Useful commands:
```bash
# see logs
less /var/log/fail2ban.log

# status
sudo fail2ban-client status sshd

# admin
sudo fail2ban-client restart
# ... reload, start, stop

# unban
sudo fail2ban-client set sshd unbanip 192.168.whatever.whatever
```

## Useful systemd stuff
Systemctl commands:
```bash
sudo systemctl daemon-reload                       # whenever change config file
sudo systemctl start/stop/restart calibre-flask
```

Allow restart `systemctl` services without sudo. Create a new `sudoers` file with:
```bash
sudo visudo -f /etc/sudoers.d/nopassword
```

And add the line:
```
your-username ALL = NOPASSWD: /bin/systemctl restart service-name
```

## X forwarding
Haven't had much success with this yet, but pretty cool forward full X windows over SSH!
```bash
ssh -X pc qgis

# or
ssh -X pc
qgis
```

## Disable LEDs
The flashing lights on the RPi, which don't look great in a classy living room. [Source](https://n.ethz.ch/~dbernhard/disable-led-on-a-raspberry-pi.html). First try:
```bash
echo 0 | sudo tee /sys/class/leds/led1/brightness > /dev/null
```

If it works then `sudo crontab -e`:
```
@reboot echo 0 | sudo tee /sys/class/leds/led0/brightness > /dev/null
@reboot echo 0 | sudo tee /sys/class/leds/led1/brightness > /dev/null
```


## Nginx basics
[Source](https://ubuntu.com/tutorials/install-and-configure-nginx#2-installing-nginx). Install:
```
sudo apt install nginx
```

Delete default site:
```
sudo rm /etc/nginx/sites-enabled/default
# template still at /etc/nginx/sites-available/default
```

Remember need to `sudo service nginx restart` each time change config. Create file (e.g.) `/etc/nginx/sites-enabled/foo.rdrn.me`:
```nginx
server {
    server_name foo.rdrn.me;

    # to pass eg a Flask app server
    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}
```

## Certbot
[Source](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04). Install:
```bash
sudo apt install certbot python3-certbot-nginx
```

Open firewall:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

Get certificate and automatically update Nginx config:
```bash
sudo certbot --nginx -d books.rdrn.me
```

Check auto-renew:
```bash
sudo certbot renew --dry-run
```

Go and check the nginx config and it should have been updated by Certbot.

## Calibre-Flask
My home-made web frontend for the [Calibre](https://calibre-ebook.com/) ebook library: [calibre-flask](https://github.com/carderne/calibre-flask).

### Installation
Install some packages:
```bash
sudo apt install git python3-venv python3-pip nginx

# https://stackoverflow.com/a/50583153
sudo apt install libopenjp2-7 libtiff5 libatlas-base-dev
```

Follow instructions at the [repo](https://github.com/carderne/calibre-flask).

Temporarily `sudo ufw allow 5000` for testing.

Place nginx file at `/etc/nginx/sites-enabled/books.rdrn.me` then `sudo service nginx restart`. Start server with `gunicorn app.app:app` and should be available at port 80.

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d books.rdrn.me
```

## Nextcloud setup
I do it with Nginx (rather than Apacha, which is more typical).

[Source](https://www.howtoforge.com/tutorial/ubuntu-nginx-nextcloud/).
Empty deleted files sooner: [source](https://bayton.org/docs/nextcloud/nextcloud-hoarding-trash-how-to-force-automatic-removal-of-deleted-items/).
Can't view recycle bin: [source](https://help.nextcloud.com/t/problem-with-deleted-files/64978/4).
Change data directory: [source](https://help.nextcloud.com/t/howto-change-move-data-directory-after-installation/17170).

### PHP setup
Install:
```bash
sudo apt install -y php-fpm php-curl php-cli php-mysql php-gd php-common php-xml php-json php-intl php-pear php-imagick php-dev php-common php-mbstring php-zip php-soap php-bz2 php-bcmath php-gmp redis-server php-redis
```

Edit configs `/etc/php/8.1/fpm/php.ini` and `/etc/php/8.1/cli/php.ini` with the following two lines:
```ini
date.timezone = Europe/London
cgi.fix_pathinfo=0
memory_limit = 512M  # only in fpm/php.ini
```

Edit `/etc/php/7.4/fpm/pool.d/www.conf` and uncomment:
```conf
env[HOSTNAME] = $HOSTNAME
env[PATH] = /usr/local/bin:/usr/bin:/bin
env[TMP] = /tmp
env[TMPDIR] = /tmp
env[TEMP] = /tmp
```

Start:
```bash
sudo systemctl restart php8.1-fpm
sudo systemctl enable php8.1-fpm
```

Check status:
```bash
ss -xa | grep php
systemctl status php8.1-fpm
```

### MariaDB
Install:
```bash
sudo apt install mariadb-server -y
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

Configuration:
```bash
sudo mysql_secure_installation
# yes to all
```

Set up NextCloud user:
```bash
sudo mysql -u root -p

create database nextcloud;
create user nextclouduser@localhost identified by 'password-here';
grant all privileges on nextcloud.* to nextclouduser@localhost identified by 'password-here';
flush privileges;
```

### Let's Encrypt
Only if you want it publicly facing (I don't currently do this) and you want a proper HTTPS site.

Install:
```bash
sudo apt install certbot -y
```

Config:
```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone -d domain.com
```

### Actual NextCloud installation
Install (or get [beta from here](https://github.com/nextcloud/server/releases)):
```bash
sudo apt install wget unzip zip -y
cd /var/www/
sudo wget -q https://download.nextcloud.com/server/releases/latest.zip
sudo unzip -qq latest.zip
sudo chown -R www-data:www-data /var/www/nextcloud
```

NB: Only do this step if you get a `3rdparty` error when trying to load the web page:
```bash
cd /var/www/nextcloud
rm -r 3rdpart
git clone https://github.com/nextcloud/3rdparty.git
```

Make data directory:
```bash
sudo mkdir /opt/nextcloud/
sudo chown -R www-data:www-data /opt/nextcloud/
```

### Nextcloud Nginx setup
Install:
```bash
sudo apt update
sudo apt install nginx -y
```

Configure Nginx site: `/etc/nginx/sites-enabled/domain.com`.
Additional [source](https://docs.nextcloud.com/server/18/admin_manual/installation/nginx.html).

```nginx
upstream php-handler {
    server unix:/var/run/php/php8.1-fpm.sock;
}

server {
    listen 8080;
    listen [::]:8080;
    server_name box.local;
    fastcgi_hide_header X-Powered-By;
    root /var/www/nextcloud;
    add_header Referrer-Policy "no-referrer" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Download-Options "noopen" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Permitted-Cross-Domain-Policies "none" always;
    add_header X-Robots-Tag "none" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location = /.well-known/carddav {
        return 301 $scheme://$host:$server_port/remote.php/dav;
    }
    location = /.well-known/caldav {
        return 301 $scheme://$host:$server_port/remote.php/dav;
    }

    client_max_body_size 512M;
    fastcgi_buffers 64 4K;
    gzip on;
    gzip_vary on;
    gzip_comp_level 4;
    gzip_min_length 256;
    gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
    gzip_types application/atom+xml application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;

    location / {
    rewrite ^ /index.php;
    }

    location ~ ^\/(?:build|tests|config|lib|3rdparty|templates|data)\/ {
        deny all;
    }
    location ~ ^\/(?:\.|autotest|occ|issue|indie|db_|console) {
        deny all;
    }

    location ~ ^\/(?:index|remote|public|cron|core\/ajax\/update|status|ocs\/v[12]|updater\/.+|oc[ms]-provider\/.+)\.php(?:$|\/) {
        fastcgi_split_path_info ^(.+?\.php)(\/.*|)$;
        set $path_info $fastcgi_path_info;
        try_files $fastcgi_script_name =404;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $path_info;
        fastcgi_param modHeadersAvailable true;
        fastcgi_param front_controller_active true;
        fastcgi_pass php-handler;
        fastcgi_intercept_errors on;
        fastcgi_request_buffering off;
    }

    location ~ ^\/(?:updater|oc[ms]-provider)(?:$|\/) {
        try_files $uri/ =404;
        index index.php;
    }

    location ~ \.(?:css|js|woff2?|svg|gif|map)$ {
        try_files $uri /index.php$request_uri;
        add_header Cache-Control "public, max-age=15778463";
        add_header Strict-Transport-Security "max-age=15768000;" always;
        add_header Referrer-Policy "no-referrer" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Download-Options "noopen" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Permitted-Cross-Domain-Policies "none" always;
        add_header X-Robots-Tag "none" always;
        add_header X-XSS-Protection "1; mode=block" always;
        access_log off;
    }

    location ~ \.(?:png|html|ttf|ico|jpg|jpeg|bcmap)$ {
        try_files $uri /index.php$request_uri;
        access_log off;
    }
}
```

Start it up:
```bash
systemctl restart nginx
systemctl restart php7.4-fpm
```

### Allow nextcloud through the firewall
```bash
# might want to add subnet mask, comment, proto to this
sudo ufw allow 8080
```

### Nextcloud post-install:
Go to `domain.com` and enter a new NextCloud user and password, along with the data and database details from above.

Enable memcache by editing `/var/www/nextcloud/config/config.php` and add the following before the closing parentheses `);`:
```
'memcache.local' => '\OC\Memcache\Redis',
'redis' => array(
'host' => 'localhost',
'port' => 6379,
),
'memcache.locking' => '\OC\Memcache\Redis',
```
## pihole
[Source](https://github.com/pi-hole/pi-hole/#one-step-automated-install).

```bash
# yuk!
curl -sSL https://install.pi-hole.net | bash
```

No to web portal, logging stats etc.
Set Router DNS to PiHole with 9.9.9.9 as backup.

```bash
# might want to add a comment
ufw allow 53
```

Lists: [source](https://github.com/jessedp/pihole5-list-tool).

```bash
sudo apt install python3-pip
sudo pip3 install pihole5-list-tool --upgrade
sudo pihole5-list-tool
pihole -g
```

Web admin console should be at `http://localhost:8088/admin/`.

## Transmission torrent client
### Installation
[Source 1](https://www.smarthomebeginner.com/install-transmission-web-interface-on-ubuntu-1204/), [Source2](https://linuxconfig.org/how-to-set-up-transmission-daemon-on-a-raspberry-pi-and-control-it-via-web-interface).

Install:
```bash
sudo add-apt-repository ppa:transmissionbt/ppa
sudo apt install transmission-cli transmission-common transmission-daemon
```

Set up folders and dirs:
```bash
cd ~
mkdir transmission
cd transmission
mkdir downloads torrents
```

Set up user permissions:
```bash
# add self to transmission usergroup
sudo usermod -a -G debian-transmission your-username

sudo chgrp -R debian-transmission /home/your-username/transmission
sudo chmod -R 775 /home/your-username/transmission
```

Should be running at: http://localhost:9091/transmission/web/.

### Configuration
Service at `/lib/systemd/system/transmission-daemon.service`.

Need to stop the daemon before editing config. Don't forget to start it again.
```bash
sudo systemctl stop transmission-daemon
```

Edit `/etc/transmission-daemon/settings.json`. Change `download-dir`, `username`, `password`, `whitelist`.

Add:
```json
"watch-dir": "/home/pi/transmission/torrents",
"watch-dir-enabled": true
```

### Open firewall
Check port in `settings.json`. Only needed if you want full discoverability.
```bash
sudo ufw allow 51413
```

### Nginx proxy
Add to Nginx to properly forward Web UI (only if you want it at `:80` port).
```nginx
server {
    location /transmission/ {
        proxy_pass_header X-Transmission-Session-Id;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:9091/transmission/web/;
    }
    location /rpc {
        proxy_pass         http://127.0.0.1:9091/transmission/rpc;
    }
}
```

## General logging
### Nginx logging
Add in server block:
```nginx
access_log /var/log/nginx/nc.rdrn.me.access.log;
error_log /var/log/nginx/nc.rdrn.me.error.log;
```

### Logrotate
Edit `/etc/logrotate.d/nginx`:
```
/var/log/nginx/*.log {
        monthly
        dateext
        dateyesterday
        missingok
        rotate 12
        nocompress
        notifempty
        create 0640 www-data adm
        sharedscripts
        prerotate
                if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
                        run-parts /etc/logrotate.d/httpd-prerotate; \
                fi \
        endscript
        postrotate
                invoke-rc.d nginx rotate >/dev/null 2>&1
        endscript
}
```

### Nginx logs
```
less /var/log/nginx/books.rdrn.me.access.log
```

### SSH logs
```
sudo journalctl _COMM=sshd | tail -100
```

### UFW logs
```
sudo less /var/log/ufw.log
```

### Transmission logs
```
sudo journalctl | grep transmission
```

## Only allow access from certain countries
I'm not currently using this. [Source1](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-20-04). [Source2](https://www.ustoopia.nl/technical/block-all-traffic-from-a-geo-located-country-with-ufw-firewall-on-ubuntu/). [Source3](https://serverfault.com/questions/907607/slow-rules-inserting-in-ufw).

Go to [ip2location](https://www.ip2location.com/free/visitor-blocker) and download lists in CIDR format. Merge the lists.

It will be thousands of lines, and inserting with `ufw allow ...` takes too long.

Do:
```bash
cat cidr-allow.txt | grep -v ^# | while read subnet; do echo "-A ufw-before-input -p tcp --dport 443 -s $subnet -j ACCEPT" >> rules.out; done
```

Then paste these lines into `/etc/ufw/before.rules` before the `COMMIT` line.

Then run:
```bash
sudo ufw reload
```

## Mount encrypted drives
Manually decrypt drive:
```bash
sudo cryptsetup luksOpen /dev/sda1 sda1_crypt
```

If that works, create a key so that it can be decrypted automatically:
```bash
dd if=/dev/random bs=32 count=1 of=/opt/backup_key
cryptsetup luksAddKey /dev/sda1 /opt/backup_key
```

Then edit `/etc/crypttab`:
```
sda1_crypt /dev/sda1 /opt/backup_key
```

Create mountpoint:
```bash
mkdir ~/backup
```

Edit `/etc/fstab`:
```
/dev/mapper/sda1_crypt /home/your-username/backup ext4 defaults,user,rw 0 0
```

Mount:
```bash
mount ~/backup
```

*NB*: If there's something wrong with your `crypttab` or `fstab`, it will probably fail on boot! If that happens, pull out the microSD card and comment out the offending lines somewhere else.

## Things to do on the LAN router
Set static IP.
Port forwarding.