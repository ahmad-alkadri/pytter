from pytterrator import Client

# Initiate client
client = Client()

arrtweets = client.getprecisenumtweetstext(
        "jack",
        count=12000,
        exclude_replies=True,
        include_rts=False
    )
print(arrtweets)
print(len(arrtweets))
