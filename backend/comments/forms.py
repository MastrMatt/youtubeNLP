from django import forms


class CommentForm(forms.Form):
    analysis_type = forms.ChoiceField(
        label="Analysis Type",
        choices=[
            ("vader", "Non-AI"),
            ("ml", "AI"),
        ],
        required=True,
    )

    video_url = forms.URLField(
        label="Youtube Video URL",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter Here"}),
    )

    num_comments = forms.IntegerField(
        label="Number of Comments",
        required=True,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Here"}),
    )

    def clean_video_url(self):
        video_url = self.cleaned_data["video_url"]

        if "youtube.com" not in video_url:
            raise forms.ValidationError("Invalid Youtube URL")
        if "v=" not in video_url:
            raise forms.ValidationError("Invalid Youtube URL")

        return video_url
