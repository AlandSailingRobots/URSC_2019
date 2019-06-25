from sys import argv
import gps
import requests

# Listen on port 2947 of gpsd
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True:
    rep = session.next()
    if (rep["class"] == "TPV"):
        print((rep.lat), (rep.lon))

    else:
        print("")


