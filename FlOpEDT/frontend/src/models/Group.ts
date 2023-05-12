/**
 * @class
 */
export class Group {
    private _id!: number
    private _name!: string
    private _train_prog!: string

    constructor(id: number, name: string, train_prog:string) {
        this.id = id
        this.name = name
        this.train_prog = train_prog
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

    get train_prog() {
        return this._train_prog
    }
    set train_prog(train_prog) {
        this._train_prog = train_prog
    }

    toString(){
        return this.train_prog + "-" + this.name
    }

    static serialize(group: Group) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new Group(obj.id, obj.name, obj.train_prog)
    }
}
