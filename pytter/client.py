from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from .constants import *
import requests
from urllib.parse import urlencode
import re
from numpy import ceil


class Client:
    def __init__(self, checkbearer=False):

        uagent = UserAgent()
        chosenbrowser = uagent.firefox

        if checkbearer:

            user_agent = {
                'User-Agent': bearerbrowser,
                'Referer': url_referer}
            r = requests.get(url_base, headers=user_agent)
            soup = BeautifulSoup(r.text, "html.parser")
            js_with_bearer = ""
            for i in soup.find_all('link'):
                if i.get("href").find("/main") != -1:
                    js_with_bearer = i.get("href")

            # Get Bearer token
            user_agent = {'User-Agent': chosenbrowser,
                          'Referer': url_referer}

            if len(js_with_bearer) > 1:
                r = requests.get(js_with_bearer,
                                 headers=user_agent)
            # print(r.text)
            bearer = re.findall(
                r'",[a-z]="(.*)",[a-z]="\d{8}"',
                r.text,
                re.IGNORECASE)[0].split("\"")[-1]

        else:
            bearer = bearerconst

        hdrs_guest = {
            'authorization': f'Bearer {bearer}',
            'User-Agent': chosenbrowser
        }

        guest_token = requests.post(
            endpoint_guesttoken,
            headers=hdrs_guest).json()["guest_token"]

        self.headers = {
            'authorization': f'Bearer {bearer}',
            'x-guest-token': guest_token,
            'User-Agent': chosenbrowser
        }

    def prepparams(self, pardicts: dict = {}):

        paramsprep = {}
        for ke in pardicts.keys():
            if pardicts[ke] != None:
                paramsprep[ke] = pardicts[ke]

        return paramsprep

    def status_ratelimit(self, resources=None):

        uro = endpoint_ratelimit
        urf = uro+'?'+urlencode(self.prepparams({'resources': resources}))
        response = requests.get(urf, headers=self.headers).json()
        return response

    def tweets_user(self,
                    screen_name,
                    since_id: str = None,
                    max_id: str = None,
                    count: int = 10,
                    exclude_replies: bool = False,
                    include_rts: bool = False):

        uro = endpoint_tweetuser
        queries = urlencode(
            self.prepparams(
                {'screen_name': screen_name,
                 'since_id': since_id,
                 'count': count,
                 'max_id': max_id,
                 'exlude_replies': str(exclude_replies),
                 'include_rts': str(include_rts)}))
        urf = uro+'?'+queries

        response = requests.get(urf, headers=self.headers).json()

        return response

    def getprecisenumtweets(self,
                            screen_name,
                            since_id: str = None,
                            max_id: str = None,
                            count: int = 10,
                            exclude_replies: bool = False,
                            include_rts: bool = False):

        litweets = []
        last_ids = []

        if count <= 200:
            countr = ceil(count+0.2*count)
        else:
            countr = 200

        while len(litweets) < count:
            if len(last_ids) == 0:
                statuses = self.tweets_user(
                    screen_name=screen_name,
                    since_id=since_id,
                    max_id=max_id,
                    count=str(countr),
                    exclude_replies=exclude_replies,
                    include_rts=include_rts)
            else:
                statuses = self.tweets_user(
                    screen_name=screen_name,
                    since_id=since_id,
                    max_id=last_ids[len(last_ids)-1],
                    count=str(countr),
                    exclude_replies=exclude_replies,
                    include_rts=include_rts)
            for s in range(len(statuses)):
                stat = statuses[s]
                stat_txt = stat['text']
                stat_id = stat['id_str']
                if len(stat_txt) > 0:
                    if stat not in litweets:
                        litweets.append(stat)
                        if s == (len(statuses)-1):
                            last_ids.append(stat_id)

        return litweets[0:count]

    def getprecisenumtweetstext(self,
                                screen_name,
                                since_id: str = None,
                                max_id: str = None,
                                count: int = 10,
                                exclude_replies: bool = False,
                                include_rts: bool = False):

        litweets = [tweet['text'] for tweet in self.getprecisenumtweets(
            screen_name=screen_name,
            since_id=since_id,
            max_id=max_id,
            count=count,
            exclude_replies=exclude_replies,
            include_rts=include_rts)]

        return litweets
