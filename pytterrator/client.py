from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from .constants import *
import requests
from urllib.parse import urlencode
import re
import time
import numpy as np

class Client:
    """A main class for the client. When initiated, it
    first obtains the guest-token and generated header for
    obtaining the tweets without logging in. Further, it contains
    functions that would work for scraping tweets for any public
    twitter user, ultimately returning an exact number of tweet requested
    if possible.
    """

    def __init__(self, checkbearer=False):
        """Initiating the Client class

        Args:
            checkbearer (bool, optional): If True, will scrape the twitter.com
            page to check a new bearer token. Defaults to False.
        """
        uagent = UserAgent()
        chosenbrowser = uagent.random

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

    def prepparams(self, pardicts: dict = {}) -> dict:
        """Clean up a dictionary from keys with empty values in it
        ('None' as values).

        Args:
            pardicts (dict, optional): Entered dictionary.
            Defaults to {}.

        Returns:
            dict: The cleaned-up dictionary, free from keys with
                'None' values.
        """

        paramsprep = {}
        for ke in pardicts.keys():
            if pardicts[ke] != None:
                paramsprep[ke] = pardicts[ke]

        return paramsprep

    def status_ratelimit(self, resources: str = None) -> dict:
        """Check the rate limit of the current Client session.

        Args:
            resources (str, optional): A comma-separated list of resource
                families you want to know the current rate limit disposition for.
                Example is 'help,users,search,statuses'. Defaults to None.

        Returns:
            dict: a dictionary from json of the API response, containing
                the rate limit informations.
        """

        uro = endpoint_ratelimit
        urf = uro+'?'+urlencode(self.prepparams({'resources': resources}))
        response = requests.get(urf, headers=self.headers).json()
        return response

    def tweets_user(self,
                    screen_name: str,
                    since_id: str = None,
                    max_id: str = None,
                    count: int = 10,
                    exclude_replies: bool = False,
                    include_rts: bool = False) -> list:
        """Scrape the tweets from a user if they have a public profile.

        Args:
            screen_name (str): The twitter username of the user.
            since_id (str, optional): The twitter status ID of the earliest tweet
                that you'd like to scrape. Defaults to None.
            max_id (str, optional): The twitter status ID of the latest tweet that
                you'd like to scrape. Defaults to None.
            count (int, optional): The number of twitter statuses that you'd like
                to scrape. The final number isn't always exactly the same as
                the count requested. Defaults to 10.
            exclude_replies (bool, optional): Option to exclude tweet replies
                from the scraped statuses. Defaults to False.
            include_rts (bool, optional): Option to include retweets from the
                scraped statuses. Defaults to False.

        Returns:
            list: An array containing dictionaries, each containing data of a status.
        """

        uro = endpoint_tweetuser
        queries = urlencode(
            self.prepparams(
                {'screen_name': screen_name,
                 'since_id': since_id,
                 'count': int(float(count)),
                 'max_id': max_id,
                 'include_rts': (str(include_rts)).lower(),
                 'exclude_replies': (str(exclude_replies)).lower()}))

        urf = uro+'?'+queries
        response = requests.get(urf, headers=self.headers).json()

        return response

    def getprecisenumtweets(self,
                            screen_name,
                            since_id: str = None,
                            max_id: str = None,
                            count: int = 10,
                            exclude_replies: bool = False,
                            include_rts: bool = False) -> list:
        """Scrape the tweets from user if they have a public profile. Will try
        to return the exact number of the tweets asked.

        Args:
            screen_name (str): The twitter username of the user.
            since_id (str, optional): The twitter status ID of the earliest tweet
                that you'd like to scrape. Defaults to None.
            max_id (str, optional): The twitter status ID of the latest tweet that
                you'd like to scrape. Defaults to None.
            count (int, optional): The number of twitter statuses that you'd like
                to scrape. The final number isn't always exactly the same as
                the count requested. Defaults to 10.
            exclude_replies (bool, optional): Option to exclude tweet replies
                from the scraped statuses. Defaults to False.
            include_rts (bool, optional): Option to include retweets from the
                scraped statuses. Defaults to False.

        Returns:
            list: An array containing dictionaries, each containing data of a status.
        """

        litweets = []
        last_ids = []
        lenlastobtained = []

        while len(litweets) < count:
            lenstart = len(litweets)
            if len(last_ids) == 0:
                statuses = self.tweets_user(
                    screen_name=screen_name,
                    since_id=since_id,
                    max_id=max_id,
                    count=str(count),
                    exclude_replies=exclude_replies,
                    include_rts=include_rts)
            else:
                statuses = self.tweets_user(
                    screen_name=screen_name,
                    since_id=since_id,
                    max_id=last_ids[len(last_ids)-1],
                    count=str(count-len(litweets)),
                    exclude_replies=exclude_replies,
                    include_rts=include_rts)

            for s in range(len(statuses)):
                stat = statuses[s]
                stat_txt = stat['text']
                stat_id = stat['id_str']
                if len(stat_txt) > 0:
                    if stat not in litweets:
                        litweets.append(stat)
                        if s == len(statuses)-1:
                            last_ids.append(stat_id)

            lastobtained = len(litweets)-lenstart
            lenlastobtained.append(
                lastobtained
            )

            if lastobtained == 0:
                # If no new tweet added last time,
                # Give the API a rest a bit
                time.sleep(0.5)

            if np.sum(
                # Check the last three scrapes,
                # if all three are zero, end the scrape process.
                lenlastobtained[len(
                    lenlastobtained)-3:len(
                        lenlastobtained)]) == 0:
                print(
                    "Approaching limit, ending the scrape at {} tweets".format(
                        len(litweets)
                    ))
                break

        return litweets[0:count]

    def getprecisenumtweetstext(self,
                                screen_name,
                                since_id: str = None,
                                max_id: str = None,
                                count: int = 10,
                                exclude_replies: bool = False,
                                include_rts: bool = False) -> list:
        """Scrape the tweets from user if they have a public profile. Will try
        to return the exact number of the tweets asked. Will return only the
        text of the statuses.

        Args:
            screen_name (str): The twitter username of the user.
            since_id (str, optional): The twitter status ID of the earliest tweet
            that you'd like to scrape. Defaults to None.
            max_id (str, optional): The twitter status ID of the latest tweet that
            you'd like to scrape. Defaults to None.
            count (int, optional): The number of twitter statuses that you'd like
            to scrape. The final number isn't always exactly the same as
            the count requested. Defaults to 10.
            exclude_replies (bool, optional): Option to exclude tweet replies
            from the scraped statuses. Defaults to False.
            include_rts (bool, optional): Option to include retweets from the
            scraped statuses. Defaults to False.

        Returns:
            list: An array containing strings, each of them are the text for
                the scraped statuses.
        """

        # Make sure the limit does not surpass 3000
        if count > 2000:
            count = 2000

        litweets = [
            tweet['text'] for tweet in self.getprecisenumtweets(
            screen_name=screen_name,
            since_id=since_id,
            max_id=max_id,
            count=count,
            exclude_replies=exclude_replies,
            include_rts=include_rts)
        ]

        return litweets
