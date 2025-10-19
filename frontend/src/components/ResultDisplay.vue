<template>
  <div class="space-y-6">
    <!-- Mensaje de error -->
    <div v-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
      <div class="flex items-center">
        <svg class="w-6 h-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-red-700">{{ error }}</p>
      </div>
    </div>

    <!-- Resultados del análisis -->
    <div v-if="result" id="results" class="bg-white shadow-lg rounded-xl p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-6 flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        Resultados del análisis
      </h2>

      <!-- Estados -->
      <div v-if="result.states" class="mb-6">
        <h3 class="text-lg font-medium text-gray-700 mb-3">Estados</h3>
        <div class="bg-gray-50 rounded-lg p-4 overflow-x-auto">
          <pre class="text-sm text-gray-800 font-mono">{{ formatJSON(result.states) }}</pre>
        </div>
      </div>

      <!-- Tabla de análisis -->
      <div v-if="result.table" class="mb-6">
        <h3 class="text-lg font-medium text-gray-700 mb-3">Tabla de análisis</h3>
        <div class="overflow-x-auto bg-gray-50 rounded-lg">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-100">
              <tr>
                <th v-for="header in Object.keys(result.table[0] || {})" :key="header"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(row, index) in result.table" :key="index">
                <td v-for="(value, key) in row" :key="key"
                    class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                  {{ value }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- First Sets -->
      <div v-if="result.first_sets" class="mt-6">
        <h3 class="text-lg font-medium text-gray-700 mb-3">First Sets</h3>
        <div class="bg-gray-50 rounded-lg p-4 overflow-x-auto">
          <pre class="text-sm text-gray-800 font-mono">{{ formatJSON(result.first_sets) }}</pre>
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
  return JSON.stringify(obj, null, 2)
}
</script>