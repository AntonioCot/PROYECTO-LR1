<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex flex-col">
    <!-- Encabezado -->
    <header class="py-8 bg-white shadow-md">
      <h1 class="text-5xl md:text-5xl font-extrabold text-center text-blue-600 drop-shadow-sm">
        Analizador LR(1)
      </h1>
    </header>

    <!-- Contenido principal -->
    <main class="flex-1 px-6 lg:px-20 xl:px-32 py-10 overflow-auto">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 h-full">
        <!-- Sección izquierda -->
        <section class="bg-white rounded-2xl shadow-md p-6 flex flex-col justify-between">
          <InputForm
            v-model="formData"
            :loading="loading"
            @analyze="analyze"
          />
        </section>

        <!-- Sección derecha -->
        <section class="bg-white rounded-2xl shadow-md p-6 flex flex-col justify-between">
          <ResultDisplay
            :result="result"
            :error="error"
          />
        </section>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-6 text-center text-gray-500 text-sm bg-white border-t">
      © {{ new Date().getFullYear() }} Proyecto LR(1) — Desarrollado con ❤️ por Antonio
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import InputForm from './components/InputForm.vue'
import ResultDisplay from './components/ResultDisplay.vue'

const formData = reactive({
  grammar: '',
  input: ''
})

const result = ref(null)
const loading = ref(false)
const error = ref(null)

const API_URL = 'https://proyecto-lr1.onrender.com/api/v1/parse'

const analyze = async () => {
  if (!formData.grammar.trim() || !formData.input.trim()) {
    error.value = 'Por favor, ingresa tanto la gramática como los tokens de entrada.'
    return
  }

  loading.value = true
  error.value = null
  result.value = null
  
  try {
    // Procesar tokens correctamente: separar por espacios y comas, eliminar vacíos
    const tokens = formData.input
      .replace(/\s*,\s*/g, ',') // Normaliza espacios alrededor de comas
      .split(/\s+|,/)           // Divide por espacios o comas
      .filter(token => token.length > 0)

    const response = await axios.post(API_URL, {
      grammar: formData.grammar,
      tokens: tokens
    })
    result.value = response.data
  } catch (err) {
    console.error('Error:', err)
    if (err.response?.data) {
      error.value = `Error: ${JSON.stringify(err.response.data)}`
    } else if (err.message.includes('Network Error')) {
      error.value = 'Error de conexión. Asegúrate de que la API esté disponible.'
    } else {
      error.value = 'Error al procesar la solicitud. Por favor, intenta de nuevo.'
    }
  } finally {
    loading.value = false
  }
}

// Cargar ejemplo inicial
formData.grammar = `S -> D
D -> T V
T -> int
T -> float
V -> id , V
V -> id`
formData.input = 'float id , id , id'
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Pantalla completa y márgenes adaptables */
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

/* Mejor contraste en pantallas grandes */
@media (min-width: 1536px) {
  main {
    max-width: 1800px;
    margin: 0 auto;
  }
}
</style>
