import { createPinia, setActivePinia, storeToRefs } from 'pinia'
import { beforeEach, expect, vi, describe, it, afterEach } from 'vitest'
import { useGroupStore } from './group'
import { Department } from '@/ts/type'

vi.mock('./group.ts')
describe('Group store', () => {
  beforeEach(() => {
    // creates a fresh pinia and make it active so it's automatically picked
    // up by any useStore() call without having to pass it to it:
    // `useStore(pinia)`
    setActivePinia(createPinia())
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('Populates columnIds of Structural Groups', () => {
    expect.assertions(10)
    const groupStore = useGroupStore()
    const { fetchedStructuralGroups } = storeToRefs(groupStore)
    expect(fetchedStructuralGroups.value.length).toBe(12)
    expect(fetchedStructuralGroups.value.find((gp) => gp.id === 1)?.columnIds.length).toBe(0)

    void groupStore.fetchGroups(new Department())
    const CE = fetchedStructuralGroups.value.find((gp) => gp.id === 1)
    expect(fetchedStructuralGroups.value.length).toBe(12)
    expect(CE?.id).toBe(1)
    expect(CE?.columnIds.length).toBe(8)
    expect(CE?.columnIds).toEqual([5, 6, 7, 8, 9, 10, 11, 12])
    const tpA1 = fetchedStructuralGroups.value.find((gp) => gp.id === 5)
    expect(tpA1?.columnIds.length).toBe(1)
    expect(tpA1?.columnIds).toEqual([5])
    const tdB = fetchedStructuralGroups.value.find((gp) => gp.id === 3)
    expect(tdB?.columnIds.length).toBe(3)
    expect(tdB?.columnIds).toEqual([7, 8, 9])
  })

  it('Populates columIds of Transversal Groups', () => {
    const groupStore = useGroupStore()
    const { fetchedTransversalGroups } = storeToRefs(groupStore)
    void groupStore.fetchGroups(new Department())
    expect(fetchedTransversalGroups.value.length).toBe(6)
    const all1 = fetchedTransversalGroups.value.find((gp) => gp.id === 16)
    const all2 = fetchedTransversalGroups.value.find((gp) => gp.id === 17)
    expect(all1?.name).toBe('Allemand 1')
    expect(all2?.name).toBe('Allemand 2')
    expect(all1?.columnIds).toEqual([5, 6, 7, 8, 9])
    expect(all1?.columnIds).toEqual(all2?.columnIds)
    const quech = fetchedTransversalGroups.value.find((gp) => gp.id === 18)
    expect(quech?.name).toBe('Quechua 1')
    expect(quech?.columnIds).toEqual([12])
  })
})
