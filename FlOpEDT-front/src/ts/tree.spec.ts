import { TreeNode, Tree } from './tree'
import { describe, expect, it } from 'vitest'
import { map, reverse } from 'lodash'

describe('Tree utils', () => {
  it('stores a reasonable list', () => {
    expect.assertions(4)
    const tree = new Tree()
    tree.addNodes([
        {id: 5, parentId:1},
        {id: 1, parentId:null},
        {id: 2, parentId:1},
    ])
    expect(Object.keys(tree.byId).length).toBe(3)
    expect(tree.byId[5]).toBeDefined()
    expect(tree.byId[1]).toBeDefined()
    expect(tree.byId[2]).toBeDefined()
  })

  it('builds correct children and parents', () => {
    expect.assertions(9)
    const tree = new Tree()
    tree.addNodes([
        {id: 5, parentId:1},
        {id: 1, parentId:null},
        {id: 2, parentId:1},
        {id: 8, parentId:5}
    ])
    expect(tree.byId[1].children.length).toBe(2)
    expect(map(tree.byId[1].children, c => c.id)).toEqual(expect.arrayContaining([5, 2]))
    expect(tree.byId[2].children.length).toBe(0)
    expect(map(tree.byId[5].children, c => c.id)).toEqual([8])
    expect(tree.byId[5].parent).toBe(tree.byId[1])

    expect(tree.byId[5].parent?.id).toBe(1)
    expect(tree.byId[1].parent).toBeNull()
    expect(tree.byId[2].parent?.id).toBe(1)
    expect(tree.byId[8].parent?.id).toBe(5)
  })

  it('builds correct descendants', () => {
    expect.assertions(18)
    const tree = new Tree()
    tree.addNodes([
        {id: 5, parentId:1},
        {id: 1, parentId:null},
        {id: 2, parentId:1},
        {id: 8, parentId:5}
    ])

    expect(tree.byId[1].children.length).toBe(2)
    expect(map(tree.byId[1].children, c => c.id)).toEqual(expect.arrayContaining([5, 2]))
    expect(tree.byId[2].children.length).toBe(0)
    expect(map(tree.byId[5].children, c => c.id)).toEqual([8])
    expect(tree.byId[5].parent).toBe(tree.byId[1])

    expect(tree.byId[1].descendants.length).toBe(3)
    expect(map(tree.byId[1].descendants, c => c.id)).toEqual(expect.arrayContaining([2, 5, 8]))
    expect(tree.byId[1].ancestors.length).toBe(0)
    expect(tree.byId[5].descendants.length).toBe(1)
    expect(map(tree.byId[5].descendants, c => c.id)).toEqual(expect.arrayContaining([8]))
    expect(tree.byId[5].ancestors.length).toBe(1)
    expect(map(tree.byId[5].ancestors, c => c.id)).toEqual(expect.arrayContaining([1]))
    expect(tree.byId[8].descendants.length).toBe(0)
    expect(tree.byId[8].ancestors.length).toBe(2)
    expect(map(tree.byId[8].ancestors, c => c.id)).toEqual(expect.arrayContaining([1, 5]))
    expect(tree.byId[2].descendants.length).toBe(0)
    expect(tree.byId[2].ancestors.length).toBe(1)
    expect(map(tree.byId[2].ancestors, c => c.id)).toEqual(expect.arrayContaining([1]))

  })

  it('sorts the children correctly', () => {
    expect.assertions(2)
    const tree = new Tree()

    const linkIdUps = [
      {id: 5, parentId:1},
      {id: 1, parentId:null},
      {id: 2, parentId:1},
      {id: 8, parentId:5}
    ]

    tree.addNodes(linkIdUps)
    tree.sortChildren()
    expect(map(tree.byId[1].children, c => c.id)).toEqual([5, 2])

    const reverseTree = new Tree()
    reverse(linkIdUps)
    reverseTree.addNodes(linkIdUps)
    reverseTree.sortChildren()
    expect(map(reverseTree.byId[1].children, c => c.id)).toEqual([2, 5])
    
  })


  it("computes correctly levels", () => {
    expect.assertions(8)
    const tree = new Tree()
    tree.addNodes([
        {id: 5, parentId:1},
        {id: 1, parentId:null},
        {id: 2, parentId:1},
        {id: 8, parentId:5}
    ])
    tree.computeDepthMin()
    expect(tree.byId[1].depthMin).toBe(0)
    expect(tree.byId[5].depthMin).toBe(1)
    expect(tree.byId[2].depthMin).toBe(1)
    expect(tree.byId[8].depthMin).toBe(2)
    tree.computeDepthMax()
    expect(tree.byId[1].depthMax).toBe(0)
    expect(tree.byId[5].depthMax).toBe(1)
    expect(tree.byId[2].depthMax).toBe(2)
    expect(tree.byId[8].depthMax).toBe(2)

  })
  it("computes correctly the number of leaves", () => {
    expect.assertions(5)
    const tree = new Tree()
    tree.addNodes([
        {id: 5, parentId:1},
        {id: 1, parentId:null},
        {id: 2, parentId:1},
        {id: 8, parentId:5},
        {id: 3, parentId:5}
    ])
    tree.countLeaves()
    expect(tree.byId[1].nLeaves).toBe(3)
    expect(tree.byId[5].nLeaves).toBe(2)
    expect(tree.byId[2].nLeaves).toBe(1)
    expect(tree.byId[8].nLeaves).toBe(1)
    expect(tree.byId[3].nLeaves).toBe(1)


  })


  it.todo('throws an error when cycle')

  it('throws an error when unknown node as a parentId', () => {
    expect.assertions(1)
    const tree = new Tree()
    expect(() => tree.addNodes([
        {id: 1, parentId:null},
        {id: 2, parentId:3},
    ])).toThrowError('unknown')
  })

  it('throws an error when multi-root', () => {
    expect.assertions(1)
    const tree = new Tree()
    expect(() => tree.addNodes([
        {id: 1, parentId:null},
        {id: 2, parentId:1},
        {id: 5, parentId:null},
    ])).toThrowError('multi')
  })
})
