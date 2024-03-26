from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.

class BreakingNews(models.Model):
    department =  models.ForeignKey('base.Department',
                                    on_delete=models.CASCADE,
                                    null=True)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    # x_beg and x_end in terms of day width
    x_beg = models.FloatField(default=2., blank=True)
    x_end = models.FloatField(default=3., blank=True)
    y = models.PositiveSmallIntegerField(null=True, default=None,
                                         blank=True)
    txt = models.CharField(max_length=200)
    is_linked = models.URLField(max_length=200, null=True, blank=True, default=None)
    fill_color = ColorField(default='#228B22')
    # stroke color
    strk_color = ColorField(default='#000000')

    def __str__(self):
        return '@(' + str(self.x_beg) + '--' + str(self.x_end) \
               + ',' + str(self.y) \
               + ')-W' + str(self.week) + ',Y' \
               + str(self.year) + ': ' + str(self.txt)


class TutorDisplay(models.Model):
    tutor = models.OneToOneField('people.Tutor', related_name='display', on_delete=models.CASCADE)
    color_bg = ColorField(default="#FF0000")
    color_txt = ColorField(default="#000000")

    def __str__(self):
        return str(self.tutor) + ' -> BG: ' + str(self.color_bg) \
               + ' ; TXT: ' + str(self.color_txt)


class ModuleDisplay(models.Model):
    module = models.OneToOneField('base.Module',
                                  related_name='display',
                                  on_delete=models.CASCADE)
    color_bg = ColorField(default="#D3D3D3")
    color_txt = ColorField(default="#000000")

    def __str__(self):
        return f"{self.module} -> BG: {self.color_bg} ; TXT: {self.color_txt}"


class TrainingProgrammeDisplay(models.Model):
    training_programme = models.OneToOneField('base.TrainingProgramme',
                                              related_name='display',
                                              on_delete=models.CASCADE)
    row = models.PositiveSmallIntegerField()
    short_name = models.CharField(max_length=20, default="")

    def __str__(self):
        return f"{self.training_programme} : Row {self.row} ; " + \
            f"Name {self.short_name}"


class GroupDisplay(models.Model):
    group = models.OneToOneField('base.StructuralGroup',
                                 related_name='display',
                                 on_delete=models.CASCADE)
    button_height = models.PositiveIntegerField(null=True, default=None)
    button_txt = models.CharField(max_length=20, null=True, default=None)

    def __str__(self):
        return f"{self.group} -> BH: {self.button_height} ; " + \
            f"BTXT: {self.button_txt}"
