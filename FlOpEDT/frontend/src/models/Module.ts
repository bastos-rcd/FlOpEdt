/**
 * @class
 */
export class Module {
    private _id!: number
    private _abbrev!: string
    private _name!: string

    constructor(id: number, abbrev: string, name:string) {
        this.id = id
        this.abbrev = abbrev
        this.name = name
    }

    get id() {
        return this._id
    }
    set id(id) {
        this._id = id
    }

    get abbrev() {
        return this._abbrev
    }
    set abbrev(abbrev) {
        this._abbrev = abbrev
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

    static serialize(module: Module) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new Module(obj.id, obj.abbrev, obj.name)
    }
}
