# Pytterrator

## Introduction

A simple Python module to obtain tweets from users at
[twitter](https://twitter.com) without having to have
twitter developer's account. This is achieved by using
twitter's own v1.1 API and leveraging the guest token,
thus making the client appears as if they are simply
a user who does not log in. This would benefit us for
simple tweets scraping for individual users; however
because of the rate limit it would not work for
large-scale data scraping.

Currently under heavy development. If you have any
questions, don't hesitate to raise them as Issues.

## Installation

To get started using this module, simply use
`pip` to install it directly from this repo:

```bash
pip install git+https://github.com/ahmad-alkadri/pytterrator
```

This would install the latest update of the Python package,
specifically from the `master` branch.

## Example usage

Let's say we want to get the last 1000 tweets made by
@jack (basically this guy created Twitter), we can simply
type the following lines on python:

```python
from pytterrator import Client

# Initiate client
client = Client()

arrtweets = client.getprecisenumtweetstext(
        "jack",
        count=1000,
        exclude_replies=False,
        include_rts=False
    )
print(arrtweets)
```

and it'll print down all the 1000 last tweets of his.
You can choose to exclude replies or include RTs
(retweets) as you wish.

## Notes and Warnings

The scraping process itself is quite simple and involves,
simply, an iterating process (hence the name, *pytterrator*),
which is the module would keep making the API request and
accumulate the number of tweets until they reach the
requested number. A single API request of tweets
to Twitter's v1.1 API usually will return about 100 tweets.
So, if you're asking for 500 tweets, expect the module
to iterate 5–6 times until you obtain the requested number
of tweets.

Finally, a hard limit is imposed on the number of tweets that
you can scrape (2000) because of the rate limit.
Also, depending on how often you use this module,
the rate could change accordingly. To prevent your app
from depleting the whole rate limit, this module
will cut the scraping process if it sees the API is
approaching its rate limit (usually when it sees
the returned number of tweets approaching zero).
