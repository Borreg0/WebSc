import os, re, json, es_core_news_sm
from collections import Counter,defaultdict
from multiprocessing import Process,Queue, Pool
from nltk.util import ngrams

def OpenAndGroup(ruta,tipoArchivo):
    """agrupa en una lista los nombres de los archivos de un directorio"""
    
    if tipoArchivo == '.json':
        grouped = [texto for texto in os.listdir(ruta) if texto.endswith(tipoArchivo)] #lista de nombres de los json :str
        return grouped
    elif tipoArchivo == '.txt':
        grouped = [texto for texto in os.listdir(ruta) if texto.endswith(tipoArchivo) and texto.startswith("temp")] #lista de nombres de los json :str
        return grouped

def chunkFiles(files:list,n_chunks:int):
    
    lenFiles= len(files)
    base_size = lenFiles // n_chunks  #elementos enteros
    remainder = lenFiles % n_chunks   #resto elementos

    return [
        files[i * base_size + min(i, remainder) : (i + 1) * base_size + min(i + 1, remainder)] 
        for i in range(n_chunks)
    ]

def singleFile(partes,ruta,n):

    string = str()
    # partesLen = len(partes)
    for noticia_nombre in partes:
        ruta_archivo = os.path.join(ruta, noticia_nombre)
        with open(ruta_archivo,"r",encoding="UTF-8") as f:
            noticiaCompleta:dict = json.load(f)
            #añade a la lista de tokens los tokens de cada noticia
            for i in noticiaCompleta.keys():
                tipo = type(noticiaCompleta[i])
                if i in ["titulo", "entradilla", "cuerpo"]:
                    if tipo == str:
                        string += noticiaCompleta[i]
                    elif tipo == list:
                        string += "".join(noticiaCompleta[i][0])
                else:
                    pass    
    with open(f"tokenized/temp{n}.txt","+a",encoding="utf-8") as f:
        f.write(string)

def writeTokenFile(temp_file):
    rutaTemp = r"tokenized/"
    print(f"Processing {temp_file}")
    with open(os.path.join(rutaTemp, temp_file), "r", encoding="utf-8") as f:
        content = f.read()
        return tokenize(content)

def generateTokenizedPlainFile(filesToProcess,rutaTemp):

    tokens = []
    counter = 0

    with Pool(12) as p:
        results = p.map(writeTokenFile, filesToProcess)
    
    for result in results:
        tokens.extend(result)
        counter += 1
        
        if counter % 3 == 0: #counter en mod3 como búfer
            with open(os.path.join(rutaTemp, "tokenized.txt"), "a", encoding="utf-8") as f:
                for t in tokens:
                    f.write(t + " ")
                tokens = []
    if tokens:
        with open(os.path.join(rutaTemp, "tokenized.txt"), "a", encoding="utf-8") as f:
            for t in tokens:
                f.write(t + " ")

    #eliminar archivos temporales
    for n,i in enumerate(os.listdir(rutaTemp),start=1):
        if i.startswith('temp'):
            os.remove(fr"tokenized/temp{n}.txt")

def genTokens():
    with open(os.path.join(r"tokenized/tokenized.txt"), "r", encoding="utf-8") as f:
        content = f.read()
        tokens = content.split(" ")
    with open(os.path.join(r"tokenized/tokens.json"), "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False)
        
def tokenize(raw_text:str):

    raw_text = re.sub(r'([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])', r'\1 \2', raw_text).lower()
    raw_text = re.sub(r'[\.,:\"\'}{&%$@=;\\\/#-_¿?¡!()]', " ", raw_text)
    tokens = re.findall(r'\b[\w\'-]+\b', raw_text.replace('\ufeff', ''), re.UNICODE)
    return tokens

def TagWords():
    print(f"Writing... \n\n")
    with open("tokenized/tokenized.txt","r",encoding="utf-8") as f:
        tokens = f.read() #list
    print(f"Writing... \n\n")    
    nlp = es_core_news_sm.load()
    print(f"Writing... \n\n")
    doc = nlp(tokens)
    tagged = [(word.text, word.pos_) for word in doc]
    print(f"Writing... \n\n")
    with open("tagged_data/tagged_words.json", "w", encoding="utf-8") as f:
        print(f"Writing... \n\n")
        json.dump(tagged, f, ensure_ascii=False)   

def countFreq():

    with open("tagged_data/tagged_words.json","r",encoding="utf-8") as f:
        taggedwords = json.load(f) #conversión del archivo en lista: ['agotadora', 'ADJ']
        f.close()
    with open("tokenized/tokens.json","r", encoding="utf-8") as f:
        tokens = json.load(f) #lista de tokens
        f.close()

    tokenTags = defaultdict(Counter)
    for token in tokens:
        for w in taggedwords:
            if token == w[0]:
                tag = w[1]
                tokenTags[token][tag] +=1
    
    with open("freqs/frequencies.json","w+", encoding="utf-8") as f:
        json.dump(tokenTags, f, ensure_ascii=False)
        f.close()

def makeBigrams():
        pass    

def checkLengthFile(ruta,partes):
    counter = 0
    # partesLen = len(partes)
    for noticia_nombre in partes:
        ruta_archivo = os.path.join(ruta, noticia_nombre)
        with open(ruta_archivo,"r",encoding="UTF-8") as f:
            noticiaCompleta:dict = json.load(f)
            #añade a la lista de tokens los tokens de cada noticia
            for i in noticiaCompleta.keys():
                tipo = type(noticiaCompleta[i])
                if i in ["titulo", "entradilla", "cuerpo"]:
                    if tipo == str:
                        counter += len(tokenize(noticiaCompleta[i]))
                    elif tipo == list:
                        counter += len(tokenize("".join(noticiaCompleta[i][0])))
                else:
                    pass    
    return counter