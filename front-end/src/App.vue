<template>
  <div>
    <nav class="navbar">
      <div class="nav-left">
        <span class="brand">
          URLink
        </span>
      </div>
      <div class="nav-right">
        <button v-if="showLogoutButton" @click="logout" class="logout-btn">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const showLogoutButton = computed(() => {
  return route.path === '/decompose';
});

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: rgb(60, 96, 120);
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.brand {
  font-weight: bold;
  font-size: 2rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: linear-gradient(45deg, #ffffff, rgb(84, 143, 88));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: none;
  letter-spacing: 1px;
  user-select: none;
  cursor: default;
}

.brand-accent {
  color: rgb(84, 143, 88);
  font-weight: 600;
  font-style: italic;
}

.logout-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  transition: transform 0.2s;
}

.logout-btn:hover {
  transform: scale(1.1);
}
</style>
