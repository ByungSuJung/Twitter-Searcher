import requests
import json
import tweepy
import calendar

if __name__ == '__main__':
    auth = tweepy.OAuthHandler('eP693fMAoLJZn88sOxYFEfC5n', 'SAfpuSR7OS4Nx2oUB9DJ2IOiUNvb6QeeeZGuxEuTmR4gkGC5yL')
    auth.set_access_token('3169361870-85M2iVR95iXI9b6SZgbeTIKrlcZaJC1JUe5RNJm', '6BTCgq9KqRJvOM5e7sLJv8bbOoqRrNMdVFwnRSngyJ2mn')
    abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}

    with open ('userInfo.txt', 'w') as w:
        with open('ids.txt', 'r') as f:
            api = tweepy.API(auth_handler=auth, parser=tweepy.parsers.JSONParser())
            for line in f:
                user = api.get_user(line)
                since = str(user['created_at'])
                month = str(abbr_to_num[since[4:7]])
                if len(month) == 1:
                    month = '0' + month
                day = since[8:10]
                year = since[26:30]

                since = year + '-' + month + '-' + day + '\n'
                until = '2017-07-05' + '\n'
                print(line)
                print (since)
                print (until)
                w.write(line)
                w.write(since)
                w.write(until)





