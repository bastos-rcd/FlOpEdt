import { useFetch } from "@/composables/api"
import { Constraint } from "@/models/Constraint"
import { ConstraintClass } from "@/models/ConstraintClass"

/**
 * Load the constraint classes
 * 
 * @returns a map of ConstraintClass where key are class name
 */
export async function loadConstraintClass(){
    return await useFetch('/fr/api/ttapp/constraint_types', {}).then(function (response) {
        const res = new Map<string, ConstraintClass>()
        response.forEach((element: any) => {
            const classe = ConstraintClass.unserialize(element)
            res.set(classe.className, classe)
        })
        return res
    })
}

const URL_GET_ALL = "/fr/api/ttapp/constraint"
/**
 * Load the constraints
 * 
 * @returns a map of Constraint where key are constraint id
 */
export async function getAllConstraint(department:string){
    return useFetch(URL_GET_ALL,{dept:department})
    .then(items => {
        const res: Array<Constraint> = []
        items.forEach((i:any) => {
            const curItem = Constraint.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}