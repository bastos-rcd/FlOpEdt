import { Timestamp } from '@quasar/quasar-ui-qcalendar'

export interface Availability {
  id: number
  duration: number
  start: Timestamp
  value: number
  type: string
  //dataId: number
  userName: string
}

// Gathers Course and ScheduledCourse from the back
export interface Course {
  id: number // id of ScheduledCourse
  no: number
  room: number
  start: Timestamp
  end: Timestamp
  tutorId: number
  suppTutorIds: number[]
  module: number
  groupIds: number[]
  courseTypeId: number
  roomTypeId: number
  graded: boolean
  workCopy: number
}

// Note sur les groupes : sur le serveur, en base, l'id d'un Structural ou TransversalGroup
// doit être le même que l'id de son parent Generic

// Est-ce qu'on a vraiment besoin de savoir dans le front si un groupe est structural ou transversal ?

export interface Group {
  id: number
  name: string
  size: number
  trainProgId: number
  type: string // structural or transversal
  parentsId?: number[]
  conflictingGroupIds?: number[]
  parallelGroupIds?: number[]
  columnIds: number[] // cf calendar/types.ts: CalendarColumn
}

// Nouvelle entrée pour les modules: Rajouter les IDs

export interface Module {
  id: number
  name: string
  abbrev: string
  headId?: number //Personne responsable du module
  url: string | null
  trainProgId: number
  description?: string
}

export interface Room {
  id: number
  abbrev: string
  name: string
  subroomIdOf: number[]
  departmentIds: number[]
}

// Association groupe - colonnes ? NON
// Record<number, number[]>  // groupId -> columnIds

// Course {
//   id: number
//   no: number
//   tutorId: number
//   suppTutorIds: number[]
//   moduleId: number
// }

export interface TrainingProgramme {
  id: number
  name: string
  abbrev: string
  departmentId: number
}

export interface User {
  id: number
  username: string
  firstname: string
  lastname: string
  email: string
  type: string
  departments: Array<{ departmentId: number; rights: string }>
}
