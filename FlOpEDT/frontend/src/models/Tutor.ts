

/**
 * @class
 */
export class Tutor {
    private _id!: number
    private _username!: string
    private _first_name!: string
    private _last_name!:string
    private _email!: string
    private _departments!: Array<any>

    constructor(id: number, username: string, first_name:string, last_name:string, email:string,departements:Array<any>) {
        this.id = id
        this.username = username
    }

    get id() {
        return this._id
    }
    set id(id) {
        this._id = id
    }

    get username() {
        return this._username
    }
    set username(username) {
        this._username = username
    }

    get first_name() {
        return this._first_name
    }
    set first_name(first_name) {
        this._first_name = first_name
    }

    get last_name() {
        return this._last_name
    }
    set last_name(last_name) {
        this._last_name = last_name
    }

    get email() {
        return this._email
    }
    set email(email) {
        this._email = email
    }

    get departments() {
        return this._departments
    }
    set departments(departments) {
        this._departments = departments
    }

    toString(){
        return this.username
    }

    static serialize(tutor: Tutor) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new Tutor(obj.id, obj.name,obj.first_name, obj.last_name, obj.email,obj.departements)
    }
}
