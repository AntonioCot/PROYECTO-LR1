<template>
  <div class="space-y-6">
    <!-- Gramática -->
    <div class="bg-white shadow-lg rounded-xl p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Gramática
      </h2>
      <textarea
        v-model="modelValue.grammar"
        class="w-full h-48 p-4 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition duration-200 font-mono"
        placeholder="Ejemplo:
S -> D
D -> T V
T -> int
T -> float
V -> id , V
V -> id"
        @input="$emit('update:modelValue', { ...modelValue, grammar: $event.target.value })"
      ></textarea>
    </div>

    <!-- Tokens de entrada -->
    <div class="bg-white shadow-lg rounded-xl p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Tokens de entrada
      </h2>
      <textarea
        v-model="modelValue.input"
        class="w-full h-32 p-4 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition duration-200 font-mono"
        placeholder="Ejemplo: float id , id , id"
        @input="$emit('update:modelValue', { ...modelValue, input: $event.target.value })"
      ></textarea>
    </div>

    <!-- Botón de análisis -->
    <div class="flex justify-center">
      <button
        @click="$emit('analyze')"
        class="w-full sm:w-auto px-8 py-3 bg-primary-600 text-white text-lg font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-4 focus:ring-primary-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        :disabled="loading || !modelValue.grammar.trim() || !modelValue.input.trim()"
      >
        <span v-if="loading" class="animate-spin">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        <span>{{ loading ? 'Analizando...' : 'Analizar' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue', 'analyze'])
</script>