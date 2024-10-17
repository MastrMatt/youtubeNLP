from django import forms


class CommentForm(forms.Form):
    analysis_type = forms.ChoiceField(
        label="Analysis Type",
        choices=[
            ("vader", "Non-AI"),
            ("ml", "AI"),
        ],
        required=True,
        widget=forms.Select(attrs={"class": "analysis-type"}),
    )

    video_url = forms.URLField(
        label="Youtube Video URL",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "video-url", "placeholder": "Enter here"}
        ),
    )

    num_comments = forms.IntegerField(
        label="Number of Comments",
        required=True,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(
            attrs={
                "class": "num-comments",
                "placeholder": "Enter less than 100, due to weak server",
            }
        ),
    )

    def clean_video_url(self):
        video_url = self.cleaned_data["video_url"]

        if "youtube.com" not in video_url:
            raise forms.ValidationError("Invalid Youtube URL")
        if "v=" not in video_url:
            raise forms.ValidationError("Invalid Youtube URL")

        return video_url
