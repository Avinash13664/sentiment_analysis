from googleapiclient.discovery import build
import pandas as pd
import string
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import emoji
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn 
#from IPython.display import display, HTML

stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
              "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
              "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these",
              "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
              "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
              "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before",
              "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
              "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
              "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
              "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

def get_video_comments(api_key, video_id):
    comments = []

    # Build the YouTube Data API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Request comments for the specified video
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100,  # Adjust the maxResults to retrieve more comments if needed
    ).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # Check if there are more comments to fetch
        if 'nextPageToken' in response:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100,
                pageToken=response['nextPageToken']
            ).execute()
        else:
            break

    return comments



def get_emotion(word):
    synsets = wn.synsets(word)
    if synsets:
        synset = synsets[0]  # Consider the first synset
        senti_synset = swn.senti_synset(synset.name())
        if senti_synset:
            if senti_synset.pos_score() > senti_synset.neg_score():
                return 'positive'
            elif senti_synset.pos_score() < senti_synset.neg_score():
                return 'negative'
    return 'neutral'

def get_sentence_emotion(sentence):
    # Tokenize the sentence
    tokens = word_tokenize(sentence)
    
    # Filter out stop words
    tokens = [word.lower() for word in tokens if word.lower() not in stop_words]
    
    # Determine emotions for each word
    emotions = [get_emotion(word) for word in tokens]
    
    # Determine if positive or negative emojis are present
    positive_emojis = ['😊', '😄', '❤️','✅','❤','🎉', '😃', '😍', '👍', '🌟', '😇', '🥰', '😎', '😁', '😌', '😆', '🤗', '😊', '😋', '😘', '🤩', '🥳','😂']
    negative_emojis = ['😡', '😞', '😢', '😔', '💔', '👎', '💣', '😒', '😠', '😕', '😤', '😩', '😖', '😣', '😭', '😧', '😨', '😰', '😥', '😓']



    for char in sentence:
        if char in positive_emojis:
            emotions.append('positive')
        elif char in negative_emojis:
            emotions.append('negative')
    
    # Count the occurrences of each emotion
    emotion_counts = {emotion: emotions.count(emotion) for emotion in set(emotions)}
    
    # Check if 'positive' and 'negative' emotions are present
    if 'positive' in emotion_counts and 'negative' in emotion_counts:
        if emotion_counts['positive'] > emotion_counts['negative']:
            return 'positive'
        elif emotion_counts['positive'] < emotion_counts['negative']:
            return 'negative'
    
    # Check if only 'negative' and 'neutral' emotions are present
    elif 'negative' in emotion_counts and 'neutral' in emotion_counts:
        return 'negative'
    
    # Check if only 'positive' and 'neutral' emotions are present
    elif 'positive' in emotion_counts and 'neutral' in emotion_counts:
        return 'positive'
    
    # Otherwise, return 'neutral'
    return 'neutral'

if __name__ == "__main__":
    api_key = "AIzaSyAM-E-gWGUnp3MdUGF62ERt-jrYY4IFiAs"
    youtube_link = str(input("Enter the link of youtube video to be analysed:"))
    video_id = youtube_link.split("=")[-1]
    all_comments = get_video_comments(api_key, video_id)
    data = []
    for idx, comment in enumerate(all_comments, start=1):
        #print(f"Comment {idx}: {comment}")
        lower_case = comment.lower()
        cleaned_comm = lower_case.translate(str.maketrans('','',string.punctuation))
        new_data = {'Comment_ID': f'{idx}', 'Comment': f'{cleaned_comm}'}
        data.append(new_data)

# Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
    df.to_csv(f'comment_data.csv', index=False)

# Display the final DataFrame
    #print(df)

    df['Predominant_Emotion'] = df['Comment'].apply(get_sentence_emotion)

# Display the DataFrame with predominant emotions
    #print(df["Predominant_Emotion"])

    total_entries = len(df['Predominant_Emotion'])
    positive_count = (df["Predominant_Emotion"] == 'positive').sum()
    negative_count = (df["Predominant_Emotion"] == 'negative').sum()

    positive_percentage = (positive_count / total_entries) * 100
    negative_percentage = (negative_count / total_entries) * 100

    #print(positive_percentage, negative_percentage)

    # Determine the overall emotion based on higher percentage
    if positive_percentage > negative_percentage:
        overall_emotion = 'positive'
    elif positive_percentage < negative_percentage:
        overall_emotion = 'negative'
    else:
        overall_emotion = 'neutral'

    print('Video Sentiment: ', overall_emotion)
   