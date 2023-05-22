import os
import pandas as pd


class CrawledDataProcessor:
    def __init__(self, domain, full_url):
        self.domain = domain
        self.full_url = full_url
        self.texts = []

    @staticmethod
    def remove_newlines(serie):
        serie = serie.str.replace('\n', ' ')
        serie = serie.str.replace('\\n', ' ')
        serie = serie.str.replace('  ', ' ')
        serie = serie.str.replace('  ', ' ')
        return serie

    def process(self):
        # Create a directory to store the csv files
        if not os.path.exists("processed"):
            os.mkdir("processed")

        # Get all the text files in the text directory
        for file in os.listdir("text/" + self.domain + "/"):
            # Open the file and read the text
            with open("text/" + self.domain + "/" + file, "r", encoding="UTF-8") as f:
                text = f.read()

                # Omit the first 11 lines and the last 4 lines, then replace -, _, and #update with spaces.
                self.texts.append((file[11:-4].replace('-', ' ').replace('_', ' ').replace('#update', ''), text))

        # Create a dataframe from the list of texts
        df = pd.DataFrame(self.texts, columns=['fname', 'text'])
        # Set the text column to be the raw text with the newlines removed
        df['text'] = df.fname + ". " + CrawledDataProcessor.remove_newlines(df.text)
        df.to_csv('processed/scraped.csv')
