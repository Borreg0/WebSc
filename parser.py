from parser_funcs import *
from scrapper.scrap import Scrap
from parser_funcs import TagWords
from multiprocessing import Pool
import time

def main():

    stime = time.time()
    if not os.path.isdir("scrapper/data"):
        os.makedirs("scrapper/data")
    #scraps the web
    Scrap()
    print("\n"+"-"*40+"\n", "PROCESSING FILES")

    # agrupa todas las noticias raw
    rutaOpenGroup = r"scrapper/data"
    files = OpenAndGroup(rutaOpenGroup,'.json')
    n = 128
    partes = chunkFiles(files,n) 
    """lista de listas de nombres de documentos json list[list[str]]"""
    
    fileLen = (checkLengthFile(rutaOpenGroup,files))

    # hacemos N=partes documentos temporales para ir agrupando los cuerpos de las noticias
    with Pool(12) as p:
        rutaData = r"scrapper/data"
        for n, parte in enumerate(partes, start=1):
            print(f"CHUNK {n}")
            p.apply(singleFile, args=(parte, rutaData,n))
    
    os.system('cls')
    print("-"*40+"\n", "WRITING TOKENS")
    #tokenizar y escribir
    rutaTemp = r"tokenized\\"
    
    #elimina si ya existia un archivo tokenized.txt
    for i in os.listdir(rutaTemp):
        if i.startswith('tokenized'):
            os.remove(fr"tokenized/tokenized.txt")

    #lista de archivos temporales a procesar
    filesToProcess = OpenAndGroup(rutaTemp,'.txt')
    #generar achivo tokenized.txt
    generateTokenizedPlainFile(filesToProcess,rutaTemp)
    #generar archivo tokens.txt
    genTokens()
    
    os.system('cls')
    #comprobar la longitud de tokens.json
    with open(r"tokenized/tokens.json","r",encoding = "utf-8") as f:
        file = json.load(f)
        print(f"Tokenized len: {len(file)} / Tokens len: {fileLen}")
    print(f"\n\n\n   Tiempo total: {(time.time()-stime)/60} minutos")

    os.system('cls')
    print("\n"+"-"*40+"\n", "TAGGING")
    try:
        with Pool(12) as p:
            p.apply_async(TagWords)
    except Exception as e:
        print("TAGGING FAILED: ", e)

    # print(f"\n\n\n   Tiempo total: {(time.time()-stime)/60} minutos")
    # print("\n"+"-"*40+"\n", "COUNTING FREQS")
    # with multiprocessing.Pool(processes=6) as pool:
    #     pool.apply(countFreq)

    print(f"\n\n\nFINALIZADO: Tiempo total: {(time.time()-stime)/60} minutos")
    





if __name__ == "__main__":
    main()




