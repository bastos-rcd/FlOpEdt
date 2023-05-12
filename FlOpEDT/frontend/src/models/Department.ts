/**
 * @classDepartement
 */
export class Department {
    private _id!: number
    private _abbrev!: string

    constructor(id: number, abbrev: string) {
        this.id = id
        this.abbrev = abbrev
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

    toString(){
        return this.abbrev
    }

    static serialize(dept: Department) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new Department(obj.id, obj.abbrev)
    }
}
