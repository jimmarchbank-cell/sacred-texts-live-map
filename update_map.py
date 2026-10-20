"""Copy only the public aggregate map; fail closed if the form changes."""
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime, timezone

FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfzPykCkzt4u48eR-HNB-rg8wsEqY5O31-r6VOnSAiTaUETzg/viewform"

class MapParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.matches = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        label = a.get("alt", "")
        if tag == "img" and all(word in label for word in ("youth", "hours", "states", "countries", "faith traditions")):
            self.matches.append(a.get("src", ""))

def fetch(url, limit):
    with urlopen(Request(url, headers={"User-Agent": "SacredTextsMapPublisher/1.0"}), timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Source exceeds size limit")
    return data

def main():
    parser = MapParser()
    parser.feed(fetch(FORM, 2_000_000).decode("utf-8"))
    if len(parser.matches) != 1:
        raise ValueError("Expected exactly one aggregate map; retaining previous deployment")
    url = parser.matches[0]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "docs.google.com" or not parsed.path.startswith("/forms-images-rt/"):
        raise ValueError("Unexpected image source")
    try:
        raw = fetch(url, 10_000_000)
    except HTTPError as error:
        # Forms sometimes redirects with an invalid full-frame crop suffix.
        # Request the same public image at the same width without that crop.
        target = urlparse(error.url)
        suffix = "-fcrop64=1,00000000FFFFFFFF"
        if error.code != 400 or target.scheme != "https" or not (target.hostname or "").endswith(".googleusercontent.com") or not error.url.endswith(suffix):
            raise
        raw = fetch(error.url[:-len(suffix)], 10_000_000)
    with Image.open(BytesIO(raw)) as img:
        if img.size != (740, 511):
            raise ValueError(f"Unexpected map dimensions: {img.size}")
        img.load()
        out = Path("public")
        out.mkdir(exist_ok=True)
        image = img.convert("RGB")
        # This public image is published daily. Keep its caption correct even
        # while the source forms are rolling over to the new shared artwork.
        label = Image.new("RGB", (260, 32), (237, 247, 251))
        draw = ImageDraw.Draw(label)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        text = "UPDATED DAILY"
        box = draw.textbbox((0, 0), text, font=font)
        draw.text(((260 - (box[2] - box[0])) / 2, 4 - box[1]), text,
                  font=font, fill=(0, 128, 74))
        image.paste(label.resize((65, 8), Image.Resampling.LANCZOS), (128, 462))
        image.save(out / "heat-map.png")
    (out / "updated.json").write_text(json.dumps({"copied_at": datetime.now(timezone.utc).isoformat(), "source": FORM}) + "\n")
    (out / "index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sacred Texts Worldwide Participation Map</title><img src="heat-map.png" alt="Sacred Texts Worldwide participation map" style="max-width:100%;height:auto"></html>\n')
    print("Validated and copied public map (740 x 511).")

if __name__ == "__main__":
    main()
