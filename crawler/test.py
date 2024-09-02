import httpx
import pprint

res = httpx.get("https://v6.vbb.transport.rest/stops/900001151/departures?duration=20")
pprint.pprint(res.json())
