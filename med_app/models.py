import os
import fnmatch

from django.db import models
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone # Импортируем timezone

class City(models.Model):
    name = models.CharField("Город", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField("Район", max_length=255)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"


class MedCard(models.Model):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name="Город")
    district = ChainedForeignKey(
        District,
        chained_field="city",
        chained_model_field="city",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Район"
    )

    last_name = models.CharField("Фамилия", max_length=255)
    first_name = models.CharField("Имя", max_length=255)
    phone_number = models.CharField("Телефон", max_length=13, default=" ")
    surname = models.CharField("Отчество", max_length=255)
    birth_date = models.DateField("Дата рождения")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.surname}"

    class Meta:
        verbose_name = "Мед. карта"
        verbose_name_plural = "Мед. карты"

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # Add a save method to auto-generate slug if needed
    #
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделении"

class Question(models.Model):
    question = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                   related_name="questions")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Вопрос: {self.question[:50]}..."

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Call(models.Model):
    phone_number = models.CharField("Номер телефона", max_length=20)
    comment = models.TextField("Комментарий", blank=True, null=True)
    med_card = models.ForeignKey(MedCard, on_delete=models.CASCADE, verbose_name="Медкарта")
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        blank=True,
        verbose_name="Оператор (Система)"
    )
    ip_operator = models.CharField("Оператор IP-телефонии", max_length=50, blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    recording_path = models.CharField("Путь к записи (шаблон)", max_length=512, blank=True, null=True)

    def __str__(self):
        return f"Звонок #{self.id} от {self.phone_number}"

    def get_predicted_recording_path(self):
        # Этот метод теперь будет вызываться, когда self.created_at уже установлено.
        # Убраны отладочные принты из этого метода для чистоты,
        # но вы можете их вернуть, если понадобится дальнейшая отладка.
        # print(f"  DEBUG [get_predicted_recording_path] Вызван.")
        # print(f"    ip_operator: '{self.ip_operator}', phone_number: '{self.phone_number}', created_at: '{self.created_at}'")

        if not self.ip_operator:
            # print("  DEBUG [get_predicted_recording_path] Возвращает None: self.ip_operator отсутствует или пуст.")
            return None
        if not self.created_at:
            # print("  DEBUG [get_predicted_recording_path] Возвращает None: self.created_at отсутствует.")
            return None
        if not self.phone_number:
            # print("  DEBUG [get_predicted_recording_path] Возвращает None: self.phone_number отсутствует или пуст.")
            return None

        date_path_part = self.created_at.strftime("%Y/%m/%d")
        phone_clean = ''.join(filter(str.isdigit, self.phone_number))

        if not phone_clean:
            # print(f"  DEBUG [get_predicted_recording_path] Возвращает None: phone_clean пуст (из self.phone_number: '{self.phone_number}').")
            return None

        filename_pattern = f"exten-{self.ip_operator}-{phone_clean}-{self.created_at.strftime('%Y%m%d')}-*.wav"
        base_recordings_dir = '/mnt/cdr'
        predicted_path = os.path.join(base_recordings_dir, date_path_part, filename_pattern)
        # print(f"  DEBUG [get_predicted_recording_path] Успешно сгенерирован путь: '{predicted_path}'")
        return predicted_path

    def save(self, *args, **kwargs):
        # Определяем, создается ли новый объект.
        # self._state.adding будет True только при первом сохранении (INSERT).
        is_new = self._state.adding

        print(f"DEBUG [Call.save()] Начало. PK: {self.pk}, _state.adding: {is_new}")
        print(f"  self.recording_path (начальное): '{self.recording_path}'")

        # Сначала выполняем основное сохранение.
        # Это заполнит self.id (pk) и self.created_at для новых объектов.
        super().save(*args, **kwargs)
        print(f"DEBUG [Call.save()] После super().save(). PK: {self.pk}, self.created_at: '{self.created_at}'")

        # Теперь, когда объект сохранен и created_at точно установлено (если это был новый объект),
        # мы можем попытаться сгенерировать путь.
        # Делаем это только если это был новый объект И путь еще не установлен.
        if is_new and not self.recording_path:
            print(
                f"  DEBUG [Call.save()] Это новый объект (is_new=True) и self.recording_path пуст. Попытка генерации пути.")
            generated_path = self.get_predicted_recording_path()
            if generated_path:
                self.recording_path = generated_path
                print(f"  DEBUG [Call.save()] Поле self.recording_path УСТАНОВЛЕНО в: '{self.recording_path}'")
                # Так как мы изменили поле ПОСЛЕ первого super().save(),
                # нам нужно сохранить это изменение.
                # Чтобы избежать рекурсии и лишних сигналов, обновляем только это поле.
                kwargs['update_fields'] = ['recording_path']
                super().save(*args, **kwargs)
                # Или, что часто более явно и безопасно от рекурсии (если нет специфичных сигналов на post_save):
                # Call.objects.filter(pk=self.pk).update(recording_path=self.recording_path)
                # self.refresh_from_db(fields=['recording_path']) # Обновить инстанс из БД, если используется .update()
                print(f"  DEBUG [Call.save()] Объект повторно сохранен с обновленным recording_path.")
            else:
                print(
                    "  DEBUG [Call.save()] Метод get_predicted_recording_path() вернул None. Поле self.recording_path НЕ изменено.")
        elif not self.recording_path:
            print(
                f"  DEBUG [Call.save()] Это НЕ новый объект, но self.recording_path пуст. Генерация не производится в этом сценарии (можно добавить, если нужно).")
        else:
            print(
                f"  DEBUG [Call.save()] Поле self.recording_path ('{self.recording_path}') уже содержит значение или это не новый объект с пустым путем.")

        print(f"DEBUG [Call.save()] Конец. Финальное значение self.recording_path в инстансе: '{self.recording_path}'")

    class Meta:
        verbose_name = "Звонок"
        verbose_name_plural = "Звонки"
        ordering = ['-created_at']


class CallQuestion(models.Model):
    call = models.ForeignKey("Call", on_delete=models.CASCADE, related_name="call_questions")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    questions = ChainedManyToManyField(
        Question,
        chained_field="department",
        chained_model_field="department",
        blank=True
    )

    def __str__(self):
        return f"Вопросы из {self.department.name} для звонка #{self.call.id}"



class Visit(models.Model):
    med_card = models.ForeignKey(
        MedCard,
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name="Медицинская карта пациента"
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name='registered_visits',
        verbose_name="Оператор"
    )
    visit_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Время посещения"
    )
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Причина посещения"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Заметки оператора"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время регистрации"
    )

    def __str__(self):
        visit_time_formatted = self.visit_time.strftime('%Y-%m-%d %H:%M')
        return f"Посещение {self.med_card} в {visit_time_formatted}"

    class Meta:
        verbose_name = "Посещение"
        verbose_name_plural = "Посещения"
        ordering = ['-visit_time']



