from django import forms

from django_countries.widgets import CountrySelectWidget

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


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address

        fields = ['country', 'city', 'postal_code',
                  'address_line', 'assigned_phone_number']

        widgets = {
            'country': CountrySelectWidget(attrs={'style': 'height: 30px;'}),
            'city': forms.TextInput(attrs={'placeholder': 'City', 'style': 'height: 30px;'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Postal Code', 'style': 'height: 30px;'}),
            'address_line': forms.TextInput(attrs={'placeholder': 'Address', 'style': 'height: 30px;'}),
            'assigned_phone_number': forms.TextInput(attrs={'placeholder': 'Assigned Phone Number', 'style': 'height: 30px;'}),
        }
