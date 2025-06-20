import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginView from '../../src/views/LoginView.vue' 
import { createRouter, createWebHistory } from 'vue-router'

describe('LoginView', () => {
  const router = createRouter({
    history: createWebHistory(),
    routes: [{ path: '/decompose', component: {} }]
  })

  it('renders login form correctly', () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] }
    })
    
    expect(wrapper.find('.page-title').text()).toBe('Sign in')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('handles successful login', async () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] }
    })

    const mockFetch = vi.spyOn(global, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ access_token: 'fake-token' }))
    )

    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/login',
      expect.any(Object)
    )
  })

  it('shows error on invalid credentials', async () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] }
    })

    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('Invalid credentials'))

    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('.error').exists()).toBe(true)
  })
})
