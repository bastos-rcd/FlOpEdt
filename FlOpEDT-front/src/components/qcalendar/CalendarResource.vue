<template>
    <div class="subcontent">
        <!-- <navigation-bar @today="onToday" @prev="onPrev" @next="onNext" /> -->

        <div class="row justify-center">
            <div style="display: flex; max-width: 800px; width: 100%; height: 400px;">
                <q-calendar-resource ref="calendar" v-model="selectedDate" v-model:model-resources="resources"
                    resource-key="id" resource-label="name" resource-height=20 resource-min-height=10 bordered
                    @change="onChange" @moved="onMoved" @resource-expanded="onResourceExpanded" @click-date="onClickDate"
                    @click-time="onClickTime" @click-resource="onClickResource" @click-head-resources="onClickHeadResources"
                    @click-interval="onClickInterval">

                    <template #resource-intervals="{ scope }">
                        <template v-for="(event, index) in getEvents(scope)" :key="index">
                            <div color="primary" :style="getStyle(event)" >
                                <span span style="display: table;margin: 0 auto;">{{ event.title }}</span>
                            </div> 
                        </template>
                    </template>
                </q-calendar-resource>
            </div>
        </div>
    </div>
</template>
  
<script setup lang="ts">
import { QCalendarResource, today } from '@quasar/quasar-ui-qcalendar/src/index.js' //'@quasar/quasar-ui-qcalendar/src/QCalendarResource.js'
import '@quasar/quasar-ui-qcalendar/src/QCalendarVariables.sass'
import '@quasar/quasar-ui-qcalendar/src/QCalendarTransitions.sass'
import '@quasar/quasar-ui-qcalendar/src/QCalendarResource.sass'
import { onBeforeMount, ref } from 'vue'

const calendar = ref(null)
const selectedDate = ref(today())
const props = defineProps<{
  events: any
  resources: any
  }>()

const resources = ref([] )

onBeforeMount(() => {
    resources.value = JSON.parse(JSON.stringify(props.resources))
}

)


function getEvents(scope) {
    const scopedEvents = []
    if (props.events[scope.resource.id]) {
        // get events for the specified resource
        const resourceEvents = props.events[scope.resource.id]
        // make sure we have events
        if (resourceEvents && resourceEvents.length > 0) {
            // for each events figure out start position and width
            for (let x = 0; x < resourceEvents.length; ++x) {
                scopedEvents.push({
                    left: scope.timeStartPosX(resourceEvents[x].start),
                    width: scope.timeDurationWidth(resourceEvents[x].duration),
                    title: resourceEvents[x].title
                })
            }
        }
    }
    return scopedEvents
}
function getStyle(event) {
    return {
        position: 'absolute',
        background: 'grey',
        color: 'white',
        left: event.left + 'px',
        width: event.width + 'px'
    }
}


function onMoved(data: any) {
    console.log('onMoved', data)
}
function onChange(data: any) {
    console.log('onChange', data)
}
function onResourceExpanded(data: any) {
    console.log('onResourceExpanded', data)
}
function onClickDate(data: any) {
    console.log('onClickDate', data)
}
function onClickTime(data: any) {
    console.log('onClickTime', data)
}
function onClickResource(data: any) {
    console.log('onClickResource', data)
}
function onClickHeadResources(data: any) {
    console.log('onClickHeadResources', data)
}
function onClickInterval(data: any) {
    console.log('onClickInterval', data)
}
</script>