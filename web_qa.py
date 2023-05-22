import os.path
from dotenv import load_dotenv
import os
import pandas as pd
import openai
import numpy as np
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity

from EmbeddingGenerator import EmbeddingGenerator
from WebCrawler import WebCrawler
from CrawledDataProcessor import CrawledDataProcessor


load_dotenv()
open_ai_api_key = os.getenv("OPEN_AI_API_KEY")
openai.api_key = open_ai_api_key

HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'


class WebQA:
    def __init__(self, domain, full_url):
        # Define root domain to crawl
        self.domain = domain  # "responsive-bootstrap-pandacommerce.netlify.app"
        self.full_url = full_url  # "https://responsive-bootstrap-pandacommerce.netlify.app/"

    def crawl_website(self):
        WebCrawler.crawl(self.full_url)
        crawled_data_processor = CrawledDataProcessor(self.domain, self.full_url)
        crawled_data_processor.process()

    def generate_embedding(self):
        embedding_generator = EmbeddingGenerator()
        embedding_generator.generate_embedding()

    def create_context(self, question, df, max_len=1800, size="ada"):
        """
        Create a context for a question by finding the most similar context from the dataframe
        """

        # Get the embeddings for the question
        q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

        # Get the distances from the embeddings
        df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')

        returns = []
        cur_len = 0

        # Sort by distance and add the text to the context until the context is too long
        for i, row in df.sort_values('distances', ascending=True).iterrows():

            # Add the length of the text to the current length
            cur_len += row['n_tokens'] + 4

            # If the context is too long, break
            if cur_len > max_len:
                break

            # Else add it to the text that is being returned
            returns.append(row["text"])

        # Return the context
        return "\n\n###\n\n".join(returns)

    def answer_question(
            self,
            model="text-davinci-003",
            question="Am I allowed to publish model outputs to Twitter, without a human review?",
            max_len=1800,
            size="ada",
            debug=False,
            max_tokens=150,
            stop_sequence=None
    ):

        if not os.path.exists("processed/embeddings.csv"):
            print("Started Crawling website, please wait...")
            self.crawl_website()
            print("Web crawling complete! Please wait while we are generating embeddings")
            self.generate_embedding()
        else:
            print("Existing Embeddings found! Using the found embedding")
        df = pd.read_csv('processed/embeddings.csv', index_col=0)
        df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)
        df.head()

        """
        Answer a question based on the most similar context from the dataframe texts
        """
        context = self.create_context(question, df, max_len=max_len, size=size, )

        # If debug is true, print the raw model response
        if debug:
            print("Context:\n" + context)
            print("\n\n")

        try:
            # Create a completions using the questin and context
            response = openai.Completion.create(
                prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop_sequence,
                model=model,
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(e)
            return ""
