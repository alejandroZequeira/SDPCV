<template>
  <div>
    <h1>Analytics Dashboard</h1>

    <input type="file" @change="handleCSV" />

    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Chart from 'chart.js/auto'

const chartCanvas = ref(null)

const handleCSV = async (event) => {
  const file = event.target.files[0]
  const text = await file.text()

  const rows = text.split("\n").slice(1)
  const labels = []
  const suben = []
  const bajan = []

  rows.forEach(r => {
    const cols = r.split(",")
    if(cols.length >= 3){
      labels.push(cols[0])
      suben.push(parseInt(cols[1]))
      bajan.push(parseInt(cols[2]))
    }
  })

  new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Suben', data: suben },
        { label: 'Bajan', data: bajan }
      ]
    }
  })
}
</script>