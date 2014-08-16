import urllib

def parse_latex(bot, msg, replyto, username, matches):
    bot.factory.logger.debug('Found latex expression "%s"' % matches[0])

    coded = urllib.quote(matches[0])
    url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?%s' % coded
    bot.msg(replyto, url)

def load_module(bot):
    bot.hook_regexp('^\$(.+)\$$', parse_latex)
