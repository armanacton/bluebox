BlueBox
=======

A simple daemon for using NFC events to trigger playing MP3s on a
Raspberry PIs.

A simple web-interface is available on http://localhost:8888

This lets you add card-id/mp3 links tells you what is currently
playing.

Requirements
------------
 * mplayer (it uses slave mode, so mpv is not ok)
 * Some NFC hardware supported by
   [libnfc](http://nfc-tools.org/index.php?title=Libnfc) (I used a
   [ACR122U](http://www.acs.com.hk/en/products/3/acr122u-usb-nfc-reader/))
 * [nfc-eventd](http://nfc-tools.org/index.php?title=Nfc-eventd)

Buttons
-------

Connect simple push-buttons to PINs 16/18 to get pause/next-track
functionality.

Install
-------

Configure nfc-eventd with action like this, on insert:

```sh
   action = "curl http://localhost:8888/insert/$TAG_UID";
```

on removal:

```sh
   action = "curl http://localhost:8888/remove/$TAG_UID";
```

I used [supervisord](http://supervisord.org/) to start bluebox on
startup and keep it running if it should fall over.

A sample config script for supervisord is in supervisor-conf.sample
