from django.forms import DateTimeInput, ModelForm, Select, Textarea, TextInput, URLInput
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from main.models import Project, Experience

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "thumbnail",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "thumbnail": "URL gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()



class ExperienceForm(ModelForm):
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError(
                "Nama pengalaman tidak boleh hanya berisi tag HTML.", code="required"
            )
        return title

    def clean_description(self):
        description = strip_tags(self.cleaned_data["description"]).strip()
        if not description:
            raise ValidationError(
                "Deskripsi pengalaman tidak boleh hanya berisi tag HTML.", code="required"
            )
        return description

    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "ended_at",
            "thumbnail",
        ]

        labels = {
            "title": "Nama Pengalaman",
            "description": "Deskripsi Pengalaman",
            "category": "Kategori Pengalaman",
            "ended_at": "Tanggal Berakhir (Opsional)",
            "thumbnail": "URL Gambar Pengalaman (Opsional)",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Contoh: Software Engineer Intern",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalamanmu",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "ended_at": DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/gambar-pengalaman.jpg",
                }
            ),
        }
