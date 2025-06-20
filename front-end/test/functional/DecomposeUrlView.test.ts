import { shallowMount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DecomposeUrlView from '@/views/DecomposeUrlView.vue';

describe('DecomposeUrlView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the component correctly', () => {
    const wrapper = shallowMount(DecomposeUrlView);
    expect(wrapper.find('h2').text()).toBe('Analyze your URL');
    expect(wrapper.find('input[type="text"]').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Analyze');
  });

  it('updates url v-model when input changes', async () => {
    const wrapper = shallowMount(DecomposeUrlView);
    const input = wrapper.find('input[type="text"]');
    await input.setValue('https://test.com');
    expect((wrapper.vm as any).url).toBe('https://test.com');
  });

  it('displays analysis results on successful API call', async () => {
    const mockSuccessResponse = {
      scheme: 'https',
      netloc: 'www.example.com',
      port: null,
      path: '/path/to/resource',
      query_string: 'param1=value1&param2=value2',
      query_params: {
        param1: ['value1'],
        param2: ['value2'],
      },
      fragment: 'section',
    };

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockSuccessResponse),
      })
    ) as any;

    const wrapper = shallowMount(DecomposeUrlView);
    await wrapper.find('input[type="text"]').setValue('https://www.example.com/path/to/resource?param1=value1&param2=value2#section');
    await wrapper.find('form').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.find('.result-table').exists()).toBe(true);

    const rows = wrapper.findAll('tbody tr');

    expect(rows[0].findAll('td')[1].text()).toBe('https');
    expect(rows[1].findAll('td')[1].text()).toBe('www.example.com');
    expect(rows[2].findAll('td')[1].text()).toBe('-');
    expect(rows[3].findAll('td')[1].text()).toBe('/path/to/resource');
    expect(rows[4].findAll('td')[1].text()).toBe('param1=value1&param2=value2');

    expect(rows[5].findAll('td')[1].text()).toContain('param1: value1');
    expect(rows[5].findAll('td')[1].text()).toContain('param2: value2');

    expect(rows[6].findAll('td')[1].text()).toBe('section');

  });

  it('displays error message for invalid URL format from API', async () => {
    const mockErrorResponse = {
      detail: {
        message: "URL validation failed",
        rules: [
          "Must start with http:// or https://",
          "Domain must be valid (no underscores)",
        ],
        examples: [
          "https://www.example.com",
          "http://localhost:8000"
        ]
      }
    };

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve(mockErrorResponse),
      })
    ) as any;

    const wrapper = shallowMount(DecomposeUrlView);
    await wrapper.find('input[type="text"]').setValue('invalid-url');
    await wrapper.find('form').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message h3').text()).toBe('Invalid URL format');
    expect(wrapper.find('.error-message ul').text()).toContain('Must start with http:// or https://');
    expect(wrapper.find('.error-message ul').text()).toContain('Domain must be valid (no underscores)');
    expect(wrapper.find('.examples').text()).toContain('Valid examples:');
    expect(wrapper.find('.examples').text()).toContain('https://www.example.com');
  });

  it('displays generic error message for network or unexpected errors', async () => {
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error'))) as any;

    const wrapper = shallowMount(DecomposeUrlView);
    await wrapper.find('input[type="text"]').setValue('https://example.com');
    await wrapper.find('form').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message h3').text()).toBe('An error occurred while analyzing the URL');
    expect(wrapper.find('.examples').text()).toContain('Valid examples:');
  });

  it('clears error and result when a new URL is submitted', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: { message: "error" } }),
      })
    ) as any;
    const wrapper = shallowMount(DecomposeUrlView);
    await wrapper.find('input[type="text"]').setValue('invalid');
    await wrapper.find('form').trigger('submit');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.error-message').exists()).toBe(true);
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ scheme: 'http', netloc: 'good.com' }),
      })
    ) as any;
    await wrapper.find('input[type="text"]').setValue('http://good.com');
    await wrapper.find('form').trigger('submit');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.error-message').exists()).toBe(false);
    expect(wrapper.find('.result-table').exists()).toBe(true);
  });
});
