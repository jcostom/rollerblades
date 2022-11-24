# Rollerblades

## Plex preroll automatic rotation script

You've spent all that time building up your Plex library, so you decide you want to play around with some of Plex's fun features, like prerolls. But before long, you're bored with seeing the same clip every time, right? So, you find another and change it up. Then you find another, and another, and another.

Before long, you're in the Plex settings messing around with preroll every other day, and honestly? It's a pain in the rear, so you'd like to automate changing these prerolls. Maybe a regular rotation. But wait, there are special holiday prerolls you like too, and there's that fun April Fool's Day one as well that you pranked your family with. How do you keep up with all of these?

Yes, there's [another solution](https://github.com/TheHumanRobot/Rollarr) out there already. I tried it, and while yes, it sure does look really impressive, honestly, I couldn't get it to work reliably. For *me*, it literally worked once. Four hours of bashing my head against the table later, I gave up and started writing this. Now call me biased, but in the end, I like this better. Sure, the other tool has a fancy web UI, but this is small, tight, and just works - for me at least. Maybe the other thing works for everyone else, and I'm some kind of knucklehead. If that's the case, I'll own that. This also runs as a Docker container, which for me is no big deal, since I've already got a load of other Docker containers running on systems. What's one more? Let's get to the "how" part.

## Find Your Plex Token

This is the hardest part, and honestly, it's not hard. Go into the Plex Web UI, pull up any movie or episode of a show, hit the 3-dots button (More), then Get Info. This brings up the Media Info screen, with all the details about your media file, with all the specifics, down to video and audio codecs, etc. In the bottom left corner of that window, there's a link that says, "View XML". Click it. Your browser will pop open a new tab with a bunch of XML. Copy the URL from your browser and paste it into a text editor somewhere. You're looking for the very end of the URL. It will say, "X-Plex-Token=[bunch of text]". You're interested in the bunch of text after the equals sign. Make a note of this - this is the Plex Token. You'll need this later when you go to instantiate your container.

## Create your Config File

This might seem a little daunting if you've never created JSON (Javascript Object Notation) formatted text before, but it's really not so bad. You'll be a pro in no time, especially if you've ever written Python code. You'll want sections for the MONTHS, HOLIDAYS, and DAILYPATH areas.

**NOTE**: Version 0.6 and later introduce a couple of small changes to the JSON config file. Previously, the "month" section was called SPECIAL_MONTHS and used the name of the month. As of version 0.6, the configuration now uses MONTHS as the name of the section, and uses 2-digit numbers for the month, using a leading zero for Jan - Sept.

Here's my config for an example:

```json
{
    "MONTHS": {
        "06": "/prerolls/pride.mp4"
    },
    "HOLIDAYS": {
        "0401": "/prerolls/holiday/april-fool.mp4",
        "1225": "/prerolls/holiday/christmas.mp4",
        "0214": "/prerolls/holiday/valentine.mp4",
        "1031": "/prerolls/holiday/halloween.mp4"
    },
    "DAILYPATH": "/prerolls/daily"
}
```

Even if you're not going to do the MONTH thing, put something in there, you can turn the feature off, I promise. More on that later when we get to the how to launch the container stuff.

## Launching the Container

If you're the launching from CLI type, you'll need to make a directory for your config file, drop that on the host, and then instantiate your container. For our purposes here, I'm going to assume you decided to stick your files in a directory called `/var/docks/rollerblades`. You can put your files whereever you feel like though. You do you. Also, be safe - don't run this thing as root. There's really no need to. You don't need any sort of special privileges to run this, so I'm going to assume you're going to run this as your regular user. Figure out your user's UID and GID value. To get this most easily, jump into the terminal and type `id`. The first two things to come back will be your UID and GID values. Note these as well.

Ready? You'll of course, need to know the URL scheme (http/https), hostname, port (if it's different than 32400), your Plex token that you figured out above, the path to your config file (from the perspective of the container, if not `/config/prerolls.json`), if you intend to turn off the Months feature, how often you want to sync the preroll setting (default is hourly), and if you need to turn on debugging. Here's a sample invocation:

```bash
docker run -d \
    --name=rollerblades \
    --restart=unless-stopped \
    --user=1000:1000 \
    -v /var/docks/rollerblades:/config \
    -e HOST=plex.mynetwork.net \
    -e TOKEN=ABC123def987xyz \
    ghcr.io/jcostom/rollerblades:latest
```

Personally, I prefer to run using `docker-compose`. I run my instance as part of a stack in Portainer, but as always, you do you. Here's an example `docker-compose` file you could use:

```yaml
---
version: '3'

services:
  rollerblades:
    image: ghcr.io/jcostom/rollerblades:latest
    container_name: rollerblades
    volumes:
      - /var/docks/rollerblades:/config
    environment:
      - HOST=plex.mynetwork.net
      - TOKEN=ABC123def987xyz
    restart: unless-stopped
    user: 1000:1000
    network_mode: bridge
```

You'll note in both of these examples, I'm leveraging many of the defaults - https, port 32400, the 3600s sync interval, leaving the Month feature activated, default location for config file, etc. That's why so few options in use.

## Variables you may want to change for one reason or another

1. If you'd like to deactivate the MONTHS feature, set the environment variable USE_MONTHS to 0.
2. If you wish to connect to your Plex using http instead of https, set SCHEME to 'http' (default is https).
3. If your Plex isn't running on tcp/32400, set PORT to whatever port you can find it on.
4. If things are going bananas and you want more info in the logs set DEBUG to 1.
