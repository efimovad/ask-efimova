from django import forms
from .models import Post, Comment, Tag, UserProfile, Vote
from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("passwords do not match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    query = forms.CharField(label='Username / Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        query = self.cleaned_data.get('query')
        password = self.cleaned_data.get('password')
        user_qs_final = User.objects.filter(
            Q(username__iexact=query) |
            Q(email__iexact=query)
        ).distinct()
        if not user_qs_final.exists() and user_qs_final.count != 1:
            raise forms.ValidationError("Invalid credentials - user does note exist")
        user_obj = user_qs_final.first()
        if not user_obj.check_password(password):
            raise forms.ValidationError("credentials are not correct")
        self.cleaned_data["user_obj"] = user_obj
        return super(UserLoginForm, self).clean(*args, **kwargs)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'tags')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ('title',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture', 'bio', 'location', 'birth_date')


class VoteForm(forms.ModelForm):
    obj_name = forms.CharField(required=True, max_length=8)
    obj_id = forms.IntegerField(required=True)
    value = forms.IntegerField(required=True)

    class Meta:
        model = Vote
        fields = ['value']

    def __init__(self, author, *args, **kwargs):
        self.user = author
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        obj_name = cleaned_data.get('obj_name')
        obj_id = cleaned_data.get('obj_id')
        value = cleaned_data.get('value')

        if obj_name != 'answer' and obj_name != 'question':
            self.add_error('obj_name', 'Wrong parameters')

        if value != 1 and value != -1:
            self.add_error('value', 'Vote value can be only 1 or -1')

        votes = Vote.objects.filter(user=self.user)\
                            .filter(content_type__model__iexact=obj_name)
        if votes:
            _votes = votes.filter(object_id=obj_id)
            _votes.exclude(value=value).delete()
            if _votes:
                self.add_error('value', 'Sorry but you have already voted!!!')

    def save(self, *args, commit=True):
        obj = super().save(commit=False)
        obj.user = self.user
        obj.content_object = args[0]
        obj.content_object.rate += obj.value
        obj.content_object.save(update_fields=['rate'])

        if commit:
            obj.save()


