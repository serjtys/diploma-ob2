from django import forms

from .models import CustomUser


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)
    nickname = forms.CharField(
        label="Никнейм",
        required=False,
        help_text="Будет отображаться вместо номера телефона",
    )

    class Meta:
        model = CustomUser
        fields = ("phone_number", "nickname")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if nickname and CustomUser.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("Этот никнейм уже занят")
        return nickname

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
