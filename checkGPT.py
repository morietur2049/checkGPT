import requests
import time
import json
import openai
import sys
import os
import re
import sys
import io


# Read API_KEY and organization from keys.txt
with open('keys.txt', 'r') as file:
    lines = file.readlines()
    openai.organization = lines[0].strip()
    API_KEY = lines[1].strip()

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"



def remove_unicode_chars(text):
    return re.sub(r'\\u[a-zA-Z0-9]{4}', '', text)

def count_words(text):
    # Supprimer la ponctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Diviser le texte en mots et compter le nombre de mots
    words = text.split()
    return len(words)

def read_file(filename):
    with open(filename, 'r',encoding="utf-8") as file:
        return file.read().strip()

def read_text_to_analyse(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        line = line.replace(' .', '.')
        line = line.replace(' ,', ',')
        line = remove_unicode_chars(line)
        processed_lines.append(line.strip())
    return processed_lines



# query GTP4

def query_gpt4(prompt,temperature=1.1,max_tokens=None):
    messages=[{"role": "user", "content": prompt}]
    openai.api_key = API_KEY
    sys.stderr.write ("querying gpt")
    try:
        response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=max_tokens,
        temperature=temperature,
        messages = messages)
        sys.stderr.write ("answer from gpt")
        return (True,response["choices"][0]["message"]["content"])
        time.sleep(10)   
    except Exception as e:
        sys.stderr.write(f"####### error = {e}")
        return (False,"")   


def query_gpt3(messages, model="gpt-3.5-turbo-0301", temperature=0.1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    try:
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return (True,response.json()["choices"][0]["message"]["content"])
        else:
            return (False,"")

    except:
        return (False,"")

def is_no_error(text):
    sys.stderr.write ("entering is_no_error()")
    errors = ["Le texte ne contient pas d'erreur factuelle","Il n'y a pas d'erreur factuelle dans le texte", "aucune erreur", "Il n'y a pas d'erreur factuelle","il n'y a pas d'erreur"]
    for error in errors:
        if error.lower() in text.lower():
            return True 
    return False


def main():
 
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-16')

    if len(sys.argv) != 4:
        sys.stderr.write(f"Usage: {sys.argv[0]} <text_file> <prompt_file> <model>")
        return

    text_file = sys.argv[1]
    prompt_file = sys.argv[2]
    model = sys.argv[3]

    paragraphs = read_text_to_analyse(text_file)
    i=0
    for paragraph in paragraphs:
        text=paragraph
        sys.stderr.write (f"analysing {text}")        
        l = count_words(text)
        if (l < 10):
            continue
        i=i+1
        sys.stderr.write (f"checking paragraph {i}")
        prompt = read_file(prompt_file)

        result=False
        sys.stderr.write(f" ==> {i}")
        while result == False:
            if model == "gpt3":
                messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}######{text}"} ]
                (result,response) = query_gpt3(messages)
            if model == "gpt4":
                (result,response) = query_gpt4(f"{prompt}######{text}")
            if (result == False):
                sys.stderr.write (f"error or overload: waiting 60 seconds")
                time.sleep(60)
        if is_no_error(response):
            continue
        
        print ("")
        sys.stderr.write ("")
        sys.stderr.write (f"=>{text}")    
        sys.stderr.write (f"{i} =======> {response}")
        print (f"=>{text}")    
        print (f"{i} =======> {response}")
        print ("")
        

if __name__ == "__main__":
    main()
