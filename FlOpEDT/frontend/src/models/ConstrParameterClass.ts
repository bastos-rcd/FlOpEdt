/**
 * @class
 */
export class ConstrParameterClass {
    private _name!: string
    private _type!: string
    private _required!: boolean
    private _multiple!: boolean

    constructor(name: string, type: string, required: boolean, multiple: boolean) {
        this.name = name
        this.type = type
        this.required = required
        this.multiple = multiple
    }

    get name() {
        return this._name
    }
    set name(name: string) {
        this._name = name
    }

    get type() {
        return this._type
    }
    set type(type: string) {
        this._type = type
    }

    get required() {
        return this._required
    }
    set required(required: boolean) {
        this._required = required
    }

    get multiple() {
        return this._multiple
    }
    set multiple(multiple: boolean) {
        this._multiple = multiple
    }

    toString(){
        return "[" + this.name + "; " + this.type + "; " + this.required + "; " + this.multiple + "]"
    }

    static serialize(param: ConstrParameterClass) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new ConstrParameterClass(obj.name, obj.type, obj.required, obj.multiple)
    }
}
