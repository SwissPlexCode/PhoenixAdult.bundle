import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchSiteName = PAsearchSites.getSearchSiteName(searchSiteID)
    searchResults = HTML.ElementFromURL('https://www.mofos.com/tour/search/?q=' + encodedTitle)
    for searchResult in searchResults.xpath('//div[@class="widget-release-card"]'):
        titleNoFormatting = searchResult.xpath('.//div[@class="title details-only"]//h3//a')[0].text_content()
        Log("Result Title: " + titleNoFormatting)
        mofosSite = searchResult.xpath('.//div[@class="release-info"]//a[@class="site-name"]')[0].text_content().strip()
        Log("^Mofos Site: " + mofosSite)
        Log("^searchSiteName: " + searchSiteName)
        curID = searchResult.xpath('.//a')[0].get('href').replace('/','_')
        Log("ID: " + curID)
        releasedDate = searchResult.xpath('.//div[@class="release-info"]//div[@class="views-date-box"]//span[@class="date-added"]')[0].text_content()

        girlName = searchResult.xpath('.//div[@class="girls-site-box"]//var[@class="girls-name"]//a')[0].get('title')

        Log("CurID" + str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        
        titleNoFormatting = girlName + " -" + titleNoFormatting + " [" + mofosSite + ", " + releasedDate +"]"
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results


def update(metadata, siteID, movieGenres):
    temp = str(metadata.id).split("|")[0].replace('_', '/')

    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    Log('url :' + url)
    detailsPageElements = HTML.ElementFromURL(url)

    metadata.studio = "Mofos"

    # Summary
    paragraph = detailsPageElements.xpath('//p[@class="desc"]')[0].text_content()
    # paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n', '').replace('  ', '') + "\n\n"
    metadata.summary = paragraph[:-10]
    tagline = detailsPageElements.xpath('//a[@class="site-name"]')[0].text_content().strip()
    metadata.collections.clear()
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.title = detailsPageElements.xpath('//h1[@class="title"]')[0].text_content()

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//div[contains(@class,"categories")]//a')

    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().lower()
            movieGenres.addGenre(genreName)

    # Actors
    metadata.roles.clear()
    titleActors = ""
    actors = detailsPageElements.xpath('//a[@class="model-name"]')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()

            actorPageURL = 'https://www.mofos.com' + actorLink.get("href")
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorName = actorPage.xpath('//div[@class="h1"]')[0].text_content()
            titleActors = titleActors + actorName + " & "
            role.name = actorName
            actorPhotoURL = "https:" + actorPage.xpath('//img[@class="model-pic"]')[0].get("src")
            role.photo = actorPhotoURL
        titleActors = titleActors[:-3]
        metadata.title = metadata.title


    # Posters

    background = "https:" + detailsPageElements.xpath('//*[@id="trailer-player"]/img')[0].get('src')
    Log("BG DL: " + background)
    posterURL = background[:-5]
    Log("Poster: " + posterURL)
    for i in range(1, 6):
        metadata.art[posterURL + str(i) + ".jpg"] = Proxy.Preview(HTTP.Request(posterURL + str(i) + ".jpg", headers={'Referer': 'http://www.google.com'}).content, sort_order = 6-i)
        metadata.posters[posterURL + str(i) + ".jpg"] = Proxy.Preview(HTTP.Request(posterURL + str(i) + ".jpg", headers={'Referer': 'http://www.google.com'}).content, sort_order = i)

    return metadata
