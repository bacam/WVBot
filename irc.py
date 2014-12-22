'''
    This class abstracts all the IRC stuff into a simple API
'''
import re
import logging
from tornado import tcpclient, gen, ioloop

logger = logging.getLogger(__name__)

class IRC(object):
    def __init__(self):
        self.host = "irc.imaginarynet.org.uk"
        self.port = 6667
        self.nick = "WVBot"
        self.channel = "#bottest"
        self.conn = None
        self.loopinstance = ioloop.IOLoop.instance()
        self.channel_message_received_callback = None
        self.joined_channels = False

    # Connects to the IRC server and returns a future
    @gen.coroutine
    def _connect_to_server(self):
        logger.info("Connecting to IRC server - {0}:{1}".format(self.host, self.port))
        tcpclient_factory = tcpclient.TCPClient()
        self.conn = yield tcpclient_factory.connect(self.host, self.port)
        self.loopinstance.add_future(self._schedule_line(), self._line_received)

    # Returns a future that will return a line retrieved from the server
    def _schedule_line(self):
        return self.conn.read_until(b'\n')

    # Sends a line of text to the server, used by other functions in this class
    def _write_line(self, data):
        if data[-1] != '\n':
            data += '\n'

        self.conn.write(data.encode('utf8'))

    def _line_received(self, data):
        line = data.result().decode('utf8')
        if self.channel_message_received_callback != None:
            # We need to use a regex to check if this is a channel message and extract the
            # important bits from it
            match = re.match(r":(.*)!.* PRIVMSG (#.*) :(.*)", line)
            if match:
                self.channel_message_received_callback(match.group(1), match.group(2), match.group(3))

        # Is the line a PING?
        if line.startswith("PING"):
            self._reply_ping(line)

        self.loopinstance.add_future(self._schedule_line(), self._line_received)

    def _reply_ping(self, ping_line):
        logger.debug("PING recieved, replying")
        reply_line = ping_line.replace("PING", "PONG")
        self._write_line(reply_line)

        # Now that we have pinged the server, we can join channels assuming that we have not
        # already joined
        if not self.joined_channels:
            self._join_channel()
            self.joined_channels = True

    def _ident(self):
        logger.info("Identing with server")
        self._write_line("USER {0} {1} {2} {3}".format(self.nick, self.nick, self.nick, self.nick))
        self._write_line("NICK {0}".format(self.nick))

    def _join_channel(self):
        logger.info("Joining channel")
        self._write_line("JOIN {0}".format(self.channel))

    def start_connection(self):
        self.loopinstance.add_future(self._connect_to_server(), self._connection_complete)

        self.loopinstance.start()

    def _connection_complete(self, data):
        logger.debug("Connection Complete")
        self._ident()
