/**
 * @class
 */
export class ConstrParameter {
    /**
     * Constraint parameter object types
     */
    private static CONSTR_PARAMETER_TYPE = [
        "base.Week",
        "base.TrainingProgramme",
        "base.CourseType",
        "base.Module",
        "people.Tutor",
        "base.StructuralGroup",
        "base.Room",
        "base.Department"
    ]

    /**
     * Constraint parameter primitive types
     */
    private static CONSTR_PARAMETER_PRIMITIVE_TYPE = [
        "PositiveSmallIntegerField",
        "CharField",
        "BooleanField",
    ]

    private _name!: string
    private _type!: string //Should be an enum
    private _required!: boolean
    private _multiple!: boolean
    private _id_list!: Array<number>

    constructor(name: string, type: string, required: boolean, multiple: boolean, id_list: Array<number>) {
        this.name = name
        this.type = type
        this.required = required
        this.multiple = multiple
        this.id_list = id_list
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

    get id_list() {
        return this._id_list
    }
    set id_list(id_list: Array<number>) {
        this._id_list = id_list
    }

    static serialize(param: ConstrParameter) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        const id_list: Array<number> = []
        obj.id_list.forEach((e: string) => {
            id_list.push(+e)
        });
        return new ConstrParameter(obj.name, obj.type, obj.required, obj.multiple, id_list)
    }



    static objectTypes() {
        return ConstrParameter.CONSTR_PARAMETER_TYPE
    }

    static primitiveTypes() {
        return ConstrParameter.CONSTR_PARAMETER_PRIMITIVE_TYPE
    }
}