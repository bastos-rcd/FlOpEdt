// Could not find any interesting library

import {forEach, forOwn, maxBy, minBy, sortBy, values, map} from 'lodash'


export interface LinkIdUp {
    id: number
    parentId: number | null
    active?: number
}

export interface LinkUp extends LinkIdUp {
    rank: number
}


export interface ITreeNode extends LinkUp {
    parent: ITreeNode | null
    children: ITreeNode[]
    // from the root to the node
    ancestors: ITreeNode[]
    descendants: ITreeNode[]
    nLeaves: number
    depthMin: number
    depthMax: number

    addChild(child: ITreeNode) : void
    countLeaves() : void
    computeDepthMin(yours: number) : void
    computeDepthMax() : void
    propageDownAncestors(ancestors: ITreeNode[]) : void
    propagateUpDescendants(descendants: ITreeNode[]) : void
    sortChildren() : void 
}

export class TreeNode implements ITreeNode {
    id: number
    rank: number
    parentId: number | null
    parent: ITreeNode | null
    children: ITreeNode[]
    // from the root to the node
    ancestors: ITreeNode[]
    descendants: ITreeNode[]
    nLeaves: number
    depthMin: number
    depthMax: number


    constructor(parent: TreeNode | null, linkUp : LinkUp) {
        this.id = linkUp.id
        this.rank = linkUp.rank
        this.parentId = linkUp.parentId
        this.parent = null
        this.children = []
        this.ancestors = []
        this.descendants = []
        // TODO: mieux gérer les valeurs par défaut
        this.nLeaves = -1
        this.depthMin = -1
        this.depthMax = -1
        parent?.addChild(this)
    }

    addChild(child: ITreeNode) : void {
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

    propageDownAncestors(ancestors: ITreeNode[]) {
        forEach(this.children, child => {
            child.ancestors = ancestors.concat(child.ancestors)
            child.propageDownAncestors(ancestors)
        })
    }

    propagateUpDescendants(descendants: ITreeNode[]) {
        this.descendants = this.descendants.concat(descendants)
        if (this.parent !== null) {
            this.parent.propagateUpDescendants(descendants)
        }
    }

    sortChildren() : void {
        console.log(map(this.children, c => c.id))
        this.children = sortBy(this.children,
            child => child.rank)
        console.log(map(this.children, c => c.id))
        forEach(this.children, child => child.sortChildren())
    }

    computeDepthMin(yours: number) : void {
        this.depthMin = yours
        forEach(this.children, child => {
            child.computeDepthMin(yours + 1)
        })
    }

    computeDepthMax(): void {
        if (this.children.length == 0) {
            return
        }
        const newLevel = (minBy(
            this.children,
            child => child.depthMax)?.depthMax as number) - 1
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

    
export interface ITree {
    root: ITreeNode | null
    byId: Record<number, ITreeNode>
    addNodes(data : Array<LinkIdUp>) : void
    countLeaves() : void
    computeDepthMin() : void
    computeDepthMax() : void
    sortChildren(property: string) : void
}



export class Tree implements ITree {
    root: ITreeNode | null
    byId: Record<number, TreeNode>

    constructor() {
        this.root = null
        this.byId = {}
    }

    addNodes(data : Array<LinkIdUp>) : void {
        forEach(data, (linkIdUp, rank) => {
            if (this.byId[linkIdUp.id] !== undefined) {
                throw new Error("Tree: non-unique id in the nodes")
            }
            (linkIdUp as LinkUp).rank = rank
            this.byId[linkIdUp.id] = new TreeNode(null, (linkIdUp as LinkUp))
        })
        forOwn(this.byId as Record<number, TreeNode>, (val, key) => {
            if (val.parentId === null) {
                if (this.root !== null) {
                    throw new Error("Tree: multiple roots")
                }
                this.root = this.byId[val.id]
            } else {
                if (this.byId[val.parentId] === undefined) {
                    throw new Error("Tree: unknown parent")
                }
                this.byId[val.parentId].addChild(val)
            }
        })
        if (this.root === null) {
            throw new Error("Tree: no root?!")
        }
        this.computeDepthMin()
        this.computeDepthMax()
        this.countLeaves()
    }

    sortChildren() : void {
        this.root?.sortChildren()
    }

    computeDepthMin(): void {
        if(this.root !== null) {
            this.root.computeDepthMin(0)
        }
    }

    computeDepthMax(): void {
        if (values(this.byId).length == 0) {
            return
        }
        const maxLevel = (maxBy(
            values(this.byId),
            child => child.depthMin)?.depthMin as number)
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