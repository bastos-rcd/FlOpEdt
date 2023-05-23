<template>
  <Story>
    <Variant title="Test with Filter">
      <div>
        <div class="filters">
          <FilterSelector
            :items="rooms"
            filterSelectorUndefinedLabel="Select a room"
            v-model:selectedItems="roomsSelected"
            itemVariableName="name"
            :multiple="true"
          />
          <p><q-badge v-for="r in roomsSelected" rounded color="red" :label="r.name" /></p>
        </div>
      </div>
      <ScheduleView />
    </Variant>
    <Variant title="Use case">
      <ScheduleView />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import { Room } from '@/ts/type'
import ScheduleView from './ScheduleView.vue'
import { ref } from 'vue'
import FilterSelector from '@/components/utils/FilterSelector.vue'

const roomsSelected = ref<Room[] | null>([])

const rooms = [
  {
    id: 1,
    name: 'E001',
    subroom_of: [],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 1,
        name: 'E001',
        is_basic: true,
      },
    ],
  },
  {
    id: 2,
    name: 'E002',
    subroom_of: [],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 2,
        name: 'E002',
        is_basic: true,
      },
    ],
  },
  {
    id: 3,
    name: 'E003',
    subroom_of: [],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 3,
        name: 'E003',
        is_basic: true,
      },
    ],
  },
  {
    id: 4,
    name: 'E004',
    subroom_of: [],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 4,
        name: 'E004',
        is_basic: true,
      },
    ],
  },
  {
    id: 5,
    name: 'E005',
    subroom_of: [],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 5,
        name: 'E005',
        is_basic: true,
      },
    ],
  },
  {
    id: 6,
    name: 'E008',
    subroom_of: [],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 6,
        name: 'E008',
        is_basic: true,
      },
    ],
  },
  {
    id: 7,
    name: 'E101',
    subroom_of: [139],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 7,
        name: 'E101',
        is_basic: true,
      },
    ],
  },
  {
    id: 8,
    name: 'E102',
    subroom_of: [137, 139],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 8,
        name: 'E102',
        is_basic: true,
      },
    ],
  },
  {
    id: 9,
    name: 'E103',
    subroom_of: [137],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 9,
        name: 'E103',
        is_basic: true,
      },
    ],
  },
  {
    id: 10,
    name: 'E104',
    subroom_of: [138],
    departments: [45],
    is_basic: true,
    basic_rooms: [
      {
        id: 10,
        name: 'E104',
        is_basic: true,
      },
    ],
  },
]
</script>
<style scoped>
.filters {
  width: 200px;
}
</style>
<docs lang="md">
Département donné

0 Roomtypes + Room (tout)

1 Groupes

2 ScheduledCourse minimal

2 -> 3 avec la liste des id_module : Module (sauf description, period) + ModuleDisplay
2 -> 4 Profs (id, username, first_name, last_name, email) + TutorDisplay

1, 2 : afficher sans info (rectangles incolores seulement)
0, 1, 2, 3, 4 : afficher sans modif

Double-click

- 2 -> 6 Détails cours

Annexes:

- 100 : Bknews
- 101 : Regen

Si modification :

- 2 -> 7 dispos prof (cf modules)
- 2 -> 8 dispos salles (résa + salles partagées + )
- 9 contraintes start_time


cours dans un autre dépt

## TODO :
```ts
Room {
  id: number
  name: string
  subroom_of: number[]
  is_basic: boolean
  department: number[]
}

// ScheduleView.vue
Group {
  id: number
  name: string
  columnIds: number[]
  parentId: number
  size: number
}

// Association groupe - colonnes ? NON
// Record<number, number[]>  // groupId -> columnIds

// Course {
//   id: number
//   no: number
//   tutorId: number
//   suppTutorIds: number[]
//   moduleId: number
//  
// }

// Gathers Course and ScheduledCourse from the back
Course {
  id: number // id of ScheduledCourse
  no: number
  courseTypeId: number // ??
  courseId: number
  roomIds: number[]
  start_time: Timestamp
  end_time: Timestamp
  tutorId: number
  suppTutorIds: number[]
  groupIds: number[]
  moduleId: number
  graded: boolean
}
```

```js
Tutor {
id: number,
username: string,
firstname: string,
lastname: string
}
```


Nouvelle entrée pour les modules: Rajouter les IDs 

```ts
Module
  {
    id: number,
    name: string,
    abbrev: string,
    head: number, //Personne responsable du module
    url: string | null,
    trainProgId: number
  }

//Actuellement
Module
  {
    name: string,
    abbrev: string,
    head: number, //Personne responsable du module
    ppn: string,
    url: string,
    train_prog: TrainingProgramme
    period: {
      starting_week: number,
      ending_week: number,
      name: string
    }
  },


// Note sur les groupes : sur le serveur, en base, l'id d'un Structural ou TransversalGroup
// doit être le même que l'id de son parent Generic

// Est-ce qu'on a vraiment besoin de savoir dans le front si un groupe est structural ou transversal ?

Group {
  id: number
  name: string
  size: number
  trainProgId: number
  parentGroupIds?: number[]
  conflictingGroupIds?: number[]
  parallelGroupIds?: number[]
}

// liste de Group ?
// computed:
//   - Structural
//   - Transversal
```

```ts
TrainingProgramme
  {
    id: number,
    name: string,
    abbrev: string,
    department: number
  },
```

## Dispos prof :

- Toutes les dispos de tous les profs de tous les modules qui sont présents dans la période
- Quand modification de prof pour un cours dont on a pas les dispos
  - dispos en grisées
  - appel immédiat pour récupérer les dispos
  - acceptation ou non

## Dispos salles :

- Toutes les dispos de toutes les salles qui sont disponibles au département ou à tous les départements
</docs>
