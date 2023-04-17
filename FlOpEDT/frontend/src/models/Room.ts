/**
 * @class
 */
export class Room {
    private _id!: number
    private _is_basic!: boolean
    private _name!: string
    private _departments!: Array<number>
    private _subroom_of!:Array<number>
    private _basic_rooms!:Array<{ id: number; name: string }>

    constructor(id: number, is_basic: boolean, name:string, departments:Array<number>, subroom_of:Array<number>, basic_rooms:Array<{ id: number; name: string }>) {
        this.id = id
        this.is_basic = is_basic
        this.name = name
        this.departments = departments
        this.subroom_of = subroom_of
        this.basic_rooms = basic_rooms
    }

    get id() {
        return this._id
    }
    set id(id) {
        this._id = id
    }

    get basic_rooms() {
        return this._basic_rooms
    }
    set basic_rooms(basic_rooms) {
        this._basic_rooms = basic_rooms
    }

    get subroom_of() {
        return this._subroom_of
    }
    set subroom_of(subroom_of) {
        this._subroom_of = subroom_of
    }

    get departments() {
        return this._departments
    }
    set departments(departments) {
        this._departments = departments
    }

    get is_basic() {
        return this._is_basic
    }
    set is_basic(is_basic) {
        this._is_basic = is_basic
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

    static serialize(room: Room) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new Room(obj.id,obj.is_basic, obj.name, obj.departments, obj.subroom_of, obj.basic_rooms)
    }
}
