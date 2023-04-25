import { mount } from '@vue/test-utils'
import Calendar from './Calendar.vue'
import { describe, expect, it } from 'vitest'

describe('Calendar component', () => {
  it('render correctly', () => {
    expect.assertions(2)
    const wrapper = mount(Calendar)

    expect(wrapper).toBeDefined()
    expect(wrapper.html()).toMatchSnapshot()
  })

  it('displays columns', async () => {
    expect.assertions(2)
    const wrapper = mount(Calendar, {
      props: {
        columns: [
          {
            id: 23,
            name: '1A',
            weight: 1,
            x: 0,
          },
          {
            id: 24,
            name: '1B',
            weight: 1,
            x: 1,
          },
        ],
        events: [],
        totalWeight: 2
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

    const event65992 = wrapper.find('[draggable]')
    event65992.trigger('drag')
  })

  it.todo('allows user to drag an object')
})
