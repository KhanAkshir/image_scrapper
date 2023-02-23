import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        try:
            query = request.form['content'].replace(" ","")

            # directory to store downloaded images
            save_dir = "images/"

            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # fake user agent to avoid getting blocked by Google
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            response = requests.get(
                f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")

            soup = BeautifulSoup(response.content, "html.parser")

            image_tags = soup.find_all("img")
            del image_tags[0]

            # img data = []

            web_i=[]
            img_data=[]
            for index,image_tag in enumerate(image_tags):                    
                # get the image source URL
                image_url = image_tag['src']       
                web_i.append(image_url)                         
                #print(image_url)
                # send a request to the image URL and save the image
                image_data = requests.get(image_url).content
                mydict={"Index":index,"Image":image_data}
                img_data.append(mydict)
                with open(os.path.join(save_dir, f"{query}_{image_tags.index(image_tag)}.jpg"), "wb") as f:
                    f.write(image_data)
            client = pymongo.MongoClient("mongodb+srv://Akshir:<password>@cluster0.yinu3eg.mongodb.net/?retryWrites=true&w=majority")
            db = client["Image_Scrapper"]
            img_coll=db["VSCODE"]            
            img_coll.insert_many(img_data)

            return render_template('result.html', reviews=web_i[0:(len(web_i)-1)])
            # return "image laoded"
        except Exception as e:
            logging.info(e)                    
            return 'something is wrong'

        



if __name__ == "__main__":
    app.run(host="0.0.0.0")
