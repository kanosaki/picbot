
from nose.tools import *
from picbot import utils

class TestAttrAccess(object):
    def test_normal(self):
        src = {"foo": "bar", "hoge": {"x": "y"}}
        ad = utils.AttrAccess(src)
        assert_equal(ad.foo, "bar")
        assert_equal(ad.hoge, {"x": "y"})
        assert_equal(ad.hoge.x, "y")

    @raises(AttributeError)
    def test_notfound(self):
        src = {"foo": "bar", "hoge": {"x": "y"}}
        ad = utils.AttrAccess(src)
        ad.hogehoge




