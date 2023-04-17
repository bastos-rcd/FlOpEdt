import { ConstrParameter } from '@/models/ConstrParameter'

/**
 * Regular expression catching the class name and the id in the class
 * of a constraint
 */
const ID_REGEX = new RegExp('^(?<className>.+)(?<inClassId>\\d)+$')

/**
 * @class
 */
export class Constraint {
    

    private _inClassId!: number
    private _title!: string
    private _className!: string
    private _weight!: number
    private _is_active!: boolean
    private _comment!: string
    private _modified_at!: string
    private _parameters!: Map<string, ConstrParameter|null>

    constructor(
        inClassId: number,
        title: string,
        className: string,
        weight: number,
        is_active: boolean,
        comment: string,
        modified_at: string,
        parameters: Map<string, ConstrParameter|null>
    ) {
        this.inClassId = inClassId
        this.title = title
        this.className = className
        this.weight = weight
        this.is_active = is_active
        this.comment = comment
        this.modified_at = modified_at
        this.parameters = parameters
    }

    get id() {
        return this.className + this._inClassId
    }
    set id(id) {
        const match = id.match(ID_REGEX)
        if (match && match.groups?.inClassId && match.groups?.className) {
            this._inClassId = +match.groups.inClassId
            this._className = match.groups.className
        } else throw Error('Invalid argument')
    }

    get inClassId() {
        return this._inClassId
    }
    set inClassId(inClassId) {
        this._inClassId = inClassId
    }

    get title() {
        return this._title
    }
    set title(title) {
        this._title = title
    }

    get className() {
        return this._className
    }
    set className(className) {
        this._className = className
    }

    get weight() {
        return this._weight
    }
    set weight(weight) {
        this._weight = weight
    }

    get is_active() {
        return this._is_active
    }
    set is_active(is_active) {
        this._is_active = is_active
    }

    get comment() {
        return this._comment
    }
    set comment(comment) {
        this._comment = comment
    }

    get modified_at() {
        return this._modified_at
    }
    set modified_at(modified_at) {
        this._modified_at = modified_at
    }

    get parameters() {
        return this._parameters
    }
    set parameters(parameters) {
        this._parameters = parameters
    }

    static serialize(param: ConstrParameter) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        const listParam = new Map<string, ConstrParameter>()
        obj.parameters.forEach((param: any) => {
            const p = ConstrParameter.unserialize(param)
            listParam.set(p.name, p)
        })
        return new Constraint(
            obj.id,
            obj.title,
            obj.name,
            obj.weight,
            obj.is_active,
            obj.comment,
            obj.modified_at,
            listParam
        )
    }
}
