// Could not find any interesting library

import {
  forEach,
  forOwn,
  maxBy,
  minBy,
  sortBy,
  values,
  map,
  max,
  sumBy,
  indexOf,
  find,
  filter,
  keys,
  concat,
  difference,
  union,
  range,
} from 'lodash'

export interface LinkIdUp {
  id: number
  parentsId: number[]
}

export interface LinkUp extends LinkIdUp {
  rank: number
  active: boolean
}

export interface ITreeNode extends LinkUp {
  parents: ITreeNode[]
  children: ITreeNode[]
  // from the root to the node
  ancestors: ITreeNode[]
  descendants: ITreeNode[]
  tree: Tree
  nLeaves: number
  depthMin: number
  depthMax: number
  weight: number

  addChild(child: ITreeNode): void
  computeDepthMin(yours: number): void
  computeDepthMax(): void
  propageDownAncestors(ancestors: ITreeNode[]): void
  propagateUpDescendants(descendants: ITreeNode[]): void
  inferActiveBottomUp(): void
  toggleActive(): void
}

export class TreeNode implements ITreeNode {
  id: number
  rank: number
  active: boolean
  parentsId: number[]
  parents: ITreeNode[]
  children: ITreeNode[]
  // from the root to the node
  ancestors: ITreeNode[]
  descendants: ITreeNode[]
  tree: Tree
  nLeaves: number
  depthMin: number
  depthMax: number
  weight: number

  constructor(tree: Tree, parents: ITreeNode[], linkUp: LinkUp) {
    this.id = linkUp.id
    this.rank = linkUp.rank
    this.active = linkUp.active
    this.parentsId = linkUp.parentsId
    this.parents = []
    this.children = []
    this.ancestors = []
    this.descendants = []
    this.tree = tree
    // TODO: mieux gérer les valeurs par défaut
    this.nLeaves = -1
    this.depthMin = -1
    this.depthMax = -1
    this.weight = 0
    forEach(parents, (parent) => parent.addChild(this))
  }

  toggleActive(): void {
    if (this.active) {
      // if all active
      const allNodeIds = map(keys(this.tree.byId), (nidStr: string) => parseInt(nidStr))
      const activeNodeIds = filter(allNodeIds, (id: number) => this.tree.byId[id].active)
      if (allNodeIds.length == activeNodeIds.length) {
        console.log('all there')

        const activeNodes = concat(this.descendants, this.ancestors, this)
        console.log(
          difference(
            allNodeIds,
            map(activeNodes, (n: TreeNode) => n.id)
          )
        )
        forEach(
          difference(
            allNodeIds,
            map(activeNodes, (n: TreeNode) => n.id)
          ),
          (nid: number) => {
            this.tree.byId[nid].active = false
          }
        )
      } else {
        forEach(
          filter(this.descendants, (node: TreeNode) => node.children.length == 0),
          (node: TreeNode) => {
            node.active = false
          }
        )
        this.active = false
        this.tree.inferActiveBottomUp()
      }
    } else {
      this.active = true
      forEach(this.descendants, (node: TreeNode) => (node.active = true))
      forEach(this.ancestors, (node: TreeNode) => (node.active = true))
    }
  }

  addChild(child: ITreeNode): void {
    // if (child.ancestors.length > 0 || child.parents.length > 0) {
    //   throw new Error('Tree: Multi-rooted tree')
    // }
    child.parents.push(this)
    this.children.push(child)

    child.ancestors = this.ancestors.slice(0)
    child.ancestors.push(this)
    child.propageDownAncestors(child.ancestors)

    this.propagateUpDescendants([child].concat(child.descendants))
  }

  propageDownAncestors(ancestors: ITreeNode[]) {
    forEach(this.children, (child: ITreeNode) => {
      child.ancestors = union(ancestors, child.ancestors)
      child.propageDownAncestors(ancestors)
    })
  }

  propagateUpDescendants(descendants: ITreeNode[]) {
    this.descendants = union(this.descendants, descendants)
    forEach(this.parents, (parent) => parent.propagateUpDescendants(descendants))
  }

  computeDepthMin(yours: number): void {
    this.depthMin = Math.max(yours, this.depthMin)
    forEach(this.children, (child: ITreeNode) => {
      child.computeDepthMin(this.depthMin + 1)
    })
  }

  computeDepthMax(): void {
    if (this.children.length == 0) {
      return
    }
    const newLevel = (minBy(this.children, (child: ITreeNode) => child.depthMax)?.depthMax as number) - 1
    if (newLevel != this.depthMax) {
      this.depthMax = newLevel
      forEach(this.parents, (parent) => parent.computeDepthMax())
    }
  }

  inferActiveBottomUp(): void {
    if (this.children.length == 0) {
      return
    }
    forEach(this.children, (child: ITreeNode) => child.inferActiveBottomUp())
    this.active = find(this.children, (child: ITreeNode) => child.active) ? true : false
  }
}

export interface ITree {
  roots: ITreeNode[]
  byId: Record<number, ITreeNode>
  weight: number
  depth: number
  addNodes(linkIdUps: Array<LinkIdUp>, active: Array<number> | undefined): void
  computeDepthMin(): void
  computeDepthMax(): void
  sortFamily(property: string): void
  inferActiveBottomUp(): void
  getActiveIds(): Array<number>
  adjustDepth(): void
  distributeWeight(): void
}

export class Tree implements ITree {
  roots: ITreeNode[]
  byId: Record<number, TreeNode>
  weight: number
  depth: number

