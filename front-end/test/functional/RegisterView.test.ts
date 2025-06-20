import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import RegisterView from '../../src/views/RegisterView.vue'  
import { createRouter, createWebHistory, type Router } from 'vue-router'

describe('RegisterView', () => {
  let router: Router
  let mockFetch: any

  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: {} },
        { path: '/login', component: {} },
        { path: '/register', component: RegisterView }
      ]
    })
    mockFetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ message: 'Registration successful' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    )
    global.fetch = mockFetch
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders register form correctly', () => {
    const wrapper = mount(RegisterView, {
      global: { 
        plugins: [router] 
      }
    })

    expect(wrapper.find('.title').text()).toBe('Create account')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('validates password confirmation', async () => {
    const wrapper = mount(RegisterView, {
      global: { 
        plugins: [router]
      }
    })

    await wrapper.find('input[type="password"]').setValue('Password123!') // Mot de passe valide
    await wrapper.find('input[id="password_confirmation"]').setValue('different')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-text').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').attributes()).toHaveProperty('disabled')
  })

  it('handles successful registration', async () => {
    const wrapper = mount(RegisterView, {
      global: { 
        plugins: [router],
        stubs: {
          'router-link': true
        }
      }
    })
    await wrapper.find('input[id="fullname"]').setValue('John Doe')
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('Password123!')
    await wrapper.find('input[id="password_confirmation"]').setValue('Password123!')

    await wrapper.find('form').trigger('submit')
    
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(mockFetch).toHaveBeenCalledTimes(1);

    const [url, options] = mockFetch.mock.calls[0];

    expect(url).toBe('http://localhost:8000/register');

    expect(options).toMatchObject({
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const expectedBody = {
      fullname: 'John Doe',
      email: 'test@example.com',
      password: 'Password123!'
    };
    const receivedBody = JSON.parse(options.body);

    expect(receivedBody).toEqual(expectedBody);
  })
})

function flushPromises() {
  return new Promise(resolve => setTimeout(resolve, 0))
}
