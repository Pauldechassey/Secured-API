<template>
  <div class="page-container">
    <h1 class="title">Create account</h1>
    <div class="content-container">
      <p class="sub-title">
        Already have an account? 
        <router-link to="/login">Sign in</router-link>
      </p>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="fullname">Full name</label>
          <input 
            v-model="fullname" 
            type="text" 
            id="fullname" 
            required
            oninvalid="this.setCustomValidity('Please enter your full name')"
            oninput="this.setCustomValidity('')"
          />
        </div>

        <div class="form-group">
          <label for="email">Email address</label>
          <input 
            v-model="email" 
            type="email" 
            id="email" 
            required
            oninvalid="this.setCustomValidity(this.validity.typeMismatch ? 'Please enter a valid email address (example@domain.com)' : 'Please enter your email address')"
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

        <div class="form-group">
          <label for="password_confirmation">Confirm Password</label>
          <input 
            v-model="password_confirmation" 
            type="password" 
            id="password_confirmation" 
            required 
            :class="{ 'error-input': !passwordsMatch && password_confirmation }"
            oninvalid="this.setCustomValidity('Please confirm your password')"
            oninput="this.setCustomValidity('')"
          />
          <span v-if="!passwordsMatch && password_confirmation" class="error-text">
            Passwords do not match
          </span>
        </div>

        <button type="submit" :disabled="!passwordsMatch">Create account</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const fullname = ref('')
const email = ref('')
const password = ref('')
const password_confirmation = ref('')
const error = ref('')

const passwordsMatch = computed(() => {
  return password.value === password_confirmation.value
})

const handleRegister = async () => {
  try {
    // Validation côté client
    if (password.value !== password_confirmation.value) {
      error.value = 'Les mots de passe ne correspondent pas'
      return
    }

    // S'assurer que le mot de passe est assez fort
    if (password.value.length < 8 || 
        !/[A-Z]/.test(password.value) || 
        !/[a-z]/.test(password.value) || 
        !/[0-9]/.test(password.value) || 
        !/[!@#$%^&*]/.test(password.value)) {
      error.value = 'Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial'
      return
    }

    const response = await fetch('https://localhost:8000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        fullname: fullname.value
      })
    })

    const data = await response.json()
    console.log('Server response:', data) // Debug log

    if (!response.ok) {
      if (data.detail === 'Email already registered') {
        throw new Error('An account already exists with this email address')
      }
      throw new Error(data.detail?.message || 'Registration failed')
    }

    router.push('/login')
  } catch (err: any) {
    console.error('Error:', err)
    error.value = err.message
  }
}
</script>

<style scoped>
.title {
  text-align: center;
  font-size: 1.7rem;
  color: rgb(60, 96, 120);
  margin-bottom: 2rem;
}

.subtitle {
  text-align: center;
  margin-bottom: 1.5rem;
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
  background-color:rgb(60, 96, 120);
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

.error-input {
  border-color: red !important;
}

.error-text {
  color: red;
  font-size: 0.8rem;
  margin-top: 0.2rem;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark) {
  .page-container {
    background-color: #1a1a1a;
    color: #ffffff;
  }

  .content-container {
    background-color: #2d2d2d;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  .title {
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
    color: rgb(77, 189, 199);
  }

  .error {
    color: #ff6b6b;
  }
}
</style>