  constructor() {
    this.roots = []
    this.byId = {}
    this.weight = -1
    this.depth = -1
  }
  getActiveIds(): Array<number> {
    return map(
      filter(values(this.byId), (node: TreeNode) => node.active),
      (node: TreeNode) => {
        return node.id
      }
    )
  }

  addNodes(linkIdUps: Array<LinkIdUp>, active: Array<number> | undefined): void {
    if (active === undefined) {
      active = []
    }
    forEach(linkIdUps, (linkIdUp: LinkIdUp, rank: number) => {
      if (this.byId[linkIdUp.id] !== undefined) {
        throw new Error('Tree: non-unique id in the nodes')
      }
      ;(linkIdUp as LinkUp).rank = rank
      ;(linkIdUp as LinkUp).active = indexOf(active, linkIdUp.id) > -1 ? true : false
      this.byId[linkIdUp.id] = new TreeNode(this, [], linkIdUp as LinkUp)
    })
    forEach(values(this.byId), (val) => {
      forEach(val.parentsId, (parentId) => {
        if (this.byId[parentId] === undefined) {
          throw new Error('Tree: unknown parent')
        }
        this.byId[parentId].addChild(val)
      })
      if (val.parentsId.length == 0) {
        this.roots.push(val)
      }
    })
    if (this.roots.length == 0) {
      throw new Error('Tree: no root?!')
    }
    this.computeDepthMin()
    this.computeDepthMax()
    this.inferActiveBottomUp()
  }

  inferActiveBottomUp(): void {
    forEach(this.roots, (root) => root.inferActiveBottomUp())
    const sumActive = sumBy(this.roots, (root) => (root.active ? 1 : 0))

    if (sumActive == 0) {
      forEach(values(this.byId), (n: ITreeNode) => {
        n.active = true
      })
    }
  }

  sortFamily(): void {
    forEach(values(this.byId), (node) => {
      node.parents = sortBy(node.parents, (parent) => parent.rank)
      node.children = sortBy(node.children, (child) => child.rank)
    })
  }

  computeDepthMin(): void {
    forEach(values(this.byId), (node) => {
      node.depthMin = 0
    })
    forEach(this.roots, (root) => root.computeDepthMin(0))
  }

  computeDepthMax(): void {
    if (values(this.byId).length == 0) {
      return
    }
    const maxLevel = maxBy(values(this.byId), (child: ITreeNode) => child.depthMin)?.depthMin as number
    forEach(values(this.byId), (node: ITreeNode) => {
      if (node.children.length == 0) {
        node.depthMax = maxLevel
        forEach(node.parents, (parent) => parent.computeDepthMax())
      }
    })
    this.depth = maxLevel
  }

  adjustDepth(): void {
    const sortedNodes = sortBy(values(this.byId), (node) => {
      return -node.depthMin
    })
    forEach(sortedNodes, (node) => {
      forEach(node.parents, (parent) => {
        parent.depthMax = Math.min(parent.depthMax, node.depthMin - 1)
      })
    })
  }

  distributeWeight(): void {
    const maxMinDepth = maxBy(values(this.byId), (node) => node.depthMin)?.depthMin as number
    let maxWidth = 0
    let depthMaxWidth = 0
    let nodesMaxWidth: ITreeNode[] = []
    forEach(range(maxMinDepth), (d) => {
      const filteredNodes = filter(values(this.byId), (node) => node.depthMin <= d && node.depthMax >= d)
      const currentWidth = filteredNodes.length
      if (currentWidth > maxWidth) {
        maxWidth = currentWidth
        depthMaxWidth = d
        nodesMaxWidth = filteredNodes
      }
    })

    // console.log('maxWidth', maxWidth)
    // console.log('depthMaxWidth', depthMaxWidth)
    // console.log(map(nodesMaxWidth, (node) => node.id))

    let ok = false
    let initWeight = 0
    while (!ok) {
      initWeight += 1
      // console.log('initWeight', initWeight)
      if (initWeight == 10) {
        return
      }

      forEach(values(this.byId), (node) => {
        node.weight = 0
      })
      forEach(nodesMaxWidth, (node) => {
        node.weight = initWeight
      })
      ok = true
      let d = depthMaxWidth
      while (ok && d > 0) {
        const filteredNodes = filter(values(this.byId), (node) => node.depthMin == d)
        const indivisible = find(filteredNodes, (node) => {
          forEach(node.parents, (parent) => {
            // console.log(node.id, '->', parent.id, ' -- ', node.weight / node.parents.length)
            parent.weight += node.weight / node.parents.length
          })
          return node.parents.length != 0 && node.weight % node.parents.length !== 0
        })
        ok = indivisible ? false : true
        // if (!ok) {
        //   console.log(indivisible)
        // }
        d -= 1
      }
      d = depthMaxWidth
      while (ok && d <= maxMinDepth) {
        const filteredNodes = filter(values(this.byId), (node) => node.depthMin == d)
        const indivisible = find(filteredNodes, (node) => {
          forEach(node.children, (child) => {
            // console.log(node.id, '->', child.id, ' -- ', node.weight / node.children.length)
            child.weight += node.weight / node.children.length
          })
          return node.children.length != 0 && node.weight % node.children.length !== 0
        })
        ok = indivisible ? false : true
        // if (!ok) {
        //   console.log(indivisible?.id, indivisible?.weight)
        // }
        d += 1
      }
    }
    this.weight = nodesMaxWidth.length * initWeight
  }
}
