import requests
from bs4 import BeautifulSoup
import argparse
import pandas as pd

URL_PAGE_Style = 'https://www.vagalume.com.br/browse/style/samba.html'

def getAllArtistsURLPage(URL_PAGE_Style):
    r = requests.get(URL_PAGE_Style)
    soup = BeautifulSoup(r.content, "html.parser")
    listnamesColumn = soup.findAll("ul", {"class": "namesColumn"})
    listArtistNames = [ul.findAll("li") for ul in listnamesColumn]
    divs_a = [li.findAll("a") for li in listArtistNames[0]]
    href_list = []
    for a_list in divs_a:
        for a in a_list:
            href_list.append("https://www.vagalume.com.br" + a.get("href"))
    return href_list

def getAllMusicURLPage(list_url_artists):
    list_url_musics = []
    for url in list_url_artists:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        r.close()
        lettermusic = soup.findAll("a", {"class": "nameMusic"})
        lettermusic_href = list(set([a.get("href") for a in lettermusic]))
        list_url_musics += lettermusic_href
    return list_url_musics

def getSongName(lyricContent):
    return lyricContent.find("h1").text

def getArtistName(lyricContent):
    return lyricContent.find("h2").text

def getComposer(lyricContent):
    composer = lyricContent.find("small", {"class": "styleDesc"})
    if composer != None:
        return composer.text[len("Compositor:"):]
    else:
        return "no compositor found"

def separateParagraphs(lyric):
    text = ''
    for letter in lyric:
        if letter.isupper():
            text += ' ' + letter
        else:
            text += letter

    return text

def getLyric(lyricContent):
    lyric_div = lyricContent.find("div", {"id": "lyrics"})
    text = separateParagraphs(lyric_div.text)
    return text

def getLyricContents(list_url_musics):
    data = []
    n = 1
    for url in list_url_musics:
        print("Getting lyric content of: %s" %url)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        r.close()
        lyricContent = soup.find("div", {"id": "lyricContent"})
        dic = {"musica": getSongName(lyricContent),
              "artista": getArtistName(lyricContent),
              "compositor": getComposer(lyricContent),
              "letra": getLyric(lyricContent)}
        data.append(dic)
        if n == 5:
            break
        n += 1

    return data



if __name__=="__main__":
    # parser for arguments passed by command line
    parser = argparse.ArgumentParser(
                description='Webscreper to extract all the songs of a musical style on the Vagalume website.')

    parser.add_argument('-url', '--url_style_page', type=str, default='https://www.vagalume.com.br/browse/style/samba.html',
                        help='Ex: https://www.vagalume.com.br/browse/style/pop-rock.html')

    args = parser.parse_args()
    print("Getting artists names.")
    url_pages = getAllArtistsURLPage(URL_PAGE_Style=args.url_style_page)
    print("%d artists found." %len(url_pages))
    print("Gettings the songs of each artist.")
    list_url_musics = getAllMusicURLPage(list_url_artists=url_pages)
    list_url_musics = list(set(list_url_musics)) # remove duplicate ones
    print("%d musics found." %len(list_url_musics))
    list_url_musics = ["https://www.vagalume.com.br" + url for url in list_url_musics]
    data = getLyricContents(list_url_musics)
    df = pd.DataFrame(data=data, columns=['musica', 'artista', 'compositor', 'letra'])
    csv_name =   args.url_style_page.split("/")[-1].split(".")[0] + "-dataset.csv"# get style name
    df.to_csv("data/" + csv_name, sep="|", index=False)
