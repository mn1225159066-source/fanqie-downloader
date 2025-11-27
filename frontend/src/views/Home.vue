<template>
  <div class="home">
    <h1>欢迎来到 Fanqie 网站</h1>
    <p>前端已就绪，后端 API 路径：{{ apiBase }}</p>
  </div>
</template>

<script setup lang="ts">
const apiBase = import.meta.env.VITE_API_BASE || '/api'
</script>

<style scoped>
.home { padding: 24px; }
</style>