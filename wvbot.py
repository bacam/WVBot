import logging
import re
from irc import IRC

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

volunteering_regexes = [
    r'^(I think )?(that )?We should (.*)$',
    r'^Why don\'t we (.*)$',
    r'^Tardis should (.*)$',
    r'^Someone (should|needs to) (.*)$',
    r'^(Please )?(Can|Could) someone (.*)$',
    r'^It would be good if (.*)$'
]

irc = IRC(host="irc.imaginarynet.org.uk", port=6667, nick="WVBot", channel="#bottest")

def main():
    irc.channel_message_received_callback = channel_message
    irc.start_connection()

def channel_message(sender, channel, message):
    for regex in volunteering_regexes:
        if re.match(regex, message, re.IGNORECASE):
            irc.send_channel_message(channel, "{0}: Well Volunteered!".format(sender))
            logger.info("Well Volunteered message sent to {0} in {1}".format(sender, channel))

if __name__ == '__main__':
    main()