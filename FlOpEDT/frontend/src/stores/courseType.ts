import { getAllCourseType } from '@/composables/API_CourseType'
import type { CourseType } from '@/models/CourseType'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'


class CourseTypeStore extends SimpleStoreMap<number,CourseType> {
    gatherData() {
        return getAllCourseType()
    }
}

export const useCourseTypeStore = defineStore('courseType', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number,CourseType> = new CourseTypeStore()

    const items = store.items

    function insertNew(item:CourseType){
        store.insertNew(item)
    }
        
    function initialize() {
        return store.initialize()
    }

    return { items , insertNew, initialize }
})
