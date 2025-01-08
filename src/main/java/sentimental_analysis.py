import os
import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from html.parser import HTMLParser
import re
import html
import pdfplumber
from io import BytesIO

print("Script started")

parser = HTMLParser()

issuer_data = {}

for page in range(1, 40):
    payload = {
        "issuerId": 0,     # Ако нема, ги зема сите
        "languageId": 2,
        "channelId": 1,
        "dateFrom": "2024-07-30T00:00:00",
        "dateTo": "2024-12-20T23:59:59",
        "isPushRequest": False,
        "page": page
    }
    headers = {
        "Content-Type": "application/json",
    }

    url = "https://api.seinet.com.mk/public/documents"
    response = requests.post(url, json=payload, headers=headers)
    json_data = response.json()

    print(f"PROCESSING PAGE: {page}")
    print("")

    for document in json_data['data']:
        issuer_code = document['issuer']['code']
        display_name = document['issuer']['localizedTerms'][0]['displayName']
        extracted_text = ""
        content_text = ""

        if 'content' in document:
            content_text = html.unescape(document['content'])
            content_text = re.sub(r'<[^>]*>', '', content_text)
        else:
            print("Key 'content' not found in document.")
            continue

        auto_generated_phrases = [
            "this is automaticaly generated document".lower(),
            "ова е автоматски генериран документ".lower()  # Македонска верзија
        ]
        if any(phrase in content_text.lower() for phrase in auto_generated_phrases):
            print("The content is automatically generated.")
            continue

        attachments = document.get('attachments', [])

        if attachments:
            attachment_id = attachments[0].get('attachmentId')
            file_name = attachments[0].get('fileName')

            if file_name.lower().endswith('.pdf'):
                attachment_url = "https://api.seinet.com.mk/public/documents/attachment/" + str(attachment_id)
                response = requests.get(attachment_url)

                if response.status_code == 200:
                    pdf_file = BytesIO(response.content)

                    with pdfplumber.open(pdf_file) as pdf:
                        for page in pdf.pages:
                            extracted_text += page.extract_text()

        if issuer_code not in issuer_data:
            issuer_data[issuer_code] = {
                "display_name": display_name,
                "content": content_text,
                "text": extracted_text
            }
        else:
            issuer_data[issuer_code]["content"] += "\n" + content_text
            issuer_data[issuer_code]["text"] += "\n" + extracted_text

csv_file_path = "merged_issuer_data_with_content.csv"
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Issuer Code", "Display Name", "Content", "Extracted Text"])

    for issuer_code, data in issuer_data.items():
        csv_writer.writerow([issuer_code, data["display_name"], data["content"], data["text"]])

print(f"Data successfully saved to {csv_file_path}")





import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

data = pd.read_csv("merged_issuer_data_with_content.csv")

data['Combined Text'] = data['Content'] + " " + data['Extracted Text']

def clean_text(text):
    if not isinstance(text, str):
        return ''
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum() and word not in stop_words]
    return ' '.join(tokens)

data['Cleaned Text'] = data['Combined Text'].apply(clean_text)



data['Sentiment'] = data['Cleaned Text'].apply(lambda x: 'Positive' if 'profit' in x or 'growth' in x else 'Negative')

data['Label'] = data['Sentiment'].map({'Positive': 1, 'Negative': 0})

X = data['Cleaned Text']
y = data['Label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)

from sklearn.metrics import classification_report
report = classification_report(y_test, y_pred)

with open("classification_report.txt", "w") as file:
    file.write(report)


data['Recommendation'] = data['Sentiment'].apply(lambda x: 'Buy' if x == 'Positive' else 'Sell')


output_data = data[['Issuer Code', 'Display Name', 'Sentiment', 'Label', 'Recommendation']]

output_data.to_csv("recommendationsFinal.csv", index=False, encoding='utf-8')

print("Script finished")