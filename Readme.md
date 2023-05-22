
# OpenAI Web QA

This is a project to build a question answering application that can crawl a given site, create knowledgebase on the crawled data, generates embeddings and then using openai api, answer questions like Chat-GPT about that custom website.   

## Install Dependencies
First thing you need to do is to install required packages. Run the following command from terminal 

```
pip install -r requirements.txt
```
It will isntall required packages in your environment

## OpenAI API Key
Second thing you need to do is to create a ```.env``` file in same folder with main.py file. Inside the file, keep your openai api key as follows
```
OPEN_AI_API_KEY = "your api key here"
```
## Set the url and domain url
One last thing to is to set the url and domain of the website that you want to crawl. In ```main.py``` file, update "domain" and "full_url" variable according to your website. 

## Run the application
Now you are good to go! Just run the main.py file from terminal. It will ask you for a question. Ask the question it will generate answer based on the data from the website. Note that, for the first time when you run the app, it will crawl the website to collect knowledgebase and create embedding. This may take some time based on the website. 