import json
from django.shortcuts import render
from django.http import HttpResponse
from html import unescape
from googleapiclient.discovery import build
from datetime import datetime

from .forms import CommentForm

import os
from dotenv import load_dotenv

# NLP stuff
from NLP.preprocessing import preprocess_comment
from NLP import analysis

# Load environment variables
youtube_api_key = os.getenv("YOUTUBE_API_KEY")


def get_comments_from_youtube(video_id, num_comments=50):
    """
    Function to fetch comments from a youtube video using the youtube API.
    Also, preprocesses the comments using the preprocess_comment function from the preprocessing module.

    Args:
        video_id (str): the youtube video ID

    Returns:
        comments_by_month (dict): dictionary containing comments by month
    """

    youtube = build("youtube", "v3", developerKey=youtube_api_key)

    comments_per_call = 50
    num_calls = num_comments // comments_per_call

    # Define the parameters for the API call
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": comments_per_call,
    }

    response = youtube.commentThreads().list(**params).execute()
    comments_by_month = {}

    def process_response(response):
        for item in response["items"]:
            comment = unescape(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )
            published_at = item["snippet"]["topLevelComment"]["snippet"].get(
                "publishedAt"
            )
            if published_at:
                pub_date = datetime.fromisoformat(published_at.split("T")[0])
                month = pub_date.strftime("%Y-%m")
                if month not in comments_by_month:
                    comments_by_month[month] = []

                comment = preprocess_comment(comment)
                if comment:
                    comments_by_month[month].append(comment)

    process_response(response)
    next_page_token = response.get("nextPageToken")

    for _ in range(num_calls - 1):
        if next_page_token:
            params["pageToken"] = next_page_token
            response = youtube.commentThreads().list(**params).execute()
            process_response(response)
            next_page_token = response.get("nextPageToken")
        else:
            break

    return comments_by_month


def index(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            analysis_type = form.cleaned_data["analysis_type"]
            num_comments = form.cleaned_data["num_comments"]
            video_url = form.cleaned_data["video_url"]

            # get the video url
            video_id = video_url.split("v=")[1].split("&")[0]

            # redirect to the comments analysis view
            return comments_analysis_view(
                request,
                video_id,
                analysis_type=analysis_type,
                num_comments=num_comments,
            )
        else:
            return HttpResponse("Invalid form")
    else:
        form = CommentForm()
        return render(request, "base.html", {"form": form})


def comments_analysis_view(request, video_id, analysis_type="vader", num_comments=50):

    comments = get_comments_from_youtube(video_id, num_comments=num_comments)

    # Perform sentiment analysis on the comments
    if analysis_type == "vader":
        results = analysis.comments_sentiment_analysis(comments, method="vader")
    else:
        results = analysis.comments_sentiment_analysis(comments, method="ml")

    # Prepare data for the chart
    labels = list(results.keys())

    positive_data = []
    negative_data = []
    neutral_data = []
    max_data = []
    min_data = []
    max_comments = []
    min_comments = []

    for label in labels:
        positive_data.append(results[label]["sentiment_percentages"]["positive"])
        negative_data.append(results[label]["sentiment_percentages"]["negative"])
        neutral_data.append(results[label]["sentiment_percentages"]["neutral"])
        max_data.append(results[label]["max_sentiment"])
        min_data.append(results[label]["min_sentiment"])
        max_comments.append(results[label]["max_sentiment_comment"])
        min_comments.append(results[label]["min_sentiment_comment"])

    # append the label string to the comments
    for i in range(len(max_comments)):
        max_comments[i] = labels[i] + ": " + max_comments[i]
        min_comments[i] = labels[i] + ": " + min_comments[i]

    # prepare data for chart.js
    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Positive Sentiment %",
                "data": positive_data,
            },
            {
                "label": "Negative Sentiment %",
                "data": negative_data,
            },
            {
                "label": "Neutral Sentiment %",
                "data": neutral_data,
            },
        ],
        "options": {
            "tension": 0.1,
            "borderWidth": 3,
            "borderRadius": 6,
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Sentiment % Vs. Time",
                    "font": {
                        "size": 25,
                    },
                }
            },
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "title": {
                        "display": True,
                        "text": "Sentiment %",
                        "font": {
                            "size": 15,
                        },
                    },
                },
                "x": {
                    "title": {
                        "display": True,
                        "text": "Month/Year Pair",
                        "font": {
                            "size": 15,
                        },
                    }
                },
            },
        },
    }

    context = {
        "video_id": json.dumps(video_id),
        "chart_data": json.dumps(chart_data),
        "labels": labels,
        "majority_sentiment": 0,
        "max_comments": max_comments,
        "min_comments": min_comments,
    }

    # need to draw the 3 graphs in this view
    return render(request, "displayComments.html", context)
