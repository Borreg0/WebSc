import os, re, json, es_core_news_sm
from textwrap import wrap
from collections import Counter
from multiprocessing import Pool
from nltk.util import ngrams

def OpenAndGroup(ruta,tipoArchivo):
    """Groups all names of raw data for further processing"""
    
    if tipoArchivo == '.json':
        grouped = [texto for texto in os.listdir(ruta) if texto.endswith(tipoArchivo)] #lista de nombres de los json :str
        return grouped
    elif tipoArchivo == '.txt':
        grouped = [texto for texto in os.listdir(ruta) if texto.endswith(tipoArchivo) and texto.startswith("temp")] #lista de nombres de los json :str
        return grouped

def chunkFiles(files:list,n_chunks:int):
    """Chunks given list in n-parts"""

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
    """Merges all texts in single plain text file"""

    tokens = []
    counter = 0

    #Deletes tokenized.txt if exists
    for i in os.listdir(rutaTemp):
        if i.startswith('tokenized'):
            os.remove(fr"tokenized/tokenized.txt")

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

    #removes temp files
    for n,i in enumerate(os.listdir(rutaTemp)):
        try:
            os.remove(fr"tokenized/temp{n}.txt")
        except:
            pass

def grammarFix(value:str):
    """Adds spaces in these contexts:
    aE -> a E
    a?E -> a? E
    .¿ -> . ¿
    .A -> . A
    """
    value = re.sub(r'(?<=[a-z])(?=[A-Z])', ". ", value)
    value = re.sub(r'\?(?=[A-Z])', '? ', value)
    value = re.sub(r'\.(?=¿)', '. ', value)
    value = re.sub(r'(?<!\b[A-Z])\.(?=[A-Z])', '. ', value)

    return value

def genTokens():
    """Creates the tokens file in json"""

    with open(os.path.join(r"tokenized/tokenized.txt"), "r", encoding="utf-8") as f:
        content = f.read()
        tokens = content.split(" ")
    with open(os.path.join(r"tokenized/tokens.json"), "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False)
        
def tokenize(raw_text:str):
    """Tokenizes plain string into words"""

    raw_text = re.sub(r'([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])', r'\1 \2', raw_text).lower()
    raw_text = re.sub(r'[\.,:\"\'}{&%$@=;\\\/#-_¿?¡!()]', " ", raw_text)
    tokens = re.findall(r'\b[\w\'-]+\b', raw_text.replace('\ufeff', ''), re.UNICODE)
    return tokens

def TagWords():
    """Using Spacy Spanish Tagger loads plain text file, splits it in n-parts of fixed length and tags them"""

    print(f"Tagging... \n\n")
    with open("tokenized/tokenized.txt","r",encoding="utf-8") as f:
        tokens = f.read()

    tokens = splitTextForTagging(tokens)
    #Load tagger and apply to every splitted part
    nlp = es_core_news_sm.load()
    alltagged = []
    for t in tokens:
        doc = nlp(t)
        alltagged.extend([(word.text, word.pos_) for word in doc])
        # Merge all tuples in single list
    with open("tagged_data/tagged_words.json", "w", encoding="utf-8") as f:
        print(f"Writing in file... \n\n")
        json.dump(alltagged, f, ensure_ascii=False)   

def splitTextForTagging(text:str) -> list[str]:
    """Splits a given string in parts of n-lenght for less memory usage"""

    return wrap(text,100000)

def countFreq():
    """Creates a dict with all frequencies: {'agotadora_ADJ': 3}"""

    with open("tagged_data/tagged_words.json","r",encoding="utf-8") as f:
        taggedwords = json.load(f) 
        f.close()

    tokenTags = Counter()
    for word, tag in taggedwords:
        tokenTags[word+"_"+ tag] += 1
    
    with open("freqs/frequencies.json","w+", encoding="utf-8") as f:
        json.dump(tokenTags, f, ensure_ascii=False)
        f.close()

def makeBigrams():
    """WIP"""
    with open("tokenized/tokens.json","r",encoding="UTF-8") as f:
        tokenized = json.load(f)
        f.close()
    bigrams = ngrams(tokenized,2,pad_left=True, pad_right=True, left_pad_symbol='<s>', right_pad_symbol='</s>')

    print(list(bigrams))

def extractSentences():
    """Extracts the sentences from raw files contained in a folder"""
    ruta = r"scrapper/data"
    files = OpenAndGroup(ruta,".json")
    nlp = es_core_news_sm.load()

    allSentences = []

    #removes sents.json if exists
    for i in os.listdir("tokenized/"):
        if i.startswith('sents.json'):
            os.remove(fr"tokenized/sents.json")

    #iterates every news to write its sentences
    for file in files:
        with open(ruta+"/"+file,"r",encoding="UTF-8") as f:
            news:dict = json.load(f)
            for key in news.keys():
                if key in ["titulo", "entradilla", "cuerpo"]:
                    rawValue = news[key]
                    if isinstance(rawValue, str):
                        value = grammarFix(str(rawValue))
                        text = nlp(value)
                        allSentences.extend([str(sent).strip() for sent in text.sents])    
                    elif isinstance(rawValue, list) and rawValue:
                        for item in rawValue:
                            if isinstance(item, str):
                                value = grammarFix(item)
                                text = nlp(value[0])
                                allSentences.extend([str(sent).strip() for sent in text.sents])
                    else:
                        pass  
    with open("tokenized/sents.json", "w+", encoding="utf-8") as f:
        json.dump(allSentences, f, ensure_ascii=False)              

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