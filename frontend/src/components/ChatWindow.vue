<template>
  <div>
    <div class="border p-2 h-96 overflow-y-auto mb-2" ref="chatArea">
      <div v-for="(m, i) in messages" :key="i" class="mb-1">
        <strong>{{ m.sender }}:</strong> {{ m.text }}
      </div>
    </div>
    <div class="flex items-center">
      <input v-model="input" @keyup.enter="emitSend" class="flex-1 border p-2" />
      <button @mousedown="startRecording" @mouseup="stopRecording" class="ml-2 px-2 py-2 bg-gray-300">🎤</button>
      <button @click="emitSend" class="ml-2 px-4 py-2 bg-blue-500 text-white">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
const props = defineProps({ messages: Array })
const emit = defineEmits(['send'])
const input = ref('')
const chatArea = ref(null)
let mediaRecorder
let chunks = []

const emitSend = () => {
  if (!input.value) return
  emit('send', input.value)
  input.value = ''
}

const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  mediaRecorder = new MediaRecorder(stream)
  mediaRecorder.ondataavailable = e => chunks.push(e.data)
  mediaRecorder.onstop = async () => {
    const blob = new Blob(chunks, { type: 'audio/webm' })
    chunks = []
    const form = new FormData()
    form.append('file', blob, 'recording.webm')
    const res = await axios.post('/api/transcribe', form)
    input.value = res.data.text
  }
  mediaRecorder.start()
}

const stopRecording = () => {
  if (mediaRecorder) mediaRecorder.stop()
}

watch(() => props.messages.length, () => {
  chatArea.value.scrollTop = chatArea.value.scrollHeight
})
</script>
