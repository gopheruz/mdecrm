from datetime import datetime

from django import forms
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
from smart_selects.form_fields import ChainedModelChoiceField

from med_app.models import *
from django.forms import BaseModelFormSet


class CreateMedCartForm(forms.ModelForm):
    # Новые поля для ввода названий, если город/район отсутствуют в базе
    new_city_name = forms.CharField(
        label="Или введите новый город",
        required=False,  # Необязательное поле
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название нового города'})
    )
    new_district_name = forms.CharField(
        label="Или введите новый район",
        required=False,  # Необязательное поле
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название нового района'})
    )

    class Meta:
        model = MedCard
        fields = (
            'city',  # Выбор существующего города
            'new_city_name',  # Ввод нового города
            'district',  # Выбор существующего района (зависит от city)
            'new_district_name',  # Ввод нового района
            'first_name',
            'last_name',
            'surname',
            'birth_date',
            'phone_number'
        )

        widgets = {
            # 'city' и 'district' будут использовать свои стандартные виджеты (Select и ChainedSelect)
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля выбора города и района необязательными на уровне формы,
        # так как пользователь может вместо них ввести новые названия
        self.fields['city'].required = False
        self.fields['district'].required = False

        # Применяем класс к виджетам city и district, если они есть
        # (для district может потребоваться особый подход из-за ChainedForeignKey)
        if 'city' in self.fields:
            self.fields['city'].widget.attrs.update({'class': 'form-control'})
        if 'district' in self.fields:
            # ChainedForeignKey может переопределять виджет, применяем класс осторожно
            # Возможно, класс уже добавлен в вашем коде ChainedForeignKey или его нужно добавить через JS
            self.fields['district'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        """
        Дополнительная валидация формы.
        """
        cleaned_data = super().clean()
        city = cleaned_data.get('city')
        new_city_name = cleaned_data.get('new_city_name')
        district = cleaned_data.get('district')
        new_district_name = cleaned_data.get('new_district_name')

        # --- Валидация Города ---
        if not city and not new_city_name:
            raise ValidationError("Необходимо выбрать существующий город или ввести название нового города.",
                                  code='city_required')
        if city and new_city_name:
            raise ValidationError("Нельзя одновременно выбрать существующий город и ввести название нового.",
                                  code='city_ambiguous')

        # --- Валидация Района ---
        # Если введен новый город, то нужно обязательно ввести и новый район
        if new_city_name and not new_district_name:
            raise ValidationError("Если вы вводите новый город, необходимо также ввести название нового района.",
                                  code='new_district_required_for_new_city')
        # Если введен новый город, нельзя выбирать существующий район
        if new_city_name and district:
            raise ValidationError("Если вы вводите новый город, нельзя выбирать район из списка.",
                                  code='district_invalid_for_new_city')

        # Если выбран существующий город
        if city:
            if not district and not new_district_name:
                raise ValidationError(
                    f"Для города '{city.name}' необходимо выбрать существующий район или ввести название нового.",
                    code='district_required')
            if district and new_district_name:
                raise ValidationError("Нельзя одновременно выбрать существующий район и ввести название нового.",
                                      code='district_ambiguous')
            # Дополнительная проверка: выбранный район должен принадлежать выбранному городу
            # (ChainedForeignKey обычно сам это проверяет, но для надежности)
            if district and district.city != city:
                raise ValidationError(f"Выбранный район '{district.name}' не принадлежит городу '{city.name}'.",
                                      code='district_mismatch')

        return cleaned_data

class SearchMedCardForm(forms.Form):
    first_name = forms.CharField(
        label="Имя",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        label="Фамилия",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    surname = forms.CharField(
        label="Отчество",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    phone_number = forms.CharField(
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

class CallForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = ['phone_number', 'ip_operator', 'comment']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер телефона'
            }),
            'ip_operator': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер оператора IP-телефонии (например, 203)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'height: 100px;',
                'placeholder': 'Комментарий (необязательно)'
            })
        }


class CallQuestionForm(forms.ModelForm):
    class Meta:
        model = CallQuestion
        fields = ['department', 'questions']
        widgets = {
            'department': forms.Select(attrs={
                'class': 'form-control department-select'
            }),
            'questions': forms.SelectMultiple(attrs={
                'class': 'form-control questions-select'
            })
        }


class BaseCallQuestionFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = CallQuestion.objects.none()


CallQuestionFormSet = modelformset_factory(
    CallQuestion,
    form=CallQuestionForm,
    formset=BaseCallQuestionFormSet,
    extra=5,
    can_delete=True
)


class VisitCreateForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ('reason', 'notes',)

        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

class OperatorReportForm(forms.Form):
    operator = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('first_name', 'last_name'), # Or filter users who are operators
        label="Выберите оператора",
        required=True, # Оператор остается обязательным для выбора
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label="Дата начала",
        required=False, # Сделать поле необязательным
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label="Дата конца",
        required=False, # Сделать поле необязательным
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class QuestionsReportForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Отделение",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label="Дата начала",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': datetime.now().strftime('%Y-%m-%d')
        }),
        required=False
    )
    end_date = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': datetime.now().strftime('%Y-%m-%d')
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Дата начала не может быть позже даты окончания")

        # Устанавливаем сегодняшнюю дату, если не указана конечная
        if start_date and not end_date:
            cleaned_data['end_date'] = datetime.now().date()

        return cleaned_data


class VisitsReportForm(forms.Form):
    start_date = forms.DateField(
        label="Дата начала",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    end_date = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Дата начала не может быть позже даты окончания")
        return cleaned_data