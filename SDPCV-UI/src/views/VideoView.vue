<template>
  <div class="layout">

    <!-- PANEL IZQUIERDO -->
    <aside>
      <h3>Controles</h3>

      <!-- Subir Videos -->
      <input type="file" multiple @change="uploadVideos" />

      <!-- Seleccionar Video -->
      <select v-model="selectedVideo">
        <option disabled value="">Seleccionar video</option>
        <option v-for="v in videos" :key="v" :value="v">
          {{ v }}
        </option>
      </select>

      <!-- Botones -->
      <button @click="start">▶ Iniciar</button>
      <button @click="exportCSV">📥 Exportar CSV</button>

      <!-- Velocidad -->
      <label>Velocidad: {{ speed }}x</label>
      <input
        type="range"
        min="0.5"
        max="2"
        step="0.1"
        v-model="speed"
      />

      <!-- Contadores -->
      <div class="stats">
        <p>⬆ Entraron: {{ suben }}</p>
        <p>⬇ Salieron: {{ bajan }}</p>
      </div>
    </aside>

    <!-- AREA VIDEO -->
    <div class="video-area">
      <canvas ref="canvas"></canvas>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"

const canvas = ref(null)
let ctx

const videos = ref([])
const selectedVideo = ref("")
const suben = ref(0)
const bajan = ref(0)
const speed = ref(1)

let ws = null
let lastFrameImage = null

// 🔲 Rectángulo editable
const rect = ref({
  x: 200,
  y: 150,
  width: 300,
  height: 200
})

let isDragging = false
let offsetX = 0
let offsetY = 0

// --------------------
// SUBIR VIDEOS
// --------------------
const uploadVideos = async (e) => {
  const formData = new FormData()

  for (let file of e.target.files) {
    formData.append("files", file)
  }

  const res = await fetch("http://localhost:8000/upload", {
    method: "POST",
    body: formData
  })

  const data = await res.json()
  videos.value = data.videos
}

// --------------------
// INICIAR STREAMING
// --------------------
const start = async () => {

  if (!selectedVideo.value) {
    alert("Selecciona un video primero")
    return
  }

  await fetch(
    "http://localhost:8000/select?name=" + selectedVideo.value,
    { method: "POST" }
  )

  if (ws) ws.close()

  ws = new WebSocket("ws://localhost:8000/ws")

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    suben.value = data.suben
    bajan.value = data.bajan

    const img = new Image()
    img.src = "data:image/jpeg;base64," + data.frame

    img.onload = () => {
      lastFrameImage = img
      drawFrame()
    }
  }
}

// --------------------
// DIBUJAR FRAME
// --------------------
function drawFrame() {
  if (!lastFrameImage) return

  ctx.clearRect(0, 0, 900, 500)
  ctx.drawImage(lastFrameImage, 0, 0, 900, 500)

  // Dibujar zona
  ctx.strokeStyle = "red"
  ctx.lineWidth = 3
  ctx.strokeRect(
    rect.value.x,
    rect.value.y,
    rect.value.width,
    rect.value.height
  )

  ctx.fillStyle = "rgba(255,0,0,0.2)"
  ctx.fillRect(
    rect.value.x,
    rect.value.y,
    rect.value.width,
    rect.value.height
  )
}

// --------------------
// ENVIAR ZONA
// --------------------
const sendRectToBackend = async () => {
  await fetch("http://localhost:8000/set_zone", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(rect.value)
  })
}

// --------------------
// VELOCIDAD
// --------------------
watch(speed, async (newSpeed) => {
  await fetch("http://localhost:8000/set_speed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ speed: newSpeed })
  })
})

// --------------------
// EXPORTAR CSV
// --------------------
const exportCSV = () => {
  window.open("http://localhost:8000/export")
}

// --------------------
// CANVAS EVENTS
// --------------------
onMounted(() => {

  ctx = canvas.value.getContext("2d")
  canvas.value.width = 900
  canvas.value.height = 500

  canvas.value.addEventListener("mousedown", (e) => {
    const r = canvas.value.getBoundingClientRect()
    const mx = e.clientX - r.left
    const my = e.clientY - r.top

    if (
      mx > rect.value.x &&
      mx < rect.value.x + rect.value.width &&
      my > rect.value.y &&
      my < rect.value.y + rect.value.height
    ) {
      isDragging = true
      offsetX = mx - rect.value.x
      offsetY = my - rect.value.y
    }
  })

  canvas.value.addEventListener("mousemove", (e) => {
    if (!isDragging) return

    const r = canvas.value.getBoundingClientRect()
    rect.value.x = e.clientX - r.left - offsetX
    rect.value.y = e.clientY - r.top - offsetY

    drawFrame()
  })

  canvas.value.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false
      sendRectToBackend()
    }
  })
})
</script>

<style>
.layout {
  display: flex;
  height: 100%;
}

aside {
  width: 260px;
  background: #1e1e2f;
  color: white;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

aside select,
aside input[type="file"] {
  padding: 5px;
}

aside button {
  padding: 8px;
  border: none;
  cursor: pointer;
  background: #00c896;
  color: white;
  font-weight: bold;
}

aside button:hover {
  background: #00a87c;
}

.stats {
  margin-top: 15px;
  font-size: 14px;
}

.video-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #111;
}

canvas {
  border: 2px solid #333;
}
</style>