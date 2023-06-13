from pytterrator import Client

# Initiate client
client = Client()

arrtweets = client.getprecisenumtweetstext(
        "elonmusk",
        count=141,
        exclude_replies=True,
        include_rts=False,
        limit_singlereq=20,
    )
print(arrtweets)
print(len(arrtweets))
