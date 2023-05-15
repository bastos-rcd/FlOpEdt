import { shallowMount, VueWrapper } from '@vue/test-utils'
import Calendar from './Calendar.vue'
import { describe, expect, it } from 'vitest'
import { useCase } from './test.data'

describe('Calendar component', () => {
  it.skip('render correctly', () => {
    expect.assertions(3)
    expect(Calendar).toBeTruthy()
    const wrapper = shallowMount(Calendar as any)

    expect(wrapper).toBeDefined()
    expect(wrapper.html()).toMatchSnapshot()
  })

  it.skip('displays columns', async () => {
    expect.assertions(3)
    expect(Calendar).toBeTruthy()
    const wrapper: VueWrapper = shallowMount(Calendar as any, {
      props: {
        columns: [
          {
            id: 23,
            name: '1A',
            weight: 1,
          },
          {
            id: 24,
            name: '1B',
            weight: 1,
          },
        ],
        events: [],
      },
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(wrapper).toBeDefined()
    expect(wrapper.html()).toMatchSnapshot()

    const event65992 = wrapper.find('')
    event65992.trigger('drag')
  })

  it('renders with formated data', async () => {
    expect.assertions(2)
    expect(Calendar).toBeTruthy()
    const wrapper: VueWrapper = shallowMount(Calendar as any, {
      props: {
        columns: useCase.columns,
        events: useCase.events.value,
        dropzoneEvents: useCase.dropzoneEvents,
      },
    })
    expect(wrapper).toBeDefined()
  })
})
