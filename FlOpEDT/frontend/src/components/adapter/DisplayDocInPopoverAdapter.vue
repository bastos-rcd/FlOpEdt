<template>
    <template v-if="currentPopoverFound">
        <template v-if="selectedConstraint">
            <Teleport to=".popover-body" :key="key">
                <hr />
                <DocDisplayerControler :constraint="selectedConstraint" :showDoc="showDoc" @updateShowDoc="swap"
                    hideLabel="⬆" showLabel="⬇" />
            </Teleport>
        </template>
    </template>
</template>
 

<script setup lang="ts">
import DocDisplayerControler from '@/components/controler/DocDisplayerControler.vue';
import type { Constraint } from "@/models/Constraint";
import { useConstraintStore } from '@/stores/constraint';
import { ref, type Ref } from "vue";

/** =========================================================================================
 *  In charge to : 
 *      - Alter the existing page by redifining CSS 
 *      - Adding new content by teleporting it to the right place
 *      - Infers the right constraint from the existing page
 */

/**
 * Properties declaration interface of the component
 */
interface Props {
    /**
     * Reference to know if the documentation is shown
     */
    showDoc: boolean
}
const props = withDefaults(defineProps<Props>(), {})

/**
 * Events emits by the component
 */
const emit = defineEmits<{
    (e: 'updateShowDoc', value: boolean): void
}>()

const POPOVER_MAX_WIDTH = `80vw`
const EVT_POPOVER_OPENED = 'contextmenu'
const CONSTRAINT_BODY = document.getElementById('constraints-body') as HTMLElement
const EVT_TARGET_CONSTRAINT_BODY = CONSTRAINT_BODY as EventTarget
const CST_ID_REGEX = new RegExp('^\\D+\\d+$')
const G_CURRENT_POPOVER_NAME = "currentPopover"
const CLASS_POPOVER = `popover`
const CLASS_BTN_GROUP = `btn-group`

const constraintStore = useConstraintStore()

/**
 * Is the selected popover found 
 */
const currentPopoverFound = ref(false)

/**
 * Currently selected constraint
 */
const selectedConstraint: Ref<Constraint | null> = ref(null)

/**
 * Key to force teleportation
 */
const key = ref(0)

/**
 * Enlarge the width of the parent popover & center the bottons Duplicate/Modify/Delete
 */
function enlargePopover() {
    const popover = document.getElementsByClassName(CLASS_POPOVER).item(0) as HTMLElement
    if (popover !== null) {
        popover.style.maxWidth = POPOVER_MAX_WIDTH
        //Focus the screen on the popover
        window.scroll(popover.getBoundingClientRect().right, 0)
    }
    //Center the buttons
    const groupesOfButton = document.getElementsByClassName(CLASS_BTN_GROUP)
    for (let i = 0; i < groupesOfButton.length; i++) {
        const group = groupesOfButton.item(i) as HTMLElement
        if (group != null) {
            group.style.alignItems = 'center';
            group.style.justifyContent = 'center';
            group.style.display = 'flex'
        }
    }
}

function forceTeleport() {
    if (key.value < 2) // To avoid integer overflow
        key.value++;
    else
        key.value = 0
    enlargePopover()
}

/**
 * Swap showDoc value
 */
function swap() {
    emit('updateShowDoc', props.showDoc)
}



/**
 * Return the currently selected constraint 
 * 
 * @returns name of the currently selected constraint
 */
function getCurrentConstraint() {
    //Gather the current popover global var element
    const currentPopover = window.eval(G_CURRENT_POPOVER_NAME)
    if (currentPopover) {
        currentPopoverFound.value = true
        //Look up in his attributes for the constraint id
        const cstId = currentPopover._element.getAttribute('data-cst-id') as string

        //Parse the id to get the class name
        const match = cstId.match(CST_ID_REGEX)
        //Return the associated constraint from the store if there is a match
        if (match && constraintStore.items.has(match[0])) {
            return constraintStore.items.get(match[0])
        } else
            console.warn(`constraint ${match} not found in the store`)
    } else
        console.warn(`${G_CURRENT_POPOVER_NAME} element not found`)
}

function setCurrentConstraint() {
    const cst = getCurrentConstraint()
    selectedConstraint.value = cst ? cst : null
}

/**
 * Initialize the constraint store then set the current constraint.
 * 
 * Ensure that if user click on a constraint before the store is initialized then 
 * the current constraint is registered.
 */
constraintStore.initialize().then(() => {
    setCurrentConstraint()
})

/**
 * Add an event listener that changes the current constraint when the user
 * click on a constraint card
 */
EVT_TARGET_CONSTRAINT_BODY.addEventListener(
    EVT_POPOVER_OPENED,
    (e) => {
        setCurrentConstraint()
        if (selectedConstraint.value)
            forceTeleport()
    },
    false
)

/**
 * Observer on the constraint body that reset the constraint when 
 * the popover is removed from the constraint body
 */
new MutationObserver((mutationList: any[]) =>
    mutationList.forEach(() => {
        if (CONSTRAINT_BODY.getElementsByClassName("popover").length == 0)
            selectedConstraint.value = null
    })).observe(CONSTRAINT_BODY, {
        childList: true
    })

enlargePopover()
</script>


<style scoped>
* :deep() .buttonContainer {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: larger;
}

* :deep() .plusButton {
    width: 100%;
    height: 30px;
    border-radius: 20px;
    border: none;
    background-color: green;
}

* :deep() .plusButton:hover {
    background-color: darkgreen;
}

* :deep() .minusButton {
    width: 100%;
    height: 30px;
    border-radius: 20px;
    border: none;
    background-color: firebrick;
}

* :deep() .minusButton:hover {
    background-color: darkred;
}

* :deep() .scrollbar {
    max-height: 70vh;
    overflow-y: scroll;
}

* :deep() .scrollbar-primary::-webkit-scrollbar {
    width: 12px;
}

* :deep() .scrollbar-primary::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: dodgerblue;
}

* :deep() .scrollbar-primary::-webkit-scrollbar-thumb:hover {
    border-radius: 4px;
    background-color: royalblue;
}

* :deep() .scrollbar-primary {
    scrollbar-color: #aaaaaa #f5f5f5;
}
</style>
