from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# youtube api information
from html import unescape
from googleapiclient.discovery import build

# NLP module
from NLP.preprocessing import preprocess_comment
from NLP import analysis

# env tools
import os
from dotenv import load_dotenv

# time tool
from datetime import datetime

# Load environment variables
load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")


class CommentList(APIView):

    # define some variables to fetch comments from youtube
    comments_per_call = 3
    total_calls = 2

    def get_comments_from_youtube(self, video_id):
        """
        Function to fetch comments from a youtube video using the youtube API.
        Also, preprocesses the comments using the preprocess_comment function from the preprocessing module.

        Args:
            video_id (str): the youtube video ID

        Returns:
            comments_by_month (dict): dictionary containing comments by month
        """

        youtube = build("youtube", "v3", developerKey=youtube_api_key)

        # Define the parameters for the API call
        params = {
            "part": "snippet",
            "videoId": video_id,  # replace with your video ID
            "maxResults": self.comments_per_call,  # number of comments per request (max is 100)
        }

        # Make the initial API call
        response = youtube.commentThreads().list(**params).execute()

        # Extract comments by month
        comments_by_month = {}

        # Function to process response items
        def process_response(response):
            for item in response["items"]:
                # Decode the comment text using html.unescape
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

                    # Preprocess the comment
                    comment = preprocess_comment(comment)

                    if comment:
                        comments_by_month[month].append(comment)

        # Process the initial response
        process_response(response)

        # Check for next page token
        next_page_token = response.get("nextPageToken")

        # Loop to fetch more comments if available
        for _ in range(
            self.total_calls - 1
        ):  # already fetched the first batch, so 9 more iterations
            if next_page_token:
                params["pageToken"] = next_page_token
                response = youtube.commentThreads().list(**params).execute()
                process_response(response)
                next_page_token = response.get("nextPageToken")
            else:
                break

        return comments_by_month

    def get(self, request, video_id):
        comments = self.get_comments_from_youtube(video_id)

        vader_results = analysis.comments_sentiment_analysis(comments, method="vader")
        ml_results = analysis.comments_sentiment_analysis(comments, method="ml")

        print("-----------------Vader-----------------")
        print(vader_results)

        print("-----------------ML-----------------")
        print(ml_results)

        return Response("Sucess", status=status.HTTP_200_OK)
