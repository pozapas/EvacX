#EvacX bot

# Import necessary libraries
import tweepy
import feedparser
import requests
import random
import json
from datetime import datetime
import spacy
import re
from PIL import Image
import os
import html

# Twitter API credentials
api_key = 'XXX'
api_key_secret = 'XXX'
access_token = 'XXX'
access_token_secret = 'XXX'
client_id = 'XXX'
client_secret = 'XXX'
bearer_token = 'XXX'

# Stable Diffusion API key
STABILITY_KEY = 'XXX'

# Elsevier API key
elsevier_api_key = 'XXX'

# Groq API key
groq_api_key = "XXX"

# Groq model ID
groq_model_id = "gemma-7b-it"

# Setup Tweepy Client authentication
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_key_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Setup Tweepy API v1.1 authentication (needed for media upload)
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# RSS feed URLs for the journals
rss_feeds = {
    "Safety Science": "https://rss.sciencedirect.com/publication/science/09257535",
    "Fire Technology": "https://rssproxy.migor.org/api/w2f?v=0.1&url=https%3A%2F%2Flink.springer.com%2Fjournal%2F10694%2Farticles&link=.%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fh3%5B1%5D%2Fa%5B1%5D&context=%2F%2Fdiv%5B3%5D%2Fdiv%5B2%5D%2Fmain%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fsection%5B1%5D%2Fol%5B1%5D%2Fli&re=metadata&out=atom",
    "Fire Safety Journal": "https://rss.sciencedirect.com/publication/science/03797112",
    "Physica A": "https://rss.sciencedirect.com/publication/science/03784371",
    "Automation in Construction": "https://rss.sciencedirect.com/publication/science/09265805",
    "International Journal of Disaster Risk Reduction" : "https://rss.sciencedirect.com/publication/science/22124209",
    "Advanced Engineering Informatics" : "https://rss.sciencedirect.com/publication/science/14740346",
    "Transportation Research Part A" : "https://rss.sciencedirect.com/publication/science/09658564",
    "Transportation Research Part B" : "https://rss.sciencedirect.com/publication/science/01912615",
    "Transportation Research Part C" : "https://rss.sciencedirect.com/publication/science/0968090X",
    "Transportation Research Part D" : "https://rss.sciencedirect.com/publication/science/13619209",
    "Transportation Research Part E" : "https://rss.sciencedirect.com/publication/science/13665545",
    "Transportation Research Part F" : "https://rss.sciencedirect.com/publication/science/13698478",
    "Environmental Hazards" : "https://www.tandfonline.com/feed/rss/tenh20",
    "Transportation Planning and Technology" : "https://www.tandfonline.com/feed/rss/gtpt20",
    "Tunnelling and Underground Space Technology" : "https://rss.sciencedirect.com/publication/science/08867798",
    "Developments in the Built Environment" : "https://rss.sciencedirect.com/publication/science/26661659",
    "Journal of Transport Geography" : "https://rss.sciencedirect.com/publication/science/09666923",
    "Journal of Building Engineering" : "https://rss.sciencedirect.com/publication/science/23527102",
    "Reliability Engineering & System Safety" : "https://rss.sciencedirect.com/publication/science/09518320",
    "Heliyon": "https://rss.sciencedirect.com/publication/science/24058440",
    "Simulation Modelling Practice and Theory" : "https://rss.sciencedirect.com/publication/science/1569190X",
    "Journal of Safety Science and Resilience": "https://rss.sciencedirect.com/publication/science/26664496",
    "Ocean Engineering" : "https://rss.sciencedirect.com/publication/science/00298018",
    "International Journal of Rail Transportation": "https://www.tandfonline.com/feed/rss/tjrt20",
    "Transportation Research Record": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=trra&type=etoc&feed=rss",
    "Simulation": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=simb&type=axatoc&feed=rss",
}

# List of relevant emojis
emojis = ["🚶‍♂️", "🚶‍♀️", "🚸", "🏃‍♂️", "🏃‍♀️", "🚨", "👥", "👣"]

# File to store posted papers
POSTED_PAPERS_FILE = "posted_papers.json"

