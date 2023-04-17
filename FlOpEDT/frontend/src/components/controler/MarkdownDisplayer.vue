<template>
    <div>
        <VueShowdown :markdown="doc.textContent" :options="{ tables: true }" :extensions="[POST_PROCESSING_EXTENSION]" />
    </div>
    <template v-if="teleportable">
        <template v-if="constraint">
            <template v-for="paramReqName in paramRequestedName" :key="paramReqName">
                <template v-if="constraintHasParameter(paramReqName)">
                    <template v-for="callCount in getNumberOfCallAsArray(paramReqName)" :key="callCount">
                        <Teleport :to="'#' + paramReqName + 'Displayer' + callCount">
                            <template v-if="isParamInstanciate(paramReqName)">
                                <template
                                    v-if="ConstrParameter.primitiveTypes().includes(constraint.parameters.get(paramReqName)?.type as string)">
                                    <SimpleConstraintParameterDisplayer
                                        :values="(constraint.parameters.get(paramReqName)?.id_list as unknown[])" />
                                </template>
                                <template
                                    v-if="ConstrParameter.objectTypes().includes(constraint.parameters.get(paramReqName)?.type as string)">
                                    <ConstraintParameterDisplayer
                                        :idList="(constraint.parameters.get(paramReqName)?.id_list as unknown[])"
                                        :values="storesItems.get(constraint.parameters.get(paramReqName)?.type as string)" />
                                </template>
                            </template>
                            <template v-else>
                                <i>{{ translate(paramReqName) }} </i> 
                            </template>
                        </Teleport>
                    </template>
                </template>
            </template>
        </template>
    </template>
</template>

<script setup lang="ts">
import type { MarkdownDocumentation } from '@/models/MarkdownDocumentation'
import { VueShowdown } from 'vue-showdown'
import { onMounted, ref } from 'vue'
import { useCourseTypeStore } from '@/stores/courseType'
import { useDepartmentStore } from '@/stores/departmentRework'
import { useGroupStore } from '@/stores/group'
import { useModuleStore } from '@/stores/module'
import { useTrainProgStore } from '@/stores/trainProg'
import { useTutorStore } from '@/stores/tutor'
import { useWeekStore } from '@/stores/week'
import { useRoomStore } from '@/stores/roomRework'
import type { Constraint } from '@/models/Constraint'
import ConstraintParameterDisplayer from '@/components/view/ConstraintParameterDisplayer.vue'
import SimpleConstraintParameterDisplayer from '@/components/view/SimpleConstraintParameterDisplayer.vue'
import { ConstrParameter } from '@/models/ConstrParameter'

/** =========================================================================================
 * Display a contraint documentation and teleport parameters displayer where the documentation
 * ask it
 */

/**
 * Properties declaration interface of the component
 */
interface Props {
    /**
     * Documentation to render
     */
    doc: MarkdownDocumentation
    /**
     * Associated constraint
     * Used to fill call for interpolation in the documentation
     */
    constraint: Constraint
}
const props = withDefaults(defineProps<Props>(), {})

/**
 * Classes to add to the tables processed by vueshowdown
 */
const TABLE_CLASSES = "table table-bordered"

/**
 * Post processing extension for the vueshowdown component
 */
const POST_PROCESSING_EXTENSION = {
    type: 'output', //Specify that it is a post processing(i.e. applied after the markdown is converted to html)
    filter: function (text: string) {
        return text
            //Add the classes to tables
            .replace(/<table>/g, `<table class="${TABLE_CLASSES}">`)
    }
};

const courseTypeStore = useCourseTypeStore()
const departmentStore = useDepartmentStore()
const groupStore = useGroupStore()
const moduleStore = useModuleStore()
const trainProgStore = useTrainProgStore()
const tutorStore = useTutorStore()
const weekStore = useWeekStore()
const roomStore = useRoomStore()

/**
 * Map of the items in the stores, accessible by the parameter name
 */
const storesItems = new Map<string, any>([
    ["base.CourseType", courseTypeStore.items],
    ["base.Department", departmentStore.items],
    ["base.StructuralGroup", groupStore.items],
    ["base.Module", moduleStore.items],
    ["base.TrainingProgramme", trainProgStore.items],
    ["people.Tutor", tutorStore.items],
    ["base.Week", weekStore.items],
    ["base.Room", roomStore.items]
])

/**
 * List of the requested interpolation
 */
const paramRequestedName = Array.from(props.doc.paramCallCount.keys())

/**
 * Does the parameter displayer can be teleported ?
 */
const teleportable = ref(false)

/**
 * initialize all constraint parameters stores with Promises
 */
async function initializeStores() {
    const promises = [
        courseTypeStore.initialize(),
        departmentStore.initialize(),
        groupStore.initialize(),
        moduleStore.initialize(),
        trainProgStore.initialize(),
        tutorStore.initialize(),
        weekStore.initialize(),
        roomStore.initialize()
    ]
    await Promise.all(promises)
}

/**
 * Return an integer array from 1 to the number of call of interpolation in the doc property.
 * If the parameter is not called, returns an empty array and warn in the console.
 *
 * @param paramName The constraint parameter to check
 * @returns an integer array from 1 to the number of call
 */
function getNumberOfCallAsArray(paramName: string) {
    const nbCall = props.doc.paramCallCount.get(paramName) as number
    if (nbCall) return Array.from({ length: nbCall }, (v, k) => k + 1) //Create the array from 1 to nbCall
    else {
        console.warn(`${paramName} not found in the documentation map of interporlation`)
        return []
    }
}

/**
 * Check if the constraint has the called parameter.
 * Warn in the console if not.
 * 
 * @param paramName the constraint parameter name
 * @returns true if the constraint has the called parameter, else false
 */
function constraintHasParameter(paramName: string) {
    const res = props.constraint.parameters.has(paramName)
    if (!res)
        console.warn(`${paramName} not found in the constraint's parameters`)

    return res;
}

/**
 * Checks if the parameter is instanciated in the constraint.
 * 
 * @param paramReqName 
 */
function isParamInstanciate(paramReqName:string){
    return props.constraint.parameters.get(paramReqName) != null
}

/**
 * Call for a translation of the label.
 * May not be the final version because it use gettext which depend from pre-included scripts
 * 
 * @param label to translate
 * 
 * @return translated label
 */
function translate(label:string){
    return window.eval(`gettext("${label}")`)
}

await initializeStores()
onMounted(() => {
    teleportable.value = true //Allow the teleportation of parameters displayer
})
</script>

<style scoped></style>
