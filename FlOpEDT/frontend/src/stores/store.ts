import { useFetch, usePatch, usePost, usePut } from '@/composables/api'
import { mapListId } from '@/helpers'

export type MappableToIdArray<T> = Array<{ id: number }>

const mappable: MappableToIdArray<number> = []

export class StoreAction<TApp, TAPI> {
    convertToApp: (apiVal: Partial<TAPI>) => TApp
    convertToAPI: (val: Partial<TApp>) => TAPI
    onFetch: (value: Array<TApp>) => Array<TApp>
    url: string

    constructor(
        url: string,
        convertToApp: (apiVal: Partial<TAPI>) => TApp,
        convertToAPI: (val: Partial<TApp>) => TAPI,
        onFetch: (value: Array<TApp>) => Array<TApp>
    ) {
        this.url = url
        this.convertToApp = convertToApp
        this.convertToAPI = convertToAPI
        this.onFetch = onFetch
    }

    convertToPartialAPI(val: Partial<TApp>): Partial<TAPI> {
        return Object.fromEntries(
            Object.entries(val).map((entry) => {
                const param = entry[0]
                const value = entry[1]
                if (value) {
                    if (typeof value === typeof mappable) {
                        return [param, mapListId(value as MappableToIdArray<any>)]
                    }
                    return [param, value]
                }
                return []
            })
        )
    }

    async retrieve(id: number) {
        return useFetch(this.url, { id: id }).then(this.convertToApp)
    }

    async fetch() {
        return useFetch(this.url, {})
            .then((value: Array<TAPI>) => value.map(this.convertToApp))
            .then(this.onFetch) // Allows to update the store's value
    }

    async update(id: number, value: TApp) {
        return usePut(this.url, id, this.convertToAPI(value)).then(this.convertToApp)
    }

    async create(value: TApp) {
        return usePost(this.url, this.convertToAPI(value)).then(this.convertToApp)
    }

    async partialUpdate(id: number, value: Partial<TApp>) {
        return usePatch(this.url, id, this.convertToPartialAPI(value)).then(this.convertToApp)
    }
}
