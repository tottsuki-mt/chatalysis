<template>
  <div class="mb-4">
    <input type="file" @change="onFileChange" />
  </div>
</template>

<script setup>
import axios from 'axios'
const props = defineProps({ sessionId: String })
const emit = defineEmits(['uploaded'])

const onFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const form = new FormData()
  form.append('session_id', props.sessionId)
  form.append('file', file)
  const res = await axios.post('/api/upload', form)
  emit('uploaded', res.data.columns)
}
</script>
