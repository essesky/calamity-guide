import json
import urllib.parse
import urllib.request

titles = ["Monstrous_Knives", "Auric_Tesla_armor", "Desert_Scourge", "Bandit"]
params = {
    "action": "query", "format": "json", "prop": "revisions",
    "rvprop": "content", "rvslots": "main", "titles": "|".join(titles),
}
url = "https://calamitymod.wiki.gg/api.php?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={"User-Agent": "CalamityGuideBuilder/1.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.load(r)
for p in data["query"]["pages"].values():
    content = p["revisions"][0]["slots"]["main"]["*"]
    print("=" * 20, p["title"], "len", len(content))
    print(content[:2600])
