import type { Constraint } from '@/models/Constraint'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'
import { getAllConstraint } from '@/composables/API_Constraint';

class ConstraintStore extends SimpleStoreMap<string, Constraint> {
    static G_CURRENT_DEPARTMENT = 'department'
    private dep

    constructor() {
        super()
        //Look for the pre-existing var G_CURRENT_DEPARTMENT to load the current department
        const dep = window.eval(ConstraintStore.G_CURRENT_DEPARTMENT)
        if (!dep)
            console.error("Current department not found")

        this.dep = dep
    }

    gatherData() {
        return getAllConstraint(this.dep);
    }

    replace(item:Constraint){
        if(this.items.value.has(item.id)){
            this.items.value.delete(item.id)
            this.insertNew(item)
        }else
            console.warn(item + "Does not exist in the map")
    }
}

export const useConstraintStore = defineStore('contraint', () => {
    const store = new ConstraintStore()

    const items = store.items

    function insertNew(item: Constraint) {
        store.insertNew(item)
    }

    function replace(item: Constraint){
        store.replace(item)
    }
    function initialize() {
        return store.initialize()
    }

    return { items, insertNew, initialize ,replace}
})
