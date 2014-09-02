import json

import tornado.ioloop
import tornado.web
import tornado.process
import tornado.template

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

TRACKFILE='bluebox-tracks.json'

BUTTON1 = 18
BUTTON2 = 16

process = None

cards = set()
status = None

def load_tracks():
    try:
        with file(TRACKFILE) as f:
            return json.load(f)
    except:
        return {}

def save_tracks(tracks):
    with file(TRACKFILE, 'w') as f:
        json.dump(tracks, f)

def get_track(id):

    return load_tracks().get(id)

def stop():
    print "STOP"
    if process:
        process.stdin.write('quit\n')

def stopped(*args):
    global process, status
    status = None
    process = None

def play(id):
    global process, status

    print "PLAY", id

    if process:
        process.set_exit_callback(lambda e: play(id))
        process.stdin.write('quit\n')
        return
    else:

        track = get_track(id)
        if not track: return
        status = "Playing ", track

        cmd = ['mplayer', '-quiet', '-slave']
        if track.endswith('m3u'): cmd.append('-playlist')
        cmd.append(track)

        process = tornado.process.Subprocess(cmd, stdin=tornado.process.Subprocess.STREAM)
        process.set_exit_callback(stopped)

def pause():
    print "PAUSE"
    if process:
        process.stdin.write('pause\n')

def ffwd():
    print "FAST-FORWARD"
    if process:
        process.stdin.write('pt_step 1\n')


class EventHandler(tornado.web.RequestHandler):
    def get(self, id):
        print self.request.path
        if self.request.path.startswith('/insert'):
            cards.add(id)
            play(id)
        else:
            if id in cards:
                cards.remove(id)
            stop()

        self.write('ok')

loader = tornado.template.Loader('bluebox/templates')

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        t = loader.load('status.html')
        self.write(t.generate(cards=cards, status=status))
        loader.reset()

class AddHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument('id')
        path = self.get_argument('path')

        tracks = load_tracks()
        tracks[id] = path
        save_tracks(tracks)

        self.write('ok')


application = tornado.web.Application([
    ("/", StatusHandler),
    ("/add", AddHandler),
    (r"/insert/(.*)", EventHandler),
    (r"/remove/(.*)", EventHandler),
], debug=True)

def click(channel):

    if channel == BUTTON1:
        tornado.ioloop.IOLoop.instance().add_callback(pause)
    if channel == BUTTON2:
        tornado.ioloop.IOLoop.instance().add_callback(ffwd)


if __name__ == "__main__":
    if GPIO:
        print "Using GPIO"
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(BUTTON1, GPIO.FALLING, callback=click, bouncetime=250)
        GPIO.add_event_detect(BUTTON2, GPIO.FALLING, callback=click, bouncetime=250)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=lambda channel: pause())

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
