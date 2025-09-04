from scrapper.scrapper_funcs import *

def Scrap():

    news_list = []
    counter = 0
    url = "https://www.larazon.es/"

    news_list = getNewsList(url)

    while news_list!=[]:

        for item in news_list:
            
            if item:
                try:
                    noticia = extract_news_data(item["url"])
                except Exception as e:
                    #print("NEWS LIST: ", e, item["url"])
                    pass
                if noticia != 0:
                    if url in str(noticia["url"]):
                        
                        if ExistingNewsCheck(noticia) == False:

                            n = Noticia(
                                noticia["title"][0],
                                noticia["url"],
                                noticia["id"],
                                noticia["source"],
                                noticia["authors"],
                                noticia["publish_date"],
                                noticia["description"],
                                noticia["body"],
                                noticia["tags"],
                                noticia["entities"]
                                )

                            if n:
                                writeJson(n)
                                counter +=1
                                print(f"\nNoticia Recopilada {counter}:\n\n {n.titulo}\n\n")
                            else:
                                print("Error al recopilar")
                                pass
                        else:
                            #print(f"Noticia repetida: \n\n{item["url"]}\n\n")
                            pass
                else:
                    #print(f"Noticia no válida: \n\n{item["url"]}\n\n")
                    pass

                news_list.remove(item)
                print(f"    Quedan {len(news_list)} noticias por analizar.")
            else:
                print("empty List")
                pass
    




