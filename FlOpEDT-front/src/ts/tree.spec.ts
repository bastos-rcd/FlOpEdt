import { ITreeNode, Tree } from './tree'
import { describe, expect, it } from 'vitest'
import _ from 'lodash'

describe('Tree utils', () => {
  it('stores a reasonable list', () => {
    expect.assertions(4)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
      ],
      []
    )
    expect(Object.keys(tree.byId).length).toBe(3)
    expect(tree.byId[5]).toBeDefined()
    expect(tree.byId[1]).toBeDefined()
    expect(tree.byId[2]).toBeDefined()
  })

  it('builds correct children and parents', () => {
    expect.assertions(12)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
      ],
      []
    )
    expect(tree.byId[1].children.length).toBe(2)
    expect(_.map(tree.byId[1].children, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([5, 2]))
    expect(tree.byId[2].children.length).toBe(0)
    expect(_.map(tree.byId[5].children, (c: ITreeNode) => c.id)).toEqual([8])
    expect(tree.byId[5].parents.length).toBe(1)
    expect(tree.byId[5].parents[0]).toBe(tree.byId[1])

    expect(tree.byId[5].parents[0].id).toBe(1)
    expect(tree.byId[1].parents.length).toBe(0)
    expect(tree.byId[2].parents.length).toBe(1)
    expect(tree.byId[8].parents.length).toBe(1)
    expect(tree.byId[2].parents[0].id).toBe(1)
    expect(tree.byId[8].parents[0].id).toBe(5)
  })

  it('builds correct descendants', () => {
    expect.assertions(19)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
      ],
      []
    )

    expect(tree.byId[1].children.length).toBe(2)
    expect(_.map(tree.byId[1].children, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([5, 2]))
    expect(tree.byId[2].children.length).toBe(0)
    expect(_.map(tree.byId[5].children, (c: ITreeNode) => c.id)).toEqual([8])
    expect(tree.byId[5].parents.length).toBe(1)
    expect(tree.byId[5].parents[0]).toBe(tree.byId[1])

    expect(tree.byId[1].descendants.length).toBe(3)
    expect(_.map(tree.byId[1].descendants, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([2, 5, 8]))
    expect(tree.byId[1].ancestors.length).toBe(0)
    expect(tree.byId[5].descendants.length).toBe(1)
    expect(_.map(tree.byId[5].descendants, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([8]))
    expect(tree.byId[5].ancestors.length).toBe(1)
    expect(_.map(tree.byId[5].ancestors, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([1]))
    expect(tree.byId[8].descendants.length).toBe(0)
    expect(tree.byId[8].ancestors.length).toBe(2)
    expect(_.map(tree.byId[8].ancestors, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([1, 5]))
    expect(tree.byId[2].descendants.length).toBe(0)
    expect(tree.byId[2].ancestors.length).toBe(1)
    expect(_.map(tree.byId[2].ancestors, (c: ITreeNode) => c.id)).toEqual(expect.arrayContaining([1]))
  })

  it('sorts the children correctly', () => {
    expect.assertions(2)
    const tree = new Tree()

    const linkIdUps = [
      { id: 5, parentsId: [1] },
      { id: 1, parentsId: [] },
      { id: 2, parentsId: [1] },
      { id: 8, parentsId: [5] },
    ]

    tree.addNodes(linkIdUps, [])
    tree.sortFamily()
    expect(_.map(tree.byId[1].children, (c: ITreeNode) => c.id)).toEqual([5, 2])

    const reverseTree = new Tree()
    _.reverse(linkIdUps)
    reverseTree.addNodes(linkIdUps, [])
    reverseTree.sortFamily()
    expect(_.map(reverseTree.byId[1].children, (c: ITreeNode) => c.id)).toEqual([2, 5])
  })

  it('computes correctly levels', () => {
    expect.assertions(8)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
      ],
      []
    )
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

  it('computes correctly levels', () => {
    expect.assertions(12)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
      ],
      []
    )
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
    tree.adjustDepth()
    expect(tree.byId[1].depthMax).toBe(0)
    expect(tree.byId[5].depthMax).toBe(1)
    expect(tree.byId[2].depthMax).toBe(2)
    expect(tree.byId[8].depthMax).toBe(2)
  })

  it.skip('computes correctly the number of leaves', () => {
    expect.assertions(5)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
        { id: 3, parentsId: [5] },
      ],
      []
    )
    // tree.countLeaves()
    // expect(tree.byId[1].nLeaves).toBe(3)
    // expect(tree.byId[5].nLeaves).toBe(2)
    // expect(tree.byId[2].nLeaves).toBe(1)
    // expect(tree.byId[8].nLeaves).toBe(1)
    // expect(tree.byId[3].nLeaves).toBe(1)
  })

  it('activates the right nodes', () => {
    expect.assertions(5)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
        { id: 3, parentsId: [5] },
      ],
      [3]
    )

    expect(tree.byId[3].active).toBe(true)
    expect(tree.byId[5].active).toBe(true)
    expect(tree.byId[1].active).toBe(true)
    expect(tree.byId[8].active).toBe(false)
    expect(tree.byId[2].active).toBe(false)
  })

  it('activates the right nodes (bis)', () => {
    expect.assertions(2)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 1, parentsId: [] },
        { id: 11, parentsId: [1] },
        { id: 12, parentsId: [1] },
        { id: 13, parentsId: [1] },
        { id: 111, parentsId: [11] },
        { id: 112, parentsId: [11] },
        { id: 121, parentsId: [12] },
        { id: 122, parentsId: [12] },
        { id: 131, parentsId: [13] },
        { id: 132, parentsId: [13] },
      ],
      [131, 121]
    )

    let actives = tree.getActiveIds()
    expect(actives.length).toBe(5)
    expect(actives).toEqual(expect.arrayContaining([1, 12, 13, 121, 131]))
  })

  it('activates the right nodes (ter)', () => {
    expect.assertions(4)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 1, parentsId: [] },
        { id: 11, parentsId: [1] },
        { id: 12, parentsId: [1] },
        { id: 13, parentsId: [1] },
        { id: 111, parentsId: [11] },
        { id: 112, parentsId: [11] },
        { id: 121, parentsId: [12] },
        { id: 122, parentsId: [12] },
        { id: 131, parentsId: [13] },
        { id: 132, parentsId: [13] },
      ],
      [1, 11, 12, 112, 122]
    )

    let actives = tree.getActiveIds()
    expect(actives.length).toBe(5)
    expect(actives).toEqual(expect.arrayContaining([1, 11, 12, 112, 122]))

    tree.byId[11].toggleActive()
    actives = tree.getActiveIds()
    expect(actives.length).toBe(3)
    expect(actives).toEqual(expect.arrayContaining([1, 12, 122]))
  })

  //

  it('reacts correctly to activation', () => {
    expect.assertions(6)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
        { id: 3, parentsId: [5] },
        { id: 4, parentsId: [2] },
        { id: 6, parentsId: [2] },
        { id: 11, parentsId: [1] },
        { id: 12, parentsId: [11] },
        { id: 13, parentsId: [11] },
      ],
      [3]
    )

    let actives = tree.getActiveIds()
    expect(actives.length).toBe(3)
    expect(actives).toEqual(expect.arrayContaining([1, 3, 5]))

    tree.byId[4].toggleActive()

    actives = tree.getActiveIds()
    expect(actives.length).toBe(5)
    expect(actives).toEqual(expect.arrayContaining([1, 3, 5, 4, 2]))

    tree.byId[11].toggleActive()

    actives = tree.getActiveIds()
    expect(actives.length).toBe(8)
    expect(actives).toEqual(expect.arrayContaining([1, 3, 5, 4, 2, 11, 12, 13]))
  })

  it('reacts correctly to deactivation', () => {
    expect.assertions(6)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
        { id: 3, parentsId: [5] },
        { id: 4, parentsId: [2] },
        { id: 6, parentsId: [2] },
        { id: 11, parentsId: [1] },
        { id: 12, parentsId: [11] },
        { id: 13, parentsId: [11] },
      ],
      [3, 4, 6]
    )

    let actives = tree.getActiveIds()
    expect(actives.length).toBe(6)
    expect(actives).toEqual(expect.arrayContaining([1, 3, 5, 2, 4, 6]))

    tree.byId[4].toggleActive()

    actives = tree.getActiveIds()
    expect(actives.length).toBe(5)
    expect(actives).toEqual(expect.arrayContaining([1, 3, 5, 2, 6]))

    tree.byId[5].toggleActive()

    actives = tree.getActiveIds()
    expect(actives.length).toBe(3)
    expect(actives).toEqual(expect.arrayContaining([1, 2, 6]))
  })

  it('activates correctly when all activated', () => {
    expect.assertions(3)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 5, parentsId: [1] },
        { id: 1, parentsId: [] },
        { id: 2, parentsId: [1] },
        { id: 8, parentsId: [5] },
        { id: 3, parentsId: [5] },
        { id: 4, parentsId: [2] },
        { id: 6, parentsId: [2] },
        { id: 11, parentsId: [1] },
        { id: 12, parentsId: [11] },
        { id: 13, parentsId: [11] },
      ],
      [8, 3, 4, 6, 12, 13]
    )
    let actives = tree.getActiveIds()
    expect(actives.length).toBe(_.values(tree.byId).length)

    tree.byId[2].toggleActive()

    actives = tree.getActiveIds()
    expect(actives.length).toBe(4)
    expect(actives).toEqual(expect.arrayContaining([1, 2, 4, 6]))
  })

  it('computes correctly the depths', () => {
    expect.assertions(28)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 1, parentsId: [] },
        { id: 111, parentsId: [1] },
        { id: 112, parentsId: [111] },
        { id: 121, parentsId: [1] },
        { id: 122, parentsId: [121] },
        { id: 123, parentsId: [122] },
        { id: 2, parentsId: [112, 123] },
      ],
      []
    )
    expect(tree.byId[1].depthMin).toBe(0)
    expect(tree.byId[1].depthMax).toBe(0)
    expect(tree.byId[111].depthMin).toBe(1)
    expect(tree.byId[111].depthMax).toBe(2)
    expect(tree.byId[112].depthMin).toBe(2)
    expect(tree.byId[112].depthMax).toBe(3)
    expect(tree.byId[121].depthMin).toBe(1)
    expect(tree.byId[121].depthMax).toBe(1)
    expect(tree.byId[122].depthMin).toBe(2)
    expect(tree.byId[122].depthMax).toBe(2)
    expect(tree.byId[123].depthMin).toBe(3)
    expect(tree.byId[123].depthMax).toBe(3)
    expect(tree.byId[2].depthMin).toBe(4)
    expect(tree.byId[2].depthMax).toBe(4)
    tree.adjustDepth()
    expect(tree.byId[1].depthMin).toBe(0)
    expect(tree.byId[1].depthMax).toBe(0)
    expect(tree.byId[111].depthMin).toBe(1)
    expect(tree.byId[111].depthMax).toBe(1)
    expect(tree.byId[112].depthMin).toBe(2)
    expect(tree.byId[112].depthMax).toBe(3)
    expect(tree.byId[121].depthMin).toBe(1)
    expect(tree.byId[121].depthMax).toBe(1)
    expect(tree.byId[122].depthMin).toBe(2)
    expect(tree.byId[122].depthMax).toBe(2)
    expect(tree.byId[123].depthMin).toBe(3)
    expect(tree.byId[123].depthMax).toBe(3)
    expect(tree.byId[2].depthMin).toBe(4)
    expect(tree.byId[2].depthMax).toBe(4)
  })

  it('computes correctly the weights (easy)', () => {
    expect.assertions(7)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 1, parentsId: [] },
        { id: 111, parentsId: [1] },
        { id: 112, parentsId: [111] },
        { id: 121, parentsId: [1] },
        { id: 122, parentsId: [121] },
        { id: 123, parentsId: [122] },
        { id: 2, parentsId: [112, 123] },
      ],
      []
    )
    tree.adjustDepth()
    tree.distributeWeight()
    expect(tree.byId[1].weight).toBe(2)
    expect(tree.byId[111].weight).toBe(1)
    expect(tree.byId[112].weight).toBe(1)
    expect(tree.byId[121].weight).toBe(1)
    expect(tree.byId[122].weight).toBe(1)
    expect(tree.byId[123].weight).toBe(1)
    expect(tree.byId[2].weight).toBe(2)
  })

  it('computes correctly the weights (indivisible)', () => {
    expect.assertions(7)
    const tree = new Tree()
    tree.addNodes(
      [
        { id: 1, parentsId: [] },
        { id: 11, parentsId: [1] },
        { id: 12, parentsId: [1] },
        { id: 13, parentsId: [1] },
        { id: 112, parentsId: [11, 12] },
        { id: 123, parentsId: [12, 13] },
        { id: 2, parentsId: [112, 123] },
      ],
      []
    )
    tree.adjustDepth()
    tree.distributeWeight()
    expect(tree.byId[1].weight).toBe(6)
    expect(tree.byId[11].weight).toBe(2)
    expect(tree.byId[12].weight).toBe(2)
    expect(tree.byId[13].weight).toBe(2)
    expect(tree.byId[112].weight).toBe(3)
    expect(tree.byId[123].weight).toBe(3)
    expect(tree.byId[2].weight).toBe(6)
  })

  it.todo('throws an error when cycle')

  it.todo('activates all ndoes if all deactivated')

  it('throws an error when unknown node as a parentId', () => {
    expect.assertions(1)
    const tree = new Tree()
    expect(() =>
      tree.addNodes(
        [
          { id: 1, parentsId: [] },
          { id: 2, parentsId: [3] },
        ],
        []
      )
    ).toThrowError('unknown')
  })

  // multi-roots are allowed now
  it.skip('throws an error when multi-root', () => {
    expect.assertions(1)
    const tree = new Tree()
    expect(() =>
      tree.addNodes(
        [
          { id: 1, parentsId: [] },
          { id: 2, parentsId: [1] },
          { id: 5, parentsId: [] },
        ],
        []
      )
    ).toThrowError('multi')
  })
})
