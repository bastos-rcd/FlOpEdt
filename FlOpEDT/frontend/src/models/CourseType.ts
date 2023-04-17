/**
 * @class
 */
export class CourseType {
    private _id!: number
    private _name!: string

    constructor(id: number, name: string) {
        this.id = id
        this.name = name
    }

    get id() {
        return this._id
    }
    set id(id) {
        this._id = id
    }

    get name() {
        return this._name
    }
    set name(name) {
        this._name = name
    }

    toString(){
        return this.name
    }

    static serialize(dept: CourseType) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new CourseType(obj.id, obj.name)
    }
}
