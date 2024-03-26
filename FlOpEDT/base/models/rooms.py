from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoomType(models.Model):
    department = models.ForeignKey(
        "base.Department", on_delete=models.CASCADE, null=True
    )
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = _("room type")
        verbose_name_plural = _("room types")

    def __str__(self):
        return self.name

    def basic_rooms(self):
        s = set(b for r in self.members.all() for b in r.and_subrooms() if b.is_basic)
        return s


class RoomAttribute(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True)

    def is_boolean(self):
        return hasattr(self, "booleanroomattribute")

    def is_numeric(self):
        return hasattr(self, "numericroomattribute")

    def __str__(self):
        return self.name


class BooleanRoomAttribute(RoomAttribute):
    attribute = models.OneToOneField(
        RoomAttribute, parent_link=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name} (boolean)"


class NumericRoomAttribute(RoomAttribute):
    attribute = models.OneToOneField(
        RoomAttribute, parent_link=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name} (numeric)"


class BooleanRoomAttributeValue(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    attribute = models.ForeignKey("BooleanRoomAttribute", on_delete=models.CASCADE)
    value = models.BooleanField()


class NumericRoomAttributeValue(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    attribute = models.ForeignKey("NumericRoomAttribute", on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=7, decimal_places=2)


class Room(models.Model):
    name = models.CharField(max_length=50)
    types = models.ManyToManyField(RoomType, blank=True, related_name="members")
    subroom_of = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="subrooms"
    )
    departments = models.ManyToManyField("base.Department")

    class Meta:
        verbose_name = _("room")
        verbose_name_plural = _("rooms")

    @property
    def is_basic(self):
        return self.subrooms.count() == 0

    def and_subrooms(self):
        ret = {self}
        for sub in self.subrooms.all():
            ret |= sub.and_subrooms()
        return ret

    def basic_rooms(self):
        s = set(r for r in self.and_subrooms() if r.is_basic)
        return s

    def and_overrooms(self):
        ret = {self}
        for over in self.subroom_of.all():
            ret |= over.and_overrooms()
        return ret

    def __str__(self):
        return self.name

    def str_extended(self):
        return (
            f"{self.name}, "
            + f"Types: {[t.name for t in self.types.all()]}, "
            + f"Depts: {self.departments.all()}, "
            + f"Is in: {[rg.name for rg in self.subroom_of.all()]}"
        )

    def related_rooms(self):
        result = set()
        for r in self.basic_rooms():
            result |= r.and_overrooms()
        return result


class RoomSort(models.Model):
    for_type = models.ForeignKey(
        RoomType, blank=True, null=True, related_name="+", on_delete=models.CASCADE
    )
    prefer = models.ForeignKey(
        Room, blank=True, null=True, related_name="+", on_delete=models.CASCADE
    )
    unprefer = models.ForeignKey(
        Room, blank=True, null=True, related_name="+", on_delete=models.CASCADE
    )
    tutor = models.ForeignKey(
        "people.Tutor",
        related_name="abcd",
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.for_type}: {self.tutor} prefers {self.prefer} to {self.unprefer}"


class RoomPonderation(models.Model):
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    room_types = ArrayField(models.PositiveSmallIntegerField())
    ponderations = ArrayField(models.PositiveSmallIntegerField(), null=True)
    basic_rooms = models.ManyToManyField("Room")

    def save(self, *args, **kwargs):
        super(RoomPonderation, self).save(*args, **kwargs)
        self.add_basic_rooms()

    def add_basic_rooms(self):
        RT = RoomType.objects.filter(id__in=self.room_types)
        for rt in RT:
            for basic_room in rt.basic_rooms():
                self.basic_rooms.add(basic_room)

    def get_room_types_set(self):
        return set(RoomType.objects.filter(id__in=self.room_types))
