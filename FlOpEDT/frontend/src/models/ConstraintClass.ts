import { ConstrParameterClass } from '@/models/ConstrParameterClass'

/**
 * @class
 */
export class ConstraintClass {
    private _className!: string
    private _local_name!: string
    private _parameters!: Map<string, ConstrParameterClass>

    constructor(
        className: string,
        local_name: string,
        parameters: Map<string, ConstrParameterClass>
    ) {
        this.className = className
        this.local_name = local_name
        this.parameters = parameters
    }

    get className() {
        return this._className
    }
    set className(className) {
        this._className = className
    }

    get local_name() {
        return this._local_name
    }
    set local_name(local_name) {
        this._local_name = local_name
    }

    get parameters() {
        return this._parameters
    }
    set parameters(parameters) {
        this._parameters = parameters
    }

    toString(){
        return "[" + this.className + "; " + this.local_name + "; " + this.parameters + "]"
    }

    static serialize(param: ConstrParameterClass) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        const listParam = new Map<string, ConstrParameterClass>()
        obj.parameters.forEach((param: any) => {
            const p = ConstrParameterClass.unserialize(param)
            listParam.set(p.name, p)
        })
        return new ConstraintClass(
            obj.name,
            obj.local_name,
            listParam
        )
    }
}
