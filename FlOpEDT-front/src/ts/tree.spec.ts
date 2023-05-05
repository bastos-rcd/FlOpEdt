import { TreeNode, Tree } from './tree'
import { describe, expect, it } from 'vitest'
import { map } from 'lodash'

describe('Tree utils', () => {
  it('stores a reasonable list', () => {
    expect.assertions(4)
    const tree = new Tree<{id:number, pouet:string, parent:number|null}>()
    tree.addNodes([
        {id: 5, pouet: "truc5", parent:1},
        {id: 1, pouet: "truc1", parent:null},
        {id: 2, pouet: "truc2", parent:1},
    ])
    expect(Object.keys(tree.byId).length).toBe(3)
    expect(tree.byId[5]).toBeDefined()
    expect(tree.byId[1]).toBeDefined()
    expect(tree.byId[2]).toBeDefined()
  })

  it('builds correct children and parents', () => {
    expect.assertions(9)
    const tree = new Tree<{id:number, pouet:string, parent:number|null}>()
    tree.addNodes([
        {id: 5, pouet: "truc5", parent:1},
        {id: 1, pouet: "truc1", parent:null},
        {id: 2, pouet: "truc2", parent:1},
        {id: 8, pouet: "truc8", parent:5}
    ])
    expect(tree.byId[1].children.length).toBe(2)
    expect(map(tree.byId[1].children, c => c.data.id)).toEqual(expect.arrayContaining([5, 2]))
    expect(tree.byId[2].children.length).toBe(0)
    expect(map(tree.byId[5].children, c => c.data.id)).toEqual([8])
    expect(tree.byId[5].parent).toBe(tree.byId[1])

    expect(tree.byId[5].parent?.data.id).toBe(1)
    expect(tree.byId[1].parent).toBeNull()
    expect(tree.byId[2].parent?.data.id).toBe(1)
    expect(tree.byId[8].parent?.data.id).toBe(5)
  })

  it('builds correct descendants', () => {
    expect.assertions(18)
    const tree = new Tree<{id:number, pouet:string, parent:number|null}>()
    tree.addNodes([
        {id: 5, pouet: "truc5", parent:1},
        {id: 1, pouet: "truc1", parent:null},
        {id: 2, pouet: "truc2", parent:1},
        {id: 8, pouet: "truc8", parent:5}
    ])

    expect(tree.byId[1].children.length).toBe(2)
    expect(map(tree.byId[1].children, c => c.data.id)).toEqual(expect.arrayContaining([5, 2]))
    expect(tree.byId[2].children.length).toBe(0)
    expect(map(tree.byId[5].children, c => c.data.id)).toEqual([8])
    expect(tree.byId[5].parent).toBe(tree.byId[1])

    expect(tree.byId[1].descendants.length).toBe(3)
    expect(map(tree.byId[1].descendants, c => c.data.id)).toEqual(expect.arrayContaining([2, 5, 8]))
    expect(tree.byId[1].ancestors.length).toBe(0)
    expect(tree.byId[5].descendants.length).toBe(1)
    expect(map(tree.byId[5].descendants, c => c.data.id)).toEqual(expect.arrayContaining([8]))
    expect(tree.byId[5].ancestors.length).toBe(1)
    expect(map(tree.byId[5].ancestors, c => c.data.id)).toEqual(expect.arrayContaining([1]))
    expect(tree.byId[8].descendants.length).toBe(0)
    expect(tree.byId[8].ancestors.length).toBe(2)
    expect(map(tree.byId[8].ancestors, c => c.data.id)).toEqual(expect.arrayContaining([1, 5]))
    expect(tree.byId[2].descendants.length).toBe(0)
    expect(tree.byId[2].ancestors.length).toBe(1)
    expect(map(tree.byId[2].ancestors, c => c.data.id)).toEqual(expect.arrayContaining([1]))

  })

  it('sorts the children correctly', () => {
    expect.assertions(3)
    const tree = new Tree<{id:number, pouet:string, parent:number|null}>()
    tree.addNodes([
        {id: 5, pouet: 2, parent:1},
        {id: 1, pouet: 1, parent:null},
        {id: 2, pouet: 5, parent:1},
        {id: 8, pouet: 8, parent:5}
    ])
    tree.sortChildrenBy("id")
    expect(map(tree.byId[1].children, c => c.data.id)).toEqual([2, 5])
    tree.sortChildrenBy("pouet")
    expect(map(tree.byId[1].children, c => c.data.id)).toEqual([5, 2])
    tree.sortChildrenBy("aze")
    expect(map(tree.byId[1].children, c => c.data.id)).toEqual([5, 2])
  })

  it.todo('throws an error when cycle')

  it('throws an error when unknown node as a parent', () => {
    expect.assertions(1)
    const tree = new Tree()
    expect(() => tree.addNodes([
        {id: 1, pouet: "truc", parent:null},
        {id: 2, pouet: "truc", parent:3},
    ])).toThrowError('unknown')
  })

  it('throws an error when multi-root', () => {
    expect.assertions(1)
    const tree = new Tree()
    expect(() => tree.addNodes([
        {id: 1, pouet: "machin", parent:null},
        {id: 2, pouet: "truc", parent:1},
        {id: 5, pouet: "trucz", parent:null},
    ])).toThrowError('multi')
  })
})
