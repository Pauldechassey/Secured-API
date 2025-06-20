<template>
  <div class="page-container">
    <h1 class="page-title">Sign in</h1>
    <div class="content-container">
      <p class="subtitle">
        Not registered yet?
        <router-link to="/register">Create an account</router-link>
      </p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Email address</label>
          <input 
            v-model="username" 
            type="email" 
            id="username" 
            required
            oninvalid="this.setCustomValidity('Please enter an email address')"
            oninput="this.setCustomValidity('')"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input 
            v-model="password" 
            type="password" 
            id="password" 
            required
            oninvalid="this.setCustomValidity('Please enter your password')"
            oninput="this.setCustomValidity('')"
          />
        </div>

        <button type="submit">Sign in</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    error.value = ''

    // Create form data
    const formData = new FormData()
    formData.append('username', username.value)
    formData.append('password', password.value)
    formData.append('grant_type', 'password')

    const response = await fetch('https://localhost:8000/login', {
      method: 'POST',
      body: formData,
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Invalid credentials')
    }

    // Store token and redirect
    localStorage.setItem('token', data.access_token)
    await router.push('/decompose')

  } catch (err) {
    // Single error handling point
    console.error('Login failed:', err)
    error.value = err instanceof Error ? err.message : 'Authentication failed'
  }
}
</script>

<style scoped>

/* Existing styles */
.page-title {
  text-align: center;
  color: rgb(60, 96, 120);
  margin-bottom: 2rem;
  font-size: 1.7rem;
}

.content-container {
  width: 90%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 1rem;
}

.subtitle {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.25rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: rgb(60, 96, 120);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}

.error {
  margin-top: 1rem;
  color: red;
  text-align: center;
}

@media (prefers-color-scheme: dark) {
  .page-container {
    background-color: #1a1a1a;
    color: #ffffff;
  }

  .content-container {
    background-color: #2d2d2d;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  .page-title {
    color: rgb(84, 143, 88);
  }

  input {
    background-color: #3d3d3d;
    border-color: #505050;
    color: white;
  }

  input:focus {
    border-color: rgb(84, 143, 88);
  }

  button {
    background-color: rgb(84, 143, 88);
  }

  button:hover {
    background-color: rgb(69, 123, 72);
  }

  .subtitle {
    color: #e0e0e0;
  }

  a {
    color: rgb(77, 189, 199);;
  }

  .error {
    color: #ff6b6b;
  }
}
</style>
