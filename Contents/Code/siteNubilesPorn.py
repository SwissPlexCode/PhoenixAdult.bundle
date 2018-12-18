import PAsearchSites
import PAgenres
'''
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchSiteName = PAsearchSites.getSearchSiteName(searchSiteID)
    searchResults = HTML.ElementFromURL('https://www.nubileporn.net/?s=' + encodedTitle)
    for searchResult in searchResults.xpath('//article'):
        titleNoFormatting = searchResult.xpath('.//div[@class="row"]//div[@class="col-lg-6 col-md-6 col-sm-6 col-xs-12"]//div[@class="entry-header"]//h2[@class="entry-title h2"]//a')[0].text_content()
        Log("Result Title: " + titleNoFormatting)
        nubilesSite = searchResult.xpath('.//div[@class="row"]//div[@class="col-lg-6 col-md-6 col-sm-6 col-xs-12"]//div[@class="entry-header"]//span[@class="entry-category"]//a')[0].text_content().strip()
        curID = searchResult.xpath('.//div[@class="row"]//div[@class="col-lg-6 col-md-6 col-sm-6 col-xs-12"]//div[@class="entry-header"]//h2[@class="entry-title h2"]//a')[0].get('href').replace('/','_')
        Log("ID: " + curID)
        releasedDate = searchResult.xpath('.//div[@class="row"]//div[@class="col-lg-6 col-md-6 col-sm-6 col-xs-12"]//div[@class="entry-header"]//div[@class="entry-meta"]//div//span')[0].text_content()

        Log("CurID" + str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        
        titleNoFormatting = titleNoFormatting + " [" + releasedDate +"]"
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results
'''

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    url = 'https://nubiles-porn.com/video/watch/' + searchTitle.lower().replace(" ","-")
    searchResults = HTML.ElementFromURL(url)

    searchResult = searchResults.xpath('//div[@class="descrips"]')[0]
    titleNoFormatting = searchResult.xpath('.//div[@class="row"]//div[@class="col-lg-12 watchpage-details-titlerow"]//span[@class="wp-title videotitle"]')[0].text_content()
    Log("Result Title: " + titleNoFormatting)
    cur = 'https://nubiles-porn.com/video/watch/' + searchTitle.lower().replace(" ","-")
    curID = cur.replace('/','_')
    Log("ID: " + curID)
    releasedDate = searchResult.xpath('.//div[@class="row"]')[1].xpath('.//div[@class="col-lg-6 col-sm-6"]//span')[0].text_content()

    girlName = searchResult.xpath('.//div[@class="row"]')[1].xpath('.//div[@class="col-lg-6 col-sm-6"]//span[@class="featuring-modelname model"]//a')[0].text_content()

    Log("CurID" + str(curID))
    lowerResultTitle = str(titleNoFormatting).lower()

    titleNoFormatting = girlName + " - " + titleNoFormatting + " [Nubiles, " + releasedDate +"]"
    score = 100
    results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results

def update(metadata, siteID, movieGenres):
    temp = str(metadata.id).split("|")[0].replace('_', '/')

    url = temp
    Log('url :' + url)
    detailsPageElements = HTML.ElementFromURL(url)

    metadata.studio = "Nubiles"

    # Summary
    paragraph = detailsPageElements.xpath('//div[@class="video-description"]//article//p')[0].text_content()
    # paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n', '').replace('  ', '') + "\n\n"
    metadata.summary = paragraph[:-10]
    tagline = detailsPageElements.xpath('//a[contains(@href, "website")]')[0].text_content().replace(".com","")
    metadata.collections.clear()
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.title = detailsPageElements.xpath('//span[@class="wp-title videotitle"]')[0].text_content()

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//a[contains(@class,"wptag")]')

    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().lower()
            movieGenres.addGenre(genreName)

    # Actors
    metadata.roles.clear()
    titleActors = ""
    actors = detailsPageElements.xpath('//span[@class="featuring-modelname model"]//a[contains(@href, "model")]')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()

            actorPageURL = 'https://nubiles-porn.com' + actorLink.get("href")
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorName = actorPage.xpath('//div[@class="col-lg-4 col-sm-4 model-profile-desc"]//h2')[0].text_content().strip()
            titleActors = titleActors + actorName + " & "
            role.name = actorName
            actorPhotoURL = "https:" + actorPage.xpath('//div[@id="modelprofile"]//img')[0].get("src")
            role.photo = actorPhotoURL
        titleActors = titleActors[:-3]
        metadata.title = metadata.title


    # Posters
    background = "https:" + detailsPageElements.xpath('//div[@class="video-player"]//img')[0].get('src')
    Log("BG DL: " + background)
    metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    metadata.posters[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

    return metadata
