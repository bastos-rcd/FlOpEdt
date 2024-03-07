from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly


class DjangoModelPermissionsOrReadOnly(DjangoModelPermissionsOrAnonReadOnly):
    perms_map = DjangoModelPermissionsOrAnonReadOnly.perms_map | {"GET": [], "HEAD": []}
