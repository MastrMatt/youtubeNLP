from django import forms


class CommentForm(forms.Form):
    analysis_type = forms.ChoiceField(
        label="Analysis Type",
        choices=[
            ("vader-analysis", "Non Machine Learning"),
            ("hugging-face", "Machine Learning"),
        ],
        required=True,
    )

    video_url = forms.URLField(
        label="Youtube Video URL",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter Here"}),
    )
