from datetime import date, datetime
import requests
from bs4 import BeautifulSoup
import json


BASE_URL = "https://www.tagesschau.de"
RELATIVE_ARCHIVE_URL_AS_FORMAT_STRING = "/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"


class TSUrl():
  """A class modeling a url of tagesschau.de that is requestable and soupable"""
  def __init__(self, url):
    """Init works for relative and absolute URLs"""
    if "http" not in url:
      slash = "/" if url[0] != "/" else ""
      url = BASE_URL + slash + url
    self.url = url
    self._get_request_response = None
    self._soup = None

  @property
  def get_request_response(self):
    if not self._get_request_response:
      self._get_request_response = requests.get(self.url)
    return self._get_request_response
  
  @property
  def soup(self):
    if not self._soup:
      self._soup = BeautifulSoup(self.get_request_response.content, features="html.parser")
    return self._soup

  @property
  def json(self):
    return self.get_request_response.json()

  def __repr__(self):
    return self.url

class TSShow():
  """A class modeling a tagesschau show. Url can be relative or absolute, request response and soup are lazy inits"""
  def __init__(self, url: TSUrl):
    self.url = url
    self._video_url = None
    self._air_date = None
    self._subtitle_url = None
    self._topics = None

  @property
  def video_url(self):
    if not self._video_url:
      iframe_data = self.url.soup.find("iframe")["data-ctrl-iframe"]
      iframe_data_dict = json.loads(iframe_data.replace("'", "\""))
      self._video_url = TSUrl(iframe_data_dict["action"]["default"]["src"].split("~")[0])
    return self._video_url

  @property
  def air_date(self):
    """Returns tagesschaus upload date. This is metadata in the tagesschau site, and not the actual upload date but the broadcasting date"""
    upload_date = self.url.soup.find("meta", {"itemprop": "uploadDate"})
    return datetime.strptime(upload_date["content"], "%a %b %d %H:%M:%S %Z %Y")

  @property
  def subtitle(self):
    if not self._subtitle_url:
      metadata_url = TSUrl(self.video_url.url + "~mediajson_broadcastType-TS.json")
      self._subtitle_url = TSUrl(metadata_url.json.get("_subtitleUrl"))
    return self._subtitle_url

  @property
  def topics(self):
    if not self._topics:
      teasers = self.url.soup.find_all("p", {"class": "teasertext"})
      topics = None
      for teaser in teasers:
        if "Themen der Sendung" in teaser.text:
          self._topics = teaser.text
          break
    return self._topics

  def __repr__(self):
    return str(self.url)

class ArchiveCrawler():
  """Contains utility to crawl TSUrls for tagesschau shows from tagesschau.de's video archive"""

  def _archive_url_for_date(d: date):
    """Creates url to tageschau.de video archive at specific date"""
    return TSUrl(BASE_URL + RELATIVE_ARCHIVE_URL_AS_FORMAT_STRING.format(yyyymmdd=d.isoformat().replace("-", "")))

  def tagesschau_show_urls_for_date(d: date):
    """Crawls the tageschau.de video archive for tagesschau show TSUrl at specific date"""
    # Tagesschau url scheme changes over time ("sendung[number].html", "ts[number].html", "ts-[number.html]"
    # Identifying by title instead
    ts_urls = ArchiveCrawler._archive_url_for_date(d).soup.find_all("a", text="tagesschau")
    return [TSUrl(url["href"]) for url in ts_urls]

def main():
  # Crawl specific date for TSShows
  for show_url in ArchiveCrawler.tagesschau_show_urls_for_date(date.today()):
    show = TSShow(show_url)
    print(show)
    # Retrieve data
    print(show.video_url)
    print(show.air_date)
    print(show.subtitle)
    print(show.topics)

if __name__ == "__main__":
  main()
