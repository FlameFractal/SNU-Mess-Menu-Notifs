import urllib.request

domainUrl = 'https://fast-falls-57984.herokuapp.com'
botToken = '439142723:AAGxI51LsPuv0dgzta0lGgH1aJLZfIuDTvE';

urllib.request.urlopen(domainUrl+'/sendMenuAllUsers'+botToken)