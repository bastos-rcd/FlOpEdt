import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { ScheduledCourse } from '@/ts/type'

describe('Availibility store utils', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it.todo('converts a scheduledCourse object into a course object')
  it.todo('converts a course object into a scheduledCourse object')
  it.todo('converts a scheduledCourse object into a course object and back')
  it.todo('converts a course object into a scheduledCourse object and back')
})
