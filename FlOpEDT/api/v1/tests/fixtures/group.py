# Fixtures use to unuse arguments...
# pylint: disable=unused-argument

import pytest

from ..factories.group import StructuralGroupDummyFactory


@pytest.fixture
def make_classical_structural_groups(db):
    def from_training_programme(tp):
        groups = []
        groups.append(StructuralGroupDummyFactory.create(train_prog=tp, name="CM"))
        for i in range(2):
            group = StructuralGroupDummyFactory.create(train_prog=tp, name=f"TD{i}")
            group.parent_groups.add(groups[0])
            for j in range(2):
                subgroup = StructuralGroupDummyFactory.create(
                    train_prog=tp, name=f"TP{i}{j}", basic=True
                )
                subgroup.parent_groups.add(group)
                groups.append(subgroup)
            groups.append(group)
        return groups

    return from_training_programme