# Load spaCy model for NLP
nlp = spacy.load('en_core_web_sm')

def load_posted_papers():
    try:
        with open(POSTED_PAPERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_posted_papers(posted_papers):
    with open(POSTED_PAPERS_FILE, 'w') as f:
        json.dump(posted_papers, f)

def check_new_papers(feed_url, keyword, posted_papers):
    feed = feedparser.parse(feed_url)
    papers = []
    for entry in feed.entries:
        if keyword.lower() in entry.title.lower() and entry.link not in posted_papers:
            description_content = None
            
            # Specific handling for Transportation Research Record
            if 'journals.sagepub.com' in feed_url:
                description_html = html.unescape(entry.description)
                parts = description_html.split("<br />")
                description_content = parts[1].strip() if len(parts) > 1 else "Abstract not available."

            papers.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get('published', datetime.now().isoformat()),
                "description": description_content
            })
    return papers



def shorten_url(url):
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={url}")
        return response.text
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return url

def extract_key_concepts(title):
    doc = nlp(title)
    keywords = [chunk.text for chunk in doc.noun_chunks]
    return keywords

def create_image_prompt(title):
    key_concepts = extract_key_concepts(title)
    prompt = f"Conceptual illustration for research paper titled '{title}': {', '.join(key_concepts)}. Scientific, professional, academic style."
    return prompt

def send_generation_request(host, params):
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_KEY}"
    }

    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files) == 0:
        files["none"] = ''

    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

def generate_image_stable_diffusion(prompt):
    host = "https://api.stability.ai/v2beta/stable-image/generate/core"
    
    params = {
        "prompt": prompt,
        "negative_prompt": "",
        "aspect_ratio": "1:1",  # Twitter prefers square images
        "seed": 0,
        "output_format": "png"
    }
    
    try:
        response = send_generation_request(host, params)
        
        output_image = response.content
        finish_reason = response.headers.get("finish-reason")
        seed = response.headers.get("seed")
        
        if finish_reason == 'CONTENT_FILTERED':
            print("Generation failed NSFW classifier")
            return None
        
        return output_image
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def get_pii_from_url(url):
    pii_pattern = r'(?<=pii/)[^?/]+'
    pii_match = re.search(pii_pattern, url)
    if pii_match:
        return pii_match.group(0)
    else:
        return None

