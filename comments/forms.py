from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

class CommentForm(forms.Form):
    content_type = forms.CharField(widget = forms.HiddenInput)
    object_id = forms.IntegerField(widget= forms.HiddenInput)
    # parent_id = forms.IntegerField(widget= forms.HiddenInput, required=False)
    content = forms.CharField(label= '',widget= forms.Textarea(attrs={'placeholder': 'Your Message'}))