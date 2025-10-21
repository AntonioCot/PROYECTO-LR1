<template>
  <div class="h-full flex flex-col">
    <!-- Mensaje de error -->
    <div v-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-6">
      <div class="flex items-center">
        <svg class="w-6 h-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-red-700">{{ error }}</p>
      </div>
    </div>

    <!-- Resultados del análisis -->
    <div v-if="result" id="results" class="flex-1 bg-white rounded-xl p-6 overflow-y-auto">
      <h2 class="text-xl font-semibold text-gray-800 mb-6 flex items-center sticky top-0 bg-white z-10 py-2">
        <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        Resultados del análisis
      </h2>

      <!-- Estados -->
      <div v-if="result.states" class="mb-8">
        <h3 class="text-lg font-medium text-primary-700 mb-4">Estados LR(1)</h3>
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div v-for="(state, idx) in result.states" :key="idx" class="bg-gray-50 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
            <h4 class="font-semibold text-primary-600 mb-3">Estado {{ idx }}</h4>
            <pre class="text-sm text-gray-800 font-mono whitespace-pre-wrap">{{ formatJSON(state) }}</pre>
          </div>
        </div>
      </div>

      <!-- Tabla de análisis -->
      <div v-if="result.table && result.table.length" class="mb-8">
        <h3 class="text-lg font-medium text-primary-700 mb-4">Tabla de análisis LR(1)</h3>
        <div class="overflow-x-auto bg-gray-50 rounded-lg shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-primary-50">
              <tr>
                <th v-for="header in Object.keys(result.table[0] || {})" :key="header"
                    class="px-4 py-3 text-left text-sm font-semibold text-primary-700 uppercase tracking-wider whitespace-nowrap border-b sticky top-0 bg-primary-50">
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(row, index) in result.table" :key="index">
                <td v-for="(value, key) in row" :key="key"
                    class="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-mono border-b">
                  {{ value }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- First Sets -->
      <div v-if="result.first_sets" class="mt-8">
        <h3 class="text-lg font-medium text-primary-700 mb-4">Conjuntos FIRST</h3>
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div v-for="(set, key) in result.first_sets" :key="key" class="bg-gray-50 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
            <h4 class="font-semibold text-primary-600 mb-3">{{ key }}</h4>
            <pre class="text-sm text-gray-800 font-mono whitespace-pre-wrap">{{ formatJSON(set) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    default: null
  },
  error: {
    type: String,
    default: null
  }
})

const formatJSON = (obj) => {
  return typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2)
}
</script>

<style scoped>
pre {
  word-break: break-word;
  white-space: pre-wrap;
}
</style>