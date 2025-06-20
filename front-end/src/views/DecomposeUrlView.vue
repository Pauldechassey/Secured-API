<template>
  <div class="page-container">
    <h2 class="sub-title">Analyze your URL</h2>
    <div class="main-content">
      <form @submit.prevent="handleSubmit" class="search-form">
        <div class="search-group">
          <input 
            v-model="url" 
            type="text" 
            placeholder="https://example.com/..." 
            required
            oninvalid="this.setCustomValidity('Please enter a URL')"
            oninput="this.setCustomValidity('')"
            class="search-input"
            :class="{ 'error': error }"
          />
          <button type="submit" class="analyze-button">Analyze</button>
        </div>
      </form>

      <!-- Error message -->
      <div v-if="error" class="error-message">
        <h3>{{ error.message }}</h3>
        <ul v-if="error.rules">
          <li v-for="(rule, index) in error.rules" :key="index">{{ rule }}</li>
        </ul>
        <div v-if="error.examples" class="examples">
          <p>Valid examples:</p>
          <ul>
            <li v-for="(example, index) in error.examples" :key="index">{{ example }}</li>
          </ul>
        </div>
      </div>

      <!-- Résultats de l'analyse -->
      <div v-if="result" class="result-table">
        <table>
          <thead>
            <tr>
              <th>Composant</th>
              <th>Valeur</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Schéma</td>
              <td>{{ result.scheme }}</td>
            </tr>
            <tr>
              <td>Nom d'hôte</td>
              <td>{{ result.netloc }}</td>
            </tr>
            <tr>
              <td>Port</td>
              <td>{{ result.port || '-' }}</td>
            </tr>
            <tr>
              <td>Chemin</td>
              <td>{{ result.path || '/' }}</td>
            </tr>
            <tr>
              <td>Paramètres</td>
              <td>{{ result.query_string || '-' }}</td>
            </tr>
            <tr v-if="result.query_params">
              <td>Paramètres décodés</td>
              <td>
                <div v-for="(values, key) in result.query_params" :key="key">
                  {{ key }}: {{ values.join(', ') }}
                </div>
              </td>
            </tr>
            <tr>
              <td>Fragment</td>
              <td>{{ result.fragment || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

type ErrorType = {
  message: string
  rules?: string[]
  examples?: string[]
} | null

const url = ref('')
const result = ref<any | null>(null)
const error = ref<ErrorType>(null)

const handleSubmit = async () => {
  try {
    error.value = null
    const response = await fetch('https://localhost:8000/parse_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url.value })
    })

    const data = await response.json()

    if (!response.ok) {
      if (data.detail) {
        const translatedDetail = {
          ...data.detail,
          message: "Invalid URL format",
          rules: [
            "Must start with http:// or https://",
            "Domain must be valid (no underscores)",
            "Domain must contain valid characters (a-z, 0-9, hyphen)",
            "Must have a valid TLD"
          ],
          examples: data.detail.examples
        }
        error.value = translatedDetail
      }
      result.value = null
      return
    }

    result.value = data
    error.value = null
  } catch (err) {
    console.error('Error:', err)
    error.value = {
      message: "An error occurred while analyzing the URL",
      examples: [
        "https://www.example.com",
        "https://api.github.com:443/repos/user/repo",
        "http://localhost:8000/api"
      ]
    }
  }
}
</script>

<style scoped>

.page-container {
  min-height: 100vh;
  background-color: #f9f9f9;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title {
  margin: 0;
  color: #213547;
  font-size: 1.2rem;
}

.logout {
  background: none;
  border: none;
  color: #213547;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s;
}

.logout:hover {
  transform: scale(1.1);
}

.sub-title {
  text-align: center;
  color: rgb(84, 143, 88);
  margin: 2rem;
  font-size: 1.7rem;
}

.main-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.search-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.search-input.error {
  border-color: #d32f2f;
}

.analyze-button {
  padding: 0.5rem 1rem;
  background-color: rgb(84, 143, 88);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.analyze-button:hover {
  background-color: rgb(69, 123, 72);
}

.error-message {
  background-color: #fff3f3;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  padding: 1rem;
  margin: 1rem 0;
  color: #d32f2f;
}

.error-message h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.error-message ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.examples {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #ffcdd2;
}

.examples p {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.result-table {
  margin-top: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background-color: rgb(84, 143, 88);
  color: white;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.9rem;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: #f1f3f5;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark) {
  .page-container {
    background-color: #1a1a1a;
    color: #ffffff;
  }

  .main-content {
    background-color: #2d2d2d;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  .search-input {
    background-color: #3d3d3d;
    border-color: #505050;
    color: white;
  }

  .search-input:focus {
    border-color: rgb(84, 143, 88);
  }

  .result-table {
    background-color: #2d2d2d;
  }

  table tr:hover {
    background-color: #3d3d3d;
  }

  td {
    border-color: #404040;
    color: #e0e0e0;
  }

  .error-message {
    background-color: #3d2929;
    border-color: #5c3737;
    color: #ff8080;
  }

  .examples {
    border-color: #5c3737;
  }
}
</style>
