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
import { Room } from '@/ts/type';
import ScheduleView from './ScheduleView.vue'
import { ref } from 'vue'
import FilterSelector from '@/components/utils/FilterSelector.vue';


const roomsSelected = ref<Room[] | null>([])

const rooms = [
  {
    "id": 1,
    "name": "E001",
    "subroom_of": [],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 1,
        "name": "E001",
        "is_basic": true
      }
    ]
  },
  {
    "id": 2,
    "name": "E002",
    "subroom_of": [],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 2,
        "name": "E002",
        "is_basic": true
      }
    ]
  },
  {
    "id": 3,
    "name": "E003",
    "subroom_of": [],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 3,
        "name": "E003",
        "is_basic": true
      }
    ]
  },
  {
    "id": 4,
    "name": "E004",
    "subroom_of": [],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 4,
        "name": "E004",
        "is_basic": true
      }
    ]
  },
  {
    "id": 5,
    "name": "E005",
    "subroom_of": [],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 5,
        "name": "E005",
        "is_basic": true
      }
    ]
  },
  {
    "id": 6,
    "name": "E008",
    "subroom_of": [],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 6,
        "name": "E008",
        "is_basic": true
      }
    ]
  },
  {
    "id": 7,
    "name": "E101",
    "subroom_of": [
      139
    ],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 7,
        "name": "E101",
        "is_basic": true
      }
    ]
  },
  {
    "id": 8,
    "name": "E102",
    "subroom_of": [
      137,
      139
    ],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 8,
        "name": "E102",
        "is_basic": true
      }
    ]
  },
  {
    "id": 9,
    "name": "E103",
    "subroom_of": [
      137
    ],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 9,
        "name": "E103",
        "is_basic": true
      }
    ]
  },
  {
    "id": 10,
    "name": "E104",
    "subroom_of": [
      138
    ],
    "departments": [
      45
    ],
    "is_basic": true,
    "basic_rooms": [
      {
        "id": 10,
        "name": "E104",
        "is_basic": true
      }
    ]
  },]

</script>
<style scoped>
.filters {
  width: 200px;
}
</style>
<docs lang="md">
# Welcome

This is a demo book using Vue 3.

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>
