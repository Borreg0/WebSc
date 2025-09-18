import requests,re,json,os
from bs4 import BeautifulSoup
from scrapper.noticia import Noticia


def createRequest(url_diario:str) -> BeautifulSoup:
    """ Recoge todo el texto de la pagina """

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    }
    try:
        response = requests.get(url_diario, headers=headers, timeout=10)
    
        text = response.text
        soup = BeautifulSoup(text,'html.parser')

        return soup
        
    except:
        return []
    
def getNewsList(url) -> list:
    """ Crea una lista con todos los enlaces de noticias de la pagina """
    news = []
    try:
        soup = createRequest(url)
        if soup !=[]:
            titulares = soup.find_all('h2', class_='article__title small')

            for titular in titulares:
                enlace = titular.find("a")
                if enlace:
                    url = enlace.get("href")
                    titulo = enlace.get_text(strip=True)
                    
                    news.append({
                    'titulo': titulo,
                    'url': url
                    })
            return news
        else:
            return []
    except:
        print("Error en getNewList func")
        return []

def generalInfo(data:BeautifulSoup) -> list:
    if data != []:
        #title
        try:
            if len(data.find_all('title'))>1: #puede capturar uno o varios elementos, así no da error de índice
                heading = data.find_all('title')[0]
            else:
                heading = data.find_all('title')
        except Exception:
            pass
        #author
        try:
            author = data.select(".article-author__name a")[0]
        except IndexError:
            try:
                author = data.select(".article-author__name span")[0]
            except:
                try:
                    author = data.select(".article-author__name div")[0]
                except:
                    author = ["UNK"]         
        except:
            author["Different error in author"]
            print(f"--------Error in--------- \n\n {heading}\n\n")

        tags = data.select('.tags-list__link')
        try:
            dates = data.select(".article-dates__detail time")[0]
        except IndexError:
            try:
                dates = data.select(".article-dates__detail time")
            except:
                dates = []
        try:
            
            articleDescription_tag = data.find('meta', attrs={'name':'description'})
            if type(articleDescription_tag) == None:
                articleDescription_tag = data.find("h2", class_="article-main__description")
                articleDescription = articleDescription_tag.get_text()
            else:
                articleDescription = articleDescription_tag.get('content')

            articleID_tag = data.find('meta', attrs={'name': 'articleId'})
            articleID = articleID_tag.get('content')
            diary_tag = data.find('meta', attrs={'name':'organization'})
            diary = diary_tag.get('content')
        except Exception as ex:
            template = "GeneralInfo: An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            #print(message)
            pass
        try:
            headings_list = [x.text for x in heading]
        except UnboundLocalError:
            headings_list = [0]
        try: 
            authors_list = [x.text for x in author]
        except AttributeError:
            authors_list = author

        tags_list = [x.text for x in tags]
        dates_list = [x.text for x in dates]
        try:
            articleID_list = articleID
        except:
            articleID_list = [0]
        articleDescription_list = [articleDescription]
        try:
            diary_list = diary
        except:
            diary_list = [0]

        return [headings_list,articleDescription_list,authors_list,tags_list,dates_list,diary_list,articleID_list]
    else:
        return []

def mainContent(data:BeautifulSoup):
    if data != []:
        #eliminar imagenes, publicidad y noticias relacionadas
        for img in data.find_all(['img','picture']):
            img.extract()
        for relnews in data.find_all(['div','li'], class_=['related-news','related-news-item','wrapper-related-news']):
            relnews.extract()
        for ad in data.find_all(['aside', 'div'], class_=['advertising', 'ad-banner']):
            ad.extract()    
        for mc in data.select('.article-main__content'):
            mainContent = mc.get_text()
        try:
            return mainContent
        except:
            return "0"
        
    else:
        return 0

def extract_entities(maincontent):
    if maincontent != 0:
        ogrganizations_patrones = [
            # Entidades con estructura: Palabra + (preposición/artículo) + Palabra + "y" + Palabra
            r"\b[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]{3,}+\s(?:de|del|la|el|los|las)?\s?[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+\s(?:y|e)\s[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+\b",
            
            # Entidades con preposiciones/artículos en medio (mínimo 3 palabras)
            r"\b(?:[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]{3,}+\s)+(?:de|del|la|el|los|las|a|al|por|para|con|en)\s(?:[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+\s)*[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+\b",
            
            # Entidades compuestas sin preposiciones (2+ palabras con mayúsculas)
            r"\b(?:[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]{3,}+\s){1,3}[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+\b",

            r'\b([A-Z]{2,})\b'
        ]

        organizations = []
        for p in ogrganizations_patrones:
            organizations.extend(re.findall(p, maincontent))

        return list(set(organizations))
    else:
        return 0
    
def extract_news_data(url):
    try:    
        soup = createRequest(url)
        generalinformation = generalInfo(soup)
        maincontent = mainContent(soup)
        entities = extract_entities(maincontent)

        if generalinformation != []:
            #Construir estructura final
            news_data = {
                "title": generalinformation[0],
                "url": url,
                "id":generalinformation[6],
                "source": generalinformation[5],
                "authors": generalinformation[2],
                "publish_date": generalinformation[4],
                "description": generalinformation[1],
                "body": maincontent,
                "tags": generalinformation[3],
                "entities": entities
            }

            return news_data
        else:
            return 0
    except requests.exceptions.ConnectionError as e:
        print(f" Límite alcanzado: {e}\n\n Reiniciando")
    
def ExistingNewsCheck(noticia:dict) -> bool:
    
    news = [fullID(n) for n in os.listdir("scrapper/data")]
    current_new = fullID(noticia)

    for n in news:
        if current_new in news:
            return True
        else:
            return False
    else:
        return False

def fullID(noticia) -> str:
    if type(noticia) == dict:
        punto = len(noticia["url"]) - 1 - noticia["url"][::-1].index(".")
        guionBajo = len(noticia["url"]) - 1 - noticia["url"][::-1].index("_")
        return str(noticia["url"][guionBajo:punto])
    elif type(noticia) == Noticia:
        punto = len(noticia.url) - 1 - noticia.url[::-1].index(".")
        guionBajo = len(noticia.url) - 1 - noticia.url[::-1].index("_")
        return str(noticia.url[guionBajo:punto])
    else: #type string
        punto = noticia.rfind(".")
        guionBajo = noticia.rfind("_")
        return noticia[guionBajo:punto]

def writeJson(noticia:Noticia) -> None:
    with open(f"scrapper/data/noticia{fullID(noticia.url)}.json","w+", encoding="utf-8") as f:
        f.write(json.dumps(noticia.to_dict(), indent=2, ensure_ascii=False))    
    f.close()




