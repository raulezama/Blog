from django import forms
from pagedown.widgets import PagedownWidget
from .models import Post

class PostForm(forms.ModelForm):
    content =  forms.CharField(widget =PagedownWidget)
    publish = forms.DateField(widget = forms.SelectDateWidget)
    class Meta:
        model = Post
        fields = ["title", "content","image", "draft", "publish", "references","referencestwo","referencesthree","referencesfour", "post_tagone", "post_tagtwo",]

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField()


