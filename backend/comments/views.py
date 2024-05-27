from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Comment
from .serializers import CommentSerializer

# youtube api information
from googleapiclient.discovery import build

# NLP tools
import nltk
import numpy as np

from langdetect import detect

# env tools
import os
from dotenv import load_dotenv

# time tool
from datetime import datetime

# Load environment variables
load_dotenv()

#download nltk data
nltk.download('punkt')

youtube_api_key = os.getenv("YOUTUBE_API_KEY")


class CommentList(APIView):
    def get_comments_from_youtube(self, video_id):
        youtube = build("youtube", "v3", developerKey=youtube_api_key)

        # Define the parameters for the API call
        params = {
            "part": "snippet",
            "videoId": video_id,  # replace with your video ID
            "maxResults": 100,  # number of comments per request (max is 100)
        }

        # Make the initial API call
        response = youtube.commentThreads().list(**params).execute()

        # Extract comments by month
        comments_by_month = {}

        # Function to process response items
        def process_response(response):
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                published_at = item["snippet"]["topLevelComment"]["snippet"].get(
                    "publishedAt"
                )
                if published_at:
                    pub_date = datetime.fromisoformat(published_at.split("T")[0])
                    month = pub_date.strftime("%Y-%m")
                    if month not in comments_by_month:
                        comments_by_month[month] = []
                    comments_by_month[month].append(comment)

        # Process the initial response
        process_response(response)

        # Check for next page token
        next_page_token = response.get("nextPageToken")

        # Loop to fetch more comments if available
        for _ in range(9):  # already fetched the first batch, so 9 more iterations
            if next_page_token:
                params["pageToken"] = next_page_token
                response = youtube.commentThreads().list(**params).execute()
                process_response(response)
                next_page_token = response.get("nextPageToken")
            else:
                break

        return comments_by_month

    #currenly only works for english comments
    def preprocess_comments(self, comments):

        def verify_english(comment):
            # check if comment is in english
            try:
                return detect(comment) == "en"
            except:
                return False
            
        def clean_comment(comment):
            #remove non-english characters and emojis
            comment = comment.encode('ascii', 'ignore').decode('ascii')
            return comment
        
        
        test_comment0 = "This is testing a tokenizer and preprocessor"
        test_comment1 = "💪🗿 those are some emojis"
        test_comment2 = "Эти произведения помогают мне бороться со своими демонами. Торфинн, Гатс, Мусаши и авторы, что придумали этих персонажей- они до сих пор сохраняют моë пламя в груди...."

        comments = [test_comment0, test_comment1, test_comment2]
        
        for comment in comments:
            #ensure comment is in english
            comment = comment.encode('ascii', 'ignore').decode('ascii')

            


    def get(self, request, video_id):
        comments = self.get_comments_from_youtube(video_id)
        preprocessed_comments = self.preprocess_comments(comments)
        return Response("Sucess", status=status.HTTP_200_OK)
