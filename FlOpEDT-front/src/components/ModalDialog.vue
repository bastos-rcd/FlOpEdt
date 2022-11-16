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
                </div>
                <div class="modal-body">
                    <slot name="body"></slot>
                </div>
                <div class="modal-footer">
                    <slot name="buttons">
                        <button type="button" class="btn btn-secondary" @click.stop="cancel" :disabled="props.isLocked">
                            Cancel
                        </button>
                        <button type="button" class="btn btn-primary" @click.stop="confirm" :disabled="props.isLocked">
                            <span v-if="props.isLocked">
                                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                <span class="visually-hidden">Loading...</span>
                            </span>
                            <span v-else>Confirm</span>
                        </button>
                    </slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { Modal } from 'bootstrap'
import type { DialogInterface } from '@/assets/js/types'

interface Props {
    isOpen: boolean
    isLocked?: boolean
    onCancel?: () => void
    onConfirm?: () => void
}

const props = defineProps<Props>()

interface Emits {
    (e: 'interface', dialogInterface: DialogInterface): void
}

const emit = defineEmits<Emits>()

const isMounted = ref(false)
const modalRef = ref()

function cancel() {
    props.onCancel?.()
}

function confirm() {
    props.onConfirm?.()
}

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

function close() {
    if (!isMounted.value) {
        return
    }
    const modal = Modal.getOrCreateInstance(modalRef.value)
    if (!modal) {
        return
    }
    modal.hide()
}

onMounted(() => {
    isMounted.value = true
    emit('interface', {
        close: close,
    })
})
</script>

<script lang="ts">
export default {
    name: 'ModalDialog',
    components: {},
}
</script>

<style scoped></style>
