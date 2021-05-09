from django.shortcuts import render #to call html file we need
import tweepy #to access api
from tweepy import OAuthHandler # for authentication
import matplotlib.pyplot as plt # for displaying pie chart
from textblob import TextBlob # for analysis of the tweet
import pandas as pd #to format the data and put in to the csv file


# Create your views here.

def home(request):
    return render(request, 'home.html')


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def trend(request):
    API_key = "your API_key"
    API_secret_key = "your API_secret_key"
    Access_token = "your Access_token"
    Access_token_secret = "your Access_token_secret"

    auth = OAuthHandler(API_key, API_secret_key)#auth object
    auth.set_access_token(Access_token, Access_token_secret)
    api = tweepy.API(auth)

    search = request.POST.get('Go') #get the value of the city from the page

    Dict = {'Mumbai': 2295411, 'Chennai': 2295424, 'Kolkata': 2295386, 'Hyderabad': 2211024, 'Pune': 2295412,
            'New Delhi': 2295019, 'Ahmedabad': 29103194, 'Jaipur': 2295401, 'Surat': 2295405,
            'Agra': 2295399} #Static dict.

    woeid = 1 # for global Trending Hashtag; Where on earth id=woeid
    for city, id in Dict.items():
        if city == search:
            woeid = id

    trends = api.trends_place(id=woeid) # method
    hashtag, volume = [], [] # list

    for value in trends:
        for trend in value['trends']:
            hashtag.append(trend['name']) # dict. Key
            if trend['tweet_volume'] != None:
                volume.append(trend['tweet_volume'])

    # sorted method sorts 1st list in descending order that's why volume is mentioned first
    # As we want most trending hashtags first
    zipped_lists = sorted(zip(volume, hashtag), reverse=True)

    # unzipping is done to get both sorted tuples individually
    vol, hash = zip(*zipped_lists)

    # Re-zipping is needed as the render method only accepts dictionaries
    final_list = zip(hash, vol) #zip method return list

    return render(request, 'trending_hashtags.html', {'trends': final_list}) # {}Disctory


def search(request):
    API_key = "your API_key"
    API_secret_key = "your API_secret_key"
    Access_token = "your Access_token"
    Access_token_secret = "your Access_token_secret"

    auth = OAuthHandler(API_key, API_secret_key)
    auth.set_access_token(Access_token, Access_token_secret)
    api = tweepy.API(auth)

    searchTerm = request.POST.get('query') #get the query of page
    NoOfTerms = int(request.POST.get('no_of_tweets')) #Number of term

    # input for term to be searched and how many tweets to search
    # searchTerm = input("Enter Keyword/Tag to search about: ")
    # NoOfTerms = int(input("Enter how many tweets to search: "))

    # searching for tweets
    tweets = tweepy.Cursor(api.search, q=searchTerm, lang="en", tweet_mode='extended').items(NoOfTerms)

    # creating some variables to store info
    polarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral = 0, 0, 0, 0, 0, 0, 0, 0
    sentiment = ""
    ID, text, user, screen_name, created_at, sentiment_score, Sentiment = [], [], [], [], [], [], [] #list

    # iterating through tweets fetched
    for tweet in tweets:

        ID.append(tweet.id)
        text.append(tweet.full_text)
        user.append(tweet.user.name)
        screen_name.append(tweet.user.screen_name)
        created_at.append(tweet.created_at)

        analysis = TextBlob(tweet.full_text)
        # print(analysis.sentiment)  # print tweet's polarity
        sentiment_score.append(analysis.sentiment.polarity)
        polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

        if analysis.sentiment.polarity == 0:  # adding reaction of how people are reacting to find average later
            neutral += 1
        elif 0 < analysis.sentiment.polarity <= 0.3:
            wpositive += 1
        elif 0.3 < analysis.sentiment.polarity <= 0.6:
            positive += 1
        elif 0.6 < analysis.sentiment.polarity <= 1:
            spositive += 1
        elif -0.3 < analysis.sentiment.polarity <= 0:
            wnegative += 1
        elif -0.6 < analysis.sentiment.polarity <= -0.3:
            negative += 1
        elif -1 < analysis.sentiment.polarity <= -0.6:
            snegative += 1

    sentiment_score = [round(num, 2) for num in sentiment_score] #list comprehension (loop in list)

    # finding average of how people are reacting
    positive = percentage(positive, NoOfTerms)
    wpositive = percentage(wpositive, NoOfTerms)
    spositive = percentage(spositive, NoOfTerms)
    negative = percentage(negative, NoOfTerms)
    wnegative = percentage(wnegative, NoOfTerms)
    snegative = percentage(snegative, NoOfTerms)
    neutral = percentage(neutral, NoOfTerms)

    # finding average reaction
    polarity = polarity / NoOfTerms

    # printing out data
    print("How people are reacting on " + searchTerm + " by analyzing " + str(NoOfTerms) + " tweets.")
    print()
    print("General Report: ")

    if polarity == 0:
        sentiment = "Neutral"
        print(sentiment)
    elif 0 < polarity <= 0.3:
        sentiment = "Weakly Positive"
        print(sentiment)
    elif 0.3 < polarity <= 0.6:
        sentiment = "Positive"
        print(sentiment)
    elif 0.6 < polarity <= 1:
        sentiment = "Strongly Positive"
        print(sentiment)
    elif -0.3 < polarity <= 0:
        sentiment = "Weakly Negative"
        print(sentiment)
    elif -0.6 < polarity <= -0.3:
        sentiment = "Negative"
        print(sentiment)
    elif -1 < polarity <= -0.6:
        sentiment = "Strongly Negative"
        print(sentiment)

    print()
    print("Detailed Report: ")
    print(str(positive) + "% people thought it was positive")
    print(str(wpositive) + "% people thought it was weakly positive")
    print(str(spositive) + "% people thought it was strongly positive")
    print(str(negative) + "% people thought it was negative")
    print(str(wnegative) + "% people thought it was weakly negative")
    print(str(snegative) + "% people thought it was strongly negative")
    print(str(neutral) + "% people thought it was neutral")

    labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]', #str() Concatination
              'Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
              'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]',
              'Strongly Negative [' + str(snegative) + '%]']
    sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
    colors = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(NoOfTerms) + ' Tweets.')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    TWEETS = {'ID': ID,
              'user name': user,
              'screen name': screen_name,
              'created at': created_at,
              'text': text,
              'score': sentiment_score
              } #dict.

    df = pd.DataFrame(TWEETS, columns=['ID', 'user name', 'screen name', 'created at', 'text', 'score'])
    print(df)

    df.to_csv('data.csv', index=False)

    no_of_neu, no_of_neg, no_of_pos = 0, 0, 0

    for score in sentiment_score:
        if score == 0:
            no_of_neu += 1
            Sentiment.append("neutral")
        elif score < 0.0:
            no_of_neg += 1
            Sentiment.append("Negative")
        elif score > 0.0:
            no_of_pos += 1
            Sentiment.append("Positive")

    values = {'no_of_pos': no_of_pos, 'no_of_neg': no_of_neg, 'no_of_neu': no_of_neu} #Dict.

    context = {'data': zip(ID, text, user, screen_name, created_at, sentiment_score, Sentiment), 'values': values,
               'topic': searchTerm, 'NoOfTerms': NoOfTerms}

    return render(request, 'output.html', context=context)

