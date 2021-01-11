from datetime import date

from config import ARCHIVE_URL
from TSUrl import TSUrl
import extractor.archive_extractor
import extractor.tsShow_extractor


def scrapeTSShows(
    airDate: date,
    extractors = {"subtitleUrl": extractor.tsShow_extractor.subtitle_url_extractor}
):
    archive = TSUrl(ARCHIVE_URL.format(yyyymmdd=airDate.isoformat().replace("-", "")))
    # Make sure the archive is the correct one
    # As archive at air Date < minAirDate are forwarded to archive at minAirDate
    if extractor.archive_extractor.archive_date_extractor(archive.soup) != airDate:
        raise AttributeError("No archive for airdate, maybe to old?")
    tsShows = extractor.archive_extractor.tsShow_extractor(archive.soup)

    # Always necessary as some archive entries are wrong
    extractors["air_date"] = extractor.tsShow_extractor.air_date_extractor

    data = {}
    for tsShow in tsShows:
        for extractor_name, extractor_function in extractors.items():
            try:
                data[extractor_name] = extractor_function(tsShow.soup)
            except AttributeError:
                data[extractor_name] = None
    return data

