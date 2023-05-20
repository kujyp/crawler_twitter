from crawler.twitter import search_by_hashtag


def test_search_by_hashtag(driver):
    hashtag = "#점순쎄이2"
    userid = "jeomsoon3"

    ret = search_by_hashtag(driver, hashtag, userid)

    assert ret is not None
