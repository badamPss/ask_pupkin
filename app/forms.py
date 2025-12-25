from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.text import slugify
from .models import Profile, Question, Answer, Tag


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your login here'})
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Sorry, wrong password!')
        return cleaned_data


class SignUpForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Repeat password'
    )
    nickname = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='NickName'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Upload avatar'
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Такой email уже существует.')
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают.')
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            if self.cleaned_data.get('nickname'):
                profile.nickname = self.cleaned_data['nickname']
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data['avatar']
            profile.save()
        return user


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nickname = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='NickName'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Upload avatar'
    )

    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            if hasattr(self.user, 'profile') and self.user.profile:
                self.fields['nickname'].initial = self.user.profile.nickname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Такой email уже существует.')
        return email

    def save(self, commit=True):
        if self.user:
            profile, created = Profile.objects.get_or_create(user=self.user)
            profile.nickname = self.cleaned_data.get('nickname', '')
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data['avatar']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
                profile.save()
            return profile
        return super().save(commit=commit)


class AskQuestionForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'moon, park, puzzle'}),
        help_text='Через запятую. До 5 тегов.'
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'How to build a moon park ?',
                'maxlength': 150
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Really, how? Have no idea about it',
                'maxlength': 10000
            })
        }
        help_texts = {
            'title': 'Максимум 150 символов.',
            'text': 'Подробно опишите проблему. Максимум 10000 символов.'
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str:
            return []
        
        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        if len(tag_names) > 5:
            raise forms.ValidationError('Можно указать не более 5 тегов.')
        
        return tags_str

    def save(self, commit=True):
        question = super().save(commit=False)
        if commit:
            question.save()
            tags_str = self.cleaned_data.get('tags', '')
            question.tags.clear()
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                for tag_name in tag_names:
                    slug = slugify(tag_name)
                    if slug:
                        tag, created = Tag.objects.get_or_create(
                            slug=slug,
                            defaults={'name': tag_name}
                        )
                        question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ваш ответ...',
                'maxlength': 5000
            })
        }
        help_texts = {
            'text': 'Максимум 5000 символов.'
        }

