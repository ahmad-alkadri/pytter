from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from .constants import *
import requests
from urllib.parse import urlencode
import re
import time
import numpy as np


class Client:
    def __init__(self, checkbearer=False):
        """
        This is a Python function that initializes headers for making requests with a bearer token and a
        guest token.
        
        @param checkbearer A boolean parameter that determines whether to check for a bearer token or use a
        constant bearer token.
        """
        uagent = UserAgent()
        chosenbrowser = uagent.random

        if checkbearer:
            user_agent = {"User-Agent": bearerbrowser, "Referer": url_referer}
            r = requests.get(url_base, headers=user_agent)
            soup = BeautifulSoup(r.text, "html.parser")
            js_with_bearer = ""
            for i in soup.find_all("link"):
                if i.get("href").find("/main") != -1:
                    js_with_bearer = i.get("href")

            # Get Bearer token
            user_agent = {"User-Agent": chosenbrowser, "Referer": url_referer}

            if len(js_with_bearer) > 1:
                r = requests.get(js_with_bearer, headers=user_agent)
            bearer = re.findall(r'",[a-z]="(.*)",[a-z]="\d{8}"', r.text, re.IGNORECASE)[
                0
            ].split('"')[-1]
        else:
            bearer = bearerconst

        hdrs_guest = {"authorization": f"Bearer {bearer}", "User-Agent": chosenbrowser}

        guest_token = requests.post(endpoint_guesttoken, headers=hdrs_guest).json()[
            "guest_token"
        ]

        self.headers = {
            "authorization": f"Bearer {bearer}",
            "x-guest-token": guest_token,
            "User-Agent": chosenbrowser,
        }

    def prepparams(self, pardicts: dict = {}) -> dict:
        """
        The function prepparams takes a dictionary as input and returns a new dictionary with non-None
        values.
        
        @param pardicts A dictionary containing parameter names and their values.
        
        @return The function `prepparams` returns a dictionary `paramsprep` that contains only the key-value
        pairs from the input dictionary `pardicts` where the value is not `None`.
        """
        paramsprep = {}
        for ke in pardicts.keys():
            if pardicts[ke] != None:
                paramsprep[ke] = pardicts[ke]

        return paramsprep

    def status_ratelimit(self, resources: str = None) -> dict:
        """
        This function retrieves the rate limit status for a specified endpoint and returns it as a
        dictionary.
        
        @param resources The "resources" parameter is a string that specifies the type of resources for
        which the rate limit status is being requested. It can take the following values:
        
        @return a dictionary containing information about the rate limit status for the specified resources.
        The information includes the remaining number of requests that can be made, the total number of
        requests allowed, and the time when the rate limit will reset.
        """
        uro = endpoint_ratelimit
        urf = uro + "?" + urlencode(self.prepparams({"resources": resources}))
        response = requests.get(urf, headers=self.headers).json()
        return response

    def tweets_user(
        self,
        screen_name: str,
        since_id: str = None,
        max_id: str = None,
        count: int = 10,
        exclude_replies: bool = False,
        include_rts: bool = False,
    ) -> list:
        """
        This function retrieves tweets from a specific user's timeline with various optional parameters.
        
        @param screen_name The Twitter screen name of the user whose tweets are being requested.
        @param since_id This parameter is used to retrieve tweets with an ID greater than (i.e., more recent
        than) the specified ID. It is optional and defaults to None.
        @param max_id The max_id parameter is used to specify the maximum tweet ID to retrieve. This
        parameter is used for pagination purposes, allowing you to retrieve older tweets beyond the initial
        count limit. Only tweets with an ID less than or equal to the specified max_id will be returned.
        @param count The number of tweets to retrieve per request. The default value is 10.
        @param exclude_replies A boolean parameter that determines whether to exclude replies from the
        returned tweets. If set to True, only original tweets will be returned. If set to False, both
        original tweets and replies will be returned.
        @param include_rts A boolean parameter that determines whether to include retweets in the response.
        If set to True, retweets will be included. If set to False, only original tweets will be included.
        
        @return The function `tweets_user` returns a list of tweets from a specific user's timeline, based
        on the provided parameters such as screen name, since_id, max_id, count, exclude_replies, and
        include_rts. The tweets are returned in JSON format.
        """

        uro = endpoint_tweetuser
        queries = urlencode(
            self.prepparams(
                {
                    "screen_name": screen_name,
                    "since_id": since_id,
                    "count": int(float(count)),
                    "max_id": max_id,
                    "include_rts": (str(include_rts)).lower(),
                    "exclude_replies": (str(exclude_replies)).lower(),
                }
            )
        )

        urf = uro + "?" + queries

        while True:
            response = requests.get(urf, headers=self.headers)
            # If status code is not 403, break the loop
            if response.status_code != 403:
                break
            # Regenerate the token
            print("Regenerating guest token...")
            self.__init__()

        return response.json()

    def getprecisenumtweets(
        self,
        screen_name,
        since_id: str = None,
        max_id: str = None,
        count: int = 10,
        exclude_replies: bool = False,
        include_rts: bool = False,
        limit_singlereq: int = 10,
    ) -> list:
        """
        This function retrieves a specified number of tweets from a given user's timeline, with options
        to filter by parameters such as since_id, max_id, and exclude_replies.
        
        @param screen_name The Twitter screen name of the user whose tweets are being retrieved.
        @param since_id The ID of the earliest tweet to retrieve. Only tweets after this ID will be
        returned. Defaults to None, meaning all tweets will be retrieved.
        @param max_id `max_id` is the maximum tweet ID to retrieve. This parameter is used to retrieve
        tweets that have a lower ID than the specified ID. It is often used for pagination, where the
        first request retrieves the most recent tweets and subsequent requests retrieve older tweets.
        @param count The number of tweets to retrieve.
        @param exclude_replies exclude_replies is a boolean parameter that determines whether to exclude
        replies from the results or not. If set to True, only tweets that are not replies will be
        returned. If set to False, all tweets (including replies) will be returned.
        @param include_rts A boolean parameter that determines whether or not to include retweets in the
        results. If set to True, retweets will be included. If set to False, only original tweets will
        be included.
        @param limit_singlereq The limit_singlereq parameter is the maximum number of tweets to retrieve
        in a single request to the Twitter API.
        
        @return a list of tweets (up to a specified count) from a given Twitter user's timeline, with
        optional filters for since_id, max_id, exclude_replies, and include_rts. The function uses a
        loop to scrape tweets in batches of a specified limit_singlereq, and stops when the desired
        count is reached or when there are no new tweets obtained in the
        """

        litweets = []
        last_ids = []
        lenlastobtained = []

        targetcount = count

        while len(litweets) < targetcount:
            lenstart = len(litweets)
            if len(last_ids) == 0:
                statuses = self.tweets_user(
                    screen_name=screen_name,
                    since_id=since_id,
                    max_id=max_id,
                    count=str(limit_singlereq),
                    exclude_replies=exclude_replies,
                    include_rts=include_rts,
                )
            else:
                statuses = self.tweets_user(
                    screen_name=screen_name,
                    since_id=since_id,
                    max_id=last_ids[len(last_ids) - 1],
                    count=str(limit_singlereq),
                    exclude_replies=exclude_replies,
                    include_rts=include_rts,
                )

            for s in range(len(statuses)):
                stat = statuses[s]
                stat_txt = stat["text"]
                stat_id = stat["id_str"]
                if len(stat_txt) > 0:
                    if stat not in litweets:
                        litweets.append(stat)
                        if s == len(statuses) - 1:
                            last_ids.append(stat_id)

            lastobtained = len(litweets) - lenstart
            lenlastobtained.append(lastobtained)

            if lastobtained == 0:
                # If no new tweet added last time,
                # Give the API a rest a bit
                time.sleep(0.5)

            if (
                np.sum(
                    # Check the last three scrapes,
                    # if all three are zero, end the scrape process.
                    lenlastobtained[len(lenlastobtained) - 3 : len(lenlastobtained)]
                )
                == 0
            ):
                print(
                    "Approaching limit, ending the scrape at {} tweets".format(
                        len(litweets)
                    )
                )
                break

        return litweets[0:count]

    def getprecisenumtweetstext(
        self,
        screen_name,
        since_id: str = None,
        max_id: str = None,
        count: int = 10,
        exclude_replies: bool = False,
        include_rts: bool = False,
        limit_singlereq: int = 10,
    ) -> list:
        """
        This function retrieves a specified number of tweets' text from a Twitter user's timeline.
        
        @param screen_name The Twitter screen name of the user whose tweets are being retrieved.
        @param since_id This parameter specifies the oldest tweet ID that should be returned. Only tweets
        with an ID greater than (that is, more recent than) the specified ID will be returned.
        @param max_id max_id is the maximum tweet ID to retrieve. This parameter is used to paginate through
        results when there are more tweets than the count parameter can retrieve in a single request. Only
        tweets with an ID less than (that is, older than) the specified max_id will be returned.
        @param count The number of tweets to retrieve. It has a default value of 10 and can be set to a
        maximum of 1000.
        @param exclude_replies A boolean parameter that determines whether to exclude replies from the
        returned tweets. If set to True, only tweets that are not replies will be returned. If set to False,
        all tweets (including replies) will be returned.
        @param include_rts A boolean parameter that determines whether or not to include retweets in the
        results. If set to True, retweets will be included. If set to False, only original tweets will be
        included.
        @param limit_singlereq The limit_singlereq parameter is used to specify the maximum number of tweets
        to retrieve in a single request. This is useful for limiting the amount of data retrieved at once
        and avoiding rate limits imposed by the Twitter API. The default value is 10, but it can be adjusted
        based on
        
        @return a list of text from a specified number of tweets (determined by the `count` parameter) from
        a given Twitter user's timeline, with optional filters for excluding replies and including retweets.
        The list is obtained by calling the `getprecisenumtweets()` function and extracting the "text" field
        from each tweet.
        """

        # Make sure the limit does not surpass 1000
        if count > 1000:
            count = 1000

        litweets = [
            tweet["text"]
            for tweet in self.getprecisenumtweets(
                screen_name=screen_name,
                since_id=since_id,
                max_id=max_id,
                count=count,
                exclude_replies=exclude_replies,
                include_rts=include_rts,
                limit_singlereq=limit_singlereq,
            )
        ]

        return litweets
