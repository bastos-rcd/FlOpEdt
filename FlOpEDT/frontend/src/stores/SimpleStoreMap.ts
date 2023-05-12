import { computed, ref, type Ref } from 'vue'

interface I_Identifiable<ID_TYPE> {
    id: ID_TYPE
}

/**
 * A store object consisting in a map where items are sorted by id
 * @class
 */
export abstract class SimpleStoreMap<ID_TYPE, ITEM_TYPE extends I_Identifiable<ID_TYPE>> {
    /**
     * Items sorted by id
     */
    protected map: Ref<Map<ID_TYPE, ITEM_TYPE>> = ref(new Map<ID_TYPE, ITEM_TYPE>())

    /**
     * To know if the store has already call an initialization
     * {@link initialize}
     */
    protected isInitialized = false

    /**
     * Accessor for
     * {@link map}
     */
    items = computed(() => this.map.value)

    /**
     * Mutator for
     * {@link map}
     *
     * Insert a new entry
     */
    insertNew(item: ITEM_TYPE) {
        if (!this.map.value.has(item.id)) {
            this.map.value.set(item.id, item)
        } else throw Error('ID ' + item.id + ' alredy in the map')
    }

    /**
     * Mutator that initialize the
     * {@link map}
     *
     * Resolves if the map has already been initialized
     * Reject if {@link gatherData} reject
     */
    initialize(): Promise<null> {
        return new Promise((resolve, reject) => {
            if (!this.isInitialized) {
                this.isInitialized = true
                this.gatherData()
                    .then((items) => {
                        items.forEach((item) => {
                            this.insertNew(item)
                        })
                        resolve(null)
                    })
                    .catch((err) => {
                        console.error("Store initialize() failed : " + err)
                        this.isInitialized = false
                        reject(null)
                    })
            } else resolve(null)
        })
    }

    /**
     * template method pattern called in
     * {@link initialize}
     *
     * @returns an array of items to be inserted in the
     * {@link map}
     */
    abstract gatherData(): Promise<Array<ITEM_TYPE>>
}