def fetch_abstract_from_elsevier(pii):
    url = f'https://api.elsevier.com/content/article/pii/{pii}'
    headers = {
        'X-ELS-APIKey': elsevier_api_key,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        title = data['full-text-retrieval-response']['coredata']['dc:title']
        abstract = data['full-text-retrieval-response']['coredata']['dc:description']
        return title, abstract
    else:
        print(f"Failed to retrieve document details. Status code: {response.status_code}")
        return None, None

def generate_summary_tweet(abstract_text):
    groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"""Summarize the key findings from this research abstract in a tweet of a 270 characters, be sure it should not more than 275 character and don't use bullet points:
    Abstract: {abstract_text}
    """
    payload = {
        "model": groq_model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
        "temperature": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_api_key}",
    }
    response = requests.post(groq_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        tweet = response.json()["choices"][0]["message"]["content"]
        # Remove any asterisks
        tweet = tweet.replace('***', '').replace('**', '').replace('*', '').replace('##', '').replace('###', '')

        # Ensure the tweet does not exceed 250 characters
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        return tweet
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def create_and_post_tweet_with_image(paper, journal, keyword, emoji):
    try:
        short_url = shorten_url(paper['link'])
        title = paper['title']
        keyword_lower = keyword.lower()
        title_with_hashtag = title.replace(keyword_lower, f"#{keyword_lower}")
        title_with_hashtag = title_with_hashtag.replace(keyword.capitalize(), f"#{keyword_lower}")
        
        tweet_text = f"#EvacPaperAlert: {title_with_hashtag} {emoji}\nJust published on #{journal.replace(' ', '')}\n\n🔗 Link: {short_url}"
        
        if len(tweet_text) > 280:
            excess = len(tweet_text) - 277
            title_with_hashtag = title_with_hashtag[:-excess] + "..."
            tweet_text = f"#EvacPaperAlert: {title_with_hashtag} {emoji}\nJust published on #{journal.replace(' ', '')}\n\n🔗 Link: {short_url}"
        
        image_prompt = create_image_prompt(title)
        image_data = generate_image_stable_diffusion(image_prompt)
        
        if image_data:
            with open("temp_image.png", "wb") as f:
                f.write(image_data)
            
            media = api.media_upload(filename="temp_image.png")
            
            response = client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            
            os.remove("temp_image.png")
            
            if hasattr(response, 'data'):
                print(f"Tweet posted successfully: {tweet_text}")
                tweet_id = response.data['id']
                
                # Initialize abstract_text to avoid reference before assignment
                abstract_text = None
                
                # Check for Transportation Research Record and use description if available
                if 'Transportation Research Record' in journal and paper['description']:
                    abstract_text = paper['description']
                else:
                    # Fetch abstract from Elsevier API if available
                    pii = get_pii_from_url(paper['link'])
                    if pii:
                        _, fetched_abstract = fetch_abstract_from_elsevier(pii)
                        if fetched_abstract:
                            abstract_text = fetched_abstract

                # Check for Simulation and use description if available
                if 'Simulation' in journal and paper['description']:
                    abstract_text = paper['description']
                else:
                    # Fetch abstract from Elsevier API if available
                    pii = get_pii_from_url(paper['link'])
                    if pii:
                        _, fetched_abstract = fetch_abstract_from_elsevier(pii)
                        if fetched_abstract:
                            abstract_text = fetched_abstract
                            
                # Only proceed with summary and threading if abstract_text is not None
                if abstract_text:
                    summary_tweet = generate_summary_tweet(abstract_text)
                    if summary_tweet:
                        create_thread_tweet(tweet_id, summary_tweet)
                else:
                    print("No abstract available to create a summary tweet.")

                return tweet_id
            else:
                print(f"Failed to post tweet. Response: {response}")
                return None
        else:
            print("Failed to generate image. Posting tweet without image.")
            response = client.create_tweet(text=tweet_text)
            if hasattr(response, 'data'):
                print(f"Tweet posted successfully (without image): {tweet_text}")
                return response.data['id']
            else:
                print(f"Failed to post tweet. Response: {response}")
                return None
    except Exception as e:
        print(f"An error occurred while posting tweet: {e}")
        return None


def create_thread_tweet(parent_tweet_id, text):
    try:
        if len(text) > 280:
            text = text[:277]
            # Ensure we don't cut off mid-word
            if text[-1] != ' ' and text[-2] != ' ':
                last_space = text.rfind(' ')
                if last_space != -1:
                    text = text[:last_space]
            text += "..."
        response = client.create_tweet(text=text, in_reply_to_tweet_id=parent_tweet_id)
        if hasattr(response, 'data'):
            print(f"Thread tweet posted successfully: {text}")
            return True
        else:
            print(f"Failed to post thread tweet. Response: {response}")
            return False
    except Exception as e:
        print(f"An error occurred while posting thread tweet: {e}")
        return False
    
if __name__ == "__main__":
    keyword = "evacuation"
    posted_papers = load_posted_papers()

    for journal, feed_url in rss_feeds.items():
        new_papers = check_new_papers(feed_url, keyword, posted_papers)
        
        if not new_papers:
            print(f"No new papers found matching the '{keyword}' criteria in the title for {journal}.")
        
        for paper in new_papers:
            emoji = random.choice(emojis)
            tweet_id = create_and_post_tweet_with_image(paper, journal, keyword, emoji)
            
            if tweet_id:
                posted_papers[paper['link']] = {
                    'title': paper['title'],
                    'posted_date': datetime.now().isoformat(),
                    'journal': journal
                }
                
                pii = get_pii_from_url(paper['link'])
                if pii:
                    title, abstract = fetch_abstract_from_elsevier(pii)
                    if abstract:
                        summary_tweet = generate_summary_tweet(abstract)
                        if summary_tweet:
                            create_thread_tweet(tweet_id, summary_tweet)

    save_posted_papers(posted_papers)
    print("RSS feed processing completed.")
