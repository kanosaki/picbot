
import picbot

from picbot.utils import uniq


pixiv = picbot.pixiv(username='foobar', password='hogehoge')

rankings = uniq(
    pixiv.ranking(date=-0)[:100] +
    pixiv.ranking(date=-2)[:100] +
    pixiv.ranking(date=-3)[:100]
)

default_sink = picbot.sink.Folder('~/Dropbox/Documents/picbot/default')
default_sink.clear()
default_sink.drain(rankings)
