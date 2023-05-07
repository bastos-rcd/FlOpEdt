// Could not find any interesting library

import {forEach, forOwn, maxBy, minBy, sortBy, values} from 'lodash'

interface Ided {
    id: number
}
interface ParIded extends Ided {
    parent?: number | null
}

export interface ITreeNode<D extends Ided> {
    parent: ITreeNode<D> | null
    children: ITreeNode<D>[]
    // from the root to the node
    ancestors: ITreeNode<D>[]
    descendants: ITreeNode<D>[]
    nLeaves: number
    depthMin: number
    depthMax: number
    data: D

    addChild(child: ITreeNode<Ided>) : void
    sortChildrenBy(property: string) : void
    countLeaves() : void
    computeDepthMin(yours: number) : void
    computeDepthMax() : void
}

export class TreeNode<D extends Ided> implements ITreeNode<D> {
    parent: TreeNode<D> | null
    children: TreeNode<D>[]
    // from the root to the node
    ancestors: TreeNode<D>[]
    descendants: TreeNode<D>[]
    nLeaves : number
    depthMin: number
    depthMax: number
    data: D

    constructor(parent: TreeNode<D> | null, data: D) {
        this.parent = null
        this.children = []
        this.ancestors = []
        this.descendants = []
        this.nLeaves = -1
        this.depthMin = -1
        this.depthMax = -1
        this.data = data
        parent?.addChild(this)
    }

    addChild(child: TreeNode<D>) : void {
        if (child.ancestors.length > 0 || child.parent !== null) {
            throw new Error("Tree: Multi-rooted tree")
        }
        child.parent = this
        this.children.push(child)

        child.ancestors = this.ancestors.slice(0)
        child.ancestors.push(this)
        child.propageDownAncestors(child.ancestors)

        this.propagateUpDescendants([child].concat(child.descendants))
    }

    propageDownAncestors(ancestors: TreeNode<D>[]) {
        forEach(this.children, child => {
            child.ancestors = ancestors.concat(child.ancestors)
            child.propageDownAncestors(ancestors)
        })
    }

    propagateUpDescendants(descendants: TreeNode<D>[]) {
        this.descendants = this.descendants.concat(descendants)
        if (this.parent !== null) {
            this.parent.propagateUpDescendants(descendants)
        }
    }

    sortChildrenBy(property: string) : void {
        this.children = sortBy(this.children,
            child => (child.data as any)[property])
        forEach(this.children, child => child.sortChildrenBy(property))
    }

    computeDepthMin(yours: number) : void {
        this.depthMin = yours
        forEach(this.children, child => {
            child.computeDepthMin(yours + 1)
        })
    }

    computeDepthMax(): void {
        const newLevel = minBy(
            this.children,
            child => child.depthMax)?.depthMax - 1
        if (newLevel != this.depthMax) {
            this.depthMax = newLevel
            this.parent?.computeDepthMax()
        }
    }

    countLeaves(): void {
        if (this.children.length == 0) {
            this.nLeaves = 1
        } else {
            this.nLeaves = 0
        }
        forEach(this.children, child => {
            child.countLeaves()
            this.nLeaves += child.nLeaves
        })
    }
}


export interface ITree<D extends ParIded> {
    root: ITreeNode<Ided> | null
    byId: Record<number, ITreeNode<Ided>>
    addNodes(data : Array<D>) : void
    sortChildrenBy(property: string) : void
    countLeaves() : void
    computeDepthMin() : void
    computeDepthMax() : void
}

export class Tree<D extends ParIded> implements ITree<D> {
    root: TreeNode<Ided> | null
    byId: Record<number, TreeNode<Ided>>

    constructor() {
        this.root = null
        this.byId = {}
    }

    addNodes(data : Array<D>) : void {
        forEach(data, d => {
            if (this.byId[d.id] !== undefined) {
                throw new Error("Tree: non-unique id in the nodes")
            }
            if (d.parent === undefined) {
                throw new Error("Tree: parent undefined")
            }
            this.byId[d.id] = new TreeNode(null, d) as TreeNode<Ided>
        })
        forOwn(this.byId as Record<number, TreeNode<ParIded>>, (val, key) => {
            if (val.data.parent === null) {
                if (this.root !== null) {
                    throw new Error("Tree: multiple roots")
                }
                this.root = this.byId[val.data.id]
            } else {
                if (val.data.parent === undefined || 
                    this.byId[val.data.parent] === undefined) {
                    throw new Error("Tree: unknown parent")
                }
                this.byId[val.data.parent].addChild(val as TreeNode<Ided>)
            }
            delete val.data.parent
        })
        if (this.root === null) {
            throw new Error("Tree: no root?!")
        }
        this.computeDepthMin()
        this.computeDepthMax()
        this.countLeaves()
    }

    sortChildrenBy(property: string) : void {
        this.root?.sortChildrenBy(property)
    }

    computeDepthMin(): void {
        if(this.root !== null) {
            this.root.computeDepthMin(0)
        }
    }

    computeDepthMax(): void {
        const maxLevel = maxBy(
            values(this.byId),
            child => child.depthMin)?.depthMin
        forEach(values(this.byId), node => {
            if(node.children.length == 0) {
                node.depthMax = maxLevel
                node.parent?.computeDepthMax()
            }
        })
    }

    countLeaves(): void {
        this.root?.countLeaves()
    }   
}