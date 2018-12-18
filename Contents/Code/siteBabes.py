import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchSiteName = PAsearchSites.getSearchSiteName(searchSiteID)
    searchResults = HTML.ElementFromURL('https://www.babesnetwork.com/tour/search/all/keyword/' + encodedTitle)
    for searchResult in searchResults.xpath('//li[@class="release-wrapper type-video scene"]'):
        titleNoFormatting = searchResult.xpath('.//div[@class="release-information"]//div[@class="clearfix"]//h3[@class="release-title"]//a')[0].text_content().strip()
        Log("Result Title: " + titleNoFormatting)
        babesSite = searchResult.xpath('.//div[@class="release-information"]//div[@class="clearfix"]')[1].xpath('.//a')[0].text_content().strip()
        Log("^Babes Site: " + babesSite)
        Log("^searchSiteName: " + searchSiteName)
        curID = searchResult.xpath('.//a')[0].get('href').replace('/','_')
        Log("ID: " + curID)
        releasedDate = searchResult.xpath('.//div[@class="release-information"]//div[@class="clearfix"]//time[@class="release-date"]')[0].text_content()

        girlName = searchResult.xpath('.//div[@class="model-names clearfix"]//a')[0].text_content()

        Log("CurID" + str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        
        titleNoFormatting = girlName + " - " + titleNoFormatting + " [" + babesSite + ", " + releasedDate +"]"
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results


def update(metadata, siteID, movieGenres):
    temp = str(metadata.id).split("|")[0].replace('_', '/')

    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    Log('url :' + url)
    detailsPageElements = HTML.ElementFromURL(url)

    metadata.studio = "Babes"

    # Summary
    paragraph = detailsPageElements.xpath('//p[@class="section-detail section-detail--description"]')[0].text_content().strip()
    # paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n', '').replace('  ', '') + "\n\n"
    metadata.summary = paragraph[:-10]
    tagline = detailsPageElements.xpath('//a[@class="video-bar__release-site"]')[0].text_content().strip()
    metadata.collections.clear()
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.title = detailsPageElements.xpath('//div[@class="video-info__container center clearfix"]//h1')[0].text_content()

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//p[contains(@class,"section-detail--tags")]//a')

    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().lower()
            movieGenres.addGenre(genreName)

    # Actors
    metadata.roles.clear()
    titleActors = ""
    actors = detailsPageElements.xpath('//h2[@class="video-bar__models"]//a[contains(@class, "model-name")]')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()

            actorPageURL = 'https://www.babesnetwork.com' + actorLink.get("href")
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorName = actorPage.xpath('//div[@class="title-bar"]//h2')[0].text_content()
            titleActors = titleActors + actorName + " & "
            role.name = actorName
            actorPhotoURL = "https:" + actorPage.xpath('//img[@class="profile-picture"]')[0].get("src")
            role.photo = actorPhotoURL
        titleActors = titleActors[:-3]
        metadata.title = metadata.title


    # Posters

    background = "https://static-hw.babescontent.com/scenes/" + detailsPageElements.xpath('//input[@id="sceneid"]')[0].get('value') + "/s970x545.jpg"
    Log("BG DL: " + background)
    metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    metadata.posters[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

    return metadata
