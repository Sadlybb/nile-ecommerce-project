from django import forms

from . models import Review, Address


class ReviewForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Title'})
    )
    description = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Write your review ...'})
    )

    class Meta:
        model = Review
        fields = ['title', 'description', 'rating']
