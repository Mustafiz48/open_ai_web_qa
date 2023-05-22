import pandas as pd
import tiktoken
import openai
import numpy as np
import matplotlib.pyplot as plt


class EmbeddingGenerator:
    def __init__(self):
        # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.df = pd.read_csv('processed/scraped.csv', index_col=0)
        self.embedding_df = None
        self.max_tokens = 500

    # def visualize_token(self):
    #     self.df.columns = ['title', 'text']
    #     # Tokenize the text and save the number of tokens to a new column
    #     self.df['n_tokens'] = self.df.text.apply(lambda x: len(self.tokenizer.encode(x)))
    #
    #     # Visualize the distribution of the number of tokens per row using a histogram
    #     plt.hist(self.df.n_tokens)
    #     plt.show()
    #     # plt.plot(df.n_tokens.hist())

    # Function to split the text into chunks of a maximum number of tokens
    def split_into_many(self, text, max_tokens):
        # Split the text into sentences
        sentences = text.split('. ')

        # Get the number of tokens for each sentence
        n_tokens = [len(self.tokenizer.encode(" " + sentence)) for sentence in sentences]

        chunks = []
        tokens_so_far = 0
        chunk = []

        # Loop through the sentences and tokens joined together in a tuple
        for sentence, token in zip(sentences, n_tokens):

            # If the number of tokens so far plus the number of tokens in the current sentence is greater
            # than the max number of tokens, then add the chunk to the list of chunks and reset
            # the chunk and tokens so far
            if tokens_so_far + token > max_tokens:
                chunks.append(". ".join(chunk) + ".")
                chunk = []
                tokens_so_far = 0

            # If the number of tokens in the current sentence is greater than the max number of
            # tokens, go to the next sentence
            if token > max_tokens:
                continue

            # Otherwise, add the sentence to the chunk and add the number of tokens to the total
            chunk.append(sentence)
            tokens_so_far += token + 1

        # Add the last chunk to the list of chunks
        if chunk:
            chunks.append(". ".join(chunk) + ".")

        return chunks

    def shorten(self):
        self.df.columns = ['title', 'text']
        # Tokenize the text and save the number of tokens to a new column
        self.df['n_tokens'] = self.df.text.apply(lambda x: len(self.tokenizer.encode(x)))

        shortened = []
        # Loop through the dataframe
        for row in self.df.iterrows():

            # If the text is None, go to the next row
            if row[1]['text'] is None:
                continue

            # If the number of tokens is greater than the max number of tokens, split the text into chunks
            if row[1]['n_tokens'] > self.max_tokens:
                shortened += self.split_into_many(row[1]['text'], max_tokens=self.max_tokens)

            # Otherwise, add the text to the list of shortened texts
            else:
                shortened.append(row[1]['text'])

        self.embedding_df = pd.DataFrame(shortened, columns=['text'])
        self.embedding_df['n_tokens'] = self.embedding_df.text.apply(lambda x: len(self.tokenizer.encode(x)))
        plt.hist(self.embedding_df.n_tokens)
        plt.show()

    def generate_embedding(self):
        # Note that you may run into rate limit issues depending on how many files you try to embed
        # Please check out our rate limit guide to learn more on how to handle this: https://platform.openai.com/docs/guides/rate-limits

        self.shorten()
        self.embedding_df['embeddings'] = self.embedding_df.text.apply(
            lambda x: openai.Embedding.create(input=x, engine='text-embedding-ada-002')['data'][0]['embedding'])
        self.embedding_df.to_csv('processed/embeddings.csv')
        # print(self.embedding_df.head())
