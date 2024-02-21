from django.db import models
from base.models.courses import Course
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=7)

    class Meta:
        verbose_name = _("department")
        verbose_name_plural = _("departments")

    def __str__(self):
        return self.abbrev

# TODO : Adopter l'écriture US plutôt que UK (=> TrainingProgram)
class TrainingProgramme(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _("training programme")
        verbose_name_plural = _("training programmes")

    def __str__(self):
        return self.abbrev


class GroupType(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _("group type")
        verbose_name_plural = _("groupe types")

    def __str__(self):
        return self.name


class GenericGroup(models.Model):
    # TODO : should not include "-" nor "|"
    name = models.CharField(max_length=100)
    train_prog = models.ForeignKey('TrainingProgramme', on_delete=models.CASCADE)
    type = models.ForeignKey('GroupType', on_delete=models.CASCADE, null=True)
    size = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (("name", "train_prog"),)
        verbose_name = _("generic group")
        verbose_name_plural = _("generic groups")

    @property
    def full_name(self):
        return self.train_prog.abbrev + "-" + self.name

    def __str__(self):
        return self.full_name

    def ancestor_groups(self):
        if self.is_structural:
            return self.structuralgroup.ancestor_groups()
        return set()

    def descendants_groups(self):
        if self.is_structural:
            return self.structuralgroup.descendants_groups()
        return set()

    @property
    def is_structural(self):
        try:
            self.structuralgroup
            return True
        except:
            return False

    @property
    def is_transversal(self):
        try:
            self.transversalgroup
            return True
        except:
            return False


class StructuralGroup(GenericGroup):
    basic = models.BooleanField(verbose_name=_('Basic group?'), default=False)
    parent_groups = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="children_groups")
    generic = models.OneToOneField('GenericGroup', on_delete=models.CASCADE, parent_link=True)

    def ancestor_groups(self):
        """
        :return: the set of all StructuralGroup containing self (self not included)
        """
        ancestors = set(self.parent_groups.all())

        for gp in self.parent_groups.all():

            for new_gp in gp.ancestor_groups():
                ancestors.add(new_gp)

        return ancestors

    def and_ancestors(self):
        """
        :return: the set of all StructuralGroup containing self (self included)
        """
        return {self} | self.ancestor_groups()

    def descendants_groups(self):
        """
        :return: the set of all StructuralGroup contained by self (self not included)
        """
        descendants = set()

        for gp in StructuralGroup.objects.filter(train_prog=self.train_prog):
            if self in gp.ancestor_groups():
                descendants.add(gp)

        return descendants

    def basic_groups(self):
        s = set(g for g in self.descendants_groups() | {self} if g.basic)
        return s

    def connected_groups(self):
        """
        :return: the set of all StructuralGroup that have a non empty intersection with self (self included)
        """
        return {self} | self.descendants_groups() | self.ancestor_groups()

    @property
    def transversal_conflicting_groups(self):
        """
        :return: the set of all TransversalGroup containing self
        """
        return TransversalGroup.objects.filter(conflicting_groups__in=self.connected_groups())

    class Meta:
        verbose_name = _("structural group")
        verbose_name_plural = _("structural groups")

class TransversalGroup(GenericGroup):
    conflicting_groups = models.ManyToManyField("base.StructuralGroup", blank=True)
    parallel_groups = models.ManyToManyField('self', symmetrical=True, blank=True)
    generic = models.OneToOneField('GenericGroup', on_delete=models.CASCADE, parent_link=True)

    class Meta:
        verbose_name = _("transversal group")
        verbose_name_plural = _("transversal groups")

    def nb_of_courses(self, week):
        return len(Course.objects.filter(week=week, groups=self))

    def time_of_courses(self, week):
        t = 0
        for c in Course.objects.filter(week=week, groups=self):
            t += c.duration
        return t