import urllib.parse

def parse_latex(bot, c, e, matches):
    bot.logger.debug('Found latex expression "%s"' % matches[1])

    coded = urllib.parse.quote(matches[1])
    url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?%s' % coded
    bot.reply(c, e, url)

def load_module(bot):
    bot.hook_regexp('^\$(.+)\$$', parse_latex)

    return [hash(parse_latex)]
