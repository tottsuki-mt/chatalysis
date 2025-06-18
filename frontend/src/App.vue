<template>
  <div class="container mx-auto p-4">
    <UploadArea :sessionId="sessionId" @uploaded="handleUploaded" />
    <ChatWindow :messages="messages" @send="sendMessage" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UploadArea from './components/UploadArea.vue'
import ChatWindow from './components/ChatWindow.vue'
import axios from 'axios'

const messages = ref([])
const sessionId = Math.random().toString(36).substring(2)

const handleUploaded = (cols) => {
  messages.value.push({ sender: 'system', text: `Uploaded CSV with columns: ${cols.join(', ')}` })
}

const sendMessage = async (text) => {
  messages.value.push({ sender: 'user', text })
  const form = new FormData()
  form.append('session_id', sessionId)
  form.append('message', text)
  const res = await axios.post('/api/chat', form)
  messages.value.push({ sender: 'bot', text: res.data.reply })
}
</script>
