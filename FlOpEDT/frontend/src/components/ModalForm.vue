<template>
    <div
        ref="modalRef"
        class="modal fade"
        data-bs-backdrop="static"
        data-bs-keyboard="false"
        tabindex="-1"
        aria-labelledby="modalTitleLabel"
        aria-hidden="true"
    >
        <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 id="modalTitleLabel" class="modal-title">
                        <slot name="title"></slot>
                    </h5>
                    <button
                        v-if="!props.isLocked"
                        type="button"
                        class="btn-close"
                        aria-label="Close"
                        @click.stop="onCancel"
                    ></button>
                </div>
                <div class="modal-body">
                    <!-- Alerts -->
                    <div class="sticky-top">
                        <div
                            v-for="alert in alerts"
                            :key="alert.message"
                            :class="`alert-${alert.level}`"
                            class="alert alert-dismissible fade show"
                            role="alert"
                        >
                            {{ alert.message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    </div>
                    <slot name="body"></slot>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click.stop="cancel" :disabled="props.isLocked">
                        Cancel
                    </button>
                    <button type="button" class="btn btn-primary" @click.stop="save" :disabled="props.isLocked">
                        Save
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { FormAlert, FormInterface } from '@/assets/js/types'
import { Modal } from 'bootstrap'
import { defineProps, onMounted, ref, watch } from 'vue'

interface Emits {
    (e: 'interface', formInterface: FormInterface): void
}

const emit = defineEmits<Emits>()

interface Props {
    isOpen: boolean
    isLocked: boolean
    onCancel: () => void
    onSave: () => void
}

const props = defineProps<Props>()

const modalRef = ref()
const isMounted = ref(false)

const alerts = ref<Array<FormAlert>>([])

watch(
    () => props.isOpen,
    (newValue) => {
        if (newValue) {
            open()
        } else {
            close()
        }
    }
)

function open() {
    if (!isMounted.value) {
        return
    }
    const modal = Modal.getOrCreateInstance(modalRef.value)
    if (!modal) {
        return
    }
    modal.show()
}

function cancel() {
    props.onCancel()
}

function save() {
    addAlert('info', 'Sending data, please wait...')
    props.onSave()
}

function close() {
    if (!isMounted.value) {
        return
    }
    const modal = Modal.getOrCreateInstance(modalRef.value)
    if (!modal) {
        return
    }
    dismissAlerts()
    modal.hide()
}

function addAlert(level: string, message: string) {
    alerts.value.push({ level: level, message: message })
}

function dismissAlerts() {
    alerts.value = []
}

onMounted(() => {
    isMounted.value = true
    emit('interface', {
        close: close,
        addAlert: addAlert,
        dismissAlerts: dismissAlerts,
    })
})
</script>

<script lang="ts">
export default {
    name: 'ModalForm',
    components: {},
}
</script>

<style scoped></style>
