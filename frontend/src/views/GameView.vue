<script setup>
import { ref, onMounted, computed, watch, onUnmounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, ArrowLeft, QuestionFilled, Trophy } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const isLoading = ref(true)
const sessionId = ref('')
const puzzle = ref('')
const messages = ref([])
const newMessage = ref('')
const score = ref(0)
const gameOver = ref(false)
const isSending = ref(false)
const game_state = ref({
  completed: false,
  answered: false
})

// Game settings from route params
const gameSettings = reactive({
  difficulty: route.query.difficulty || 'medium',
  puzzleLength: route.query.puzzleLength || 'medium',
  theme: route.query.theme || 'random'
})

// API endpoint
const API_URL = 'http://localhost:5001/api'

// Start a new game
const startNewGame = async () => {
  isLoading.value = true
  try {
    // Pass the game settings to the backend
    const response = await axios.post(`${API_URL}/start_game`, {
      difficulty: gameSettings.difficulty,
      puzzleLength: gameSettings.puzzleLength,
      theme: gameSettings.theme
    })
    
    if (response.data.success) {
      sessionId.value = response.data.session_id
      puzzle.value = response.data.puzzle
      score.value = response.data.score || 0
      
      // Add the initial AI message
      messages.value.push({
        sender: 'ai',
        text: response.data.message,
        time: new Date().toLocaleTimeString()
      })

      ElMessage({
        message: `Created a ${gameSettings.difficulty} difficulty puzzle about ${gameSettings.theme !== 'random' ? gameSettings.theme : 'a random topic'}!`,
        type: 'success'
      })
    } else {
      messages.value.push({
        sender: 'system',
        text: 'Error starting game. Please try again.',
        time: new Date().toLocaleTimeString()
      })

      ElMessage.error('Failed to create puzzle. Please try again.')
    }
  } catch (error) {
    console.error('Error starting game:', error)
    messages.value.push({
      sender: 'system',
      text: 'Server error. Please try again later.',
      time: new Date().toLocaleTimeString()
    })

    ElMessage.error('Server error. Please try again later.')
  } finally {
    isLoading.value = false
  }
}

// Handle user message submission
const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value || isSending.value) return
  
  const messageText = newMessage.value.trim()
  newMessage.value = ''
  
  // Set sending state to true to prevent double submissions
  isSending.value = true
  
  // Add user message to chat
  messages.value.push({
    sender: 'user',
    text: messageText,
    time: new Date().toLocaleTimeString()
  })
  
  // Scroll immediately after adding user message
  scrollToBottom()
  
  // Set loading state
  isLoading.value = true
  
  try {
    const response = await axios.post(`${API_URL}/ask`, {
      session_id: sessionId.value,
      question: messageText
    })
    
    if (response.data.success) {
      // Add AI response to chat
      messages.value.push({
        sender: 'ai',
        text: response.data.message,
        time: new Date().toLocaleTimeString()
      })
      
      // Update game state
      score.value = response.data.score || score.value
      
      // 不立即显示游戏结束对话框，除非玩家明确请求
      // 将服务器返回的game_over状态保存但不立即显示对话框
      if (response.data.game_over) {
        game_state.value = {
          ...game_state.value,
          completed: true
        }
      }
    } else {
      messages.value.push({
        sender: 'system',
        text: response.data.error || 'Error processing your request.',
        time: new Date().toLocaleTimeString()
      })
      
      // 不立即显示游戏结束对话框，除非玩家明确请求
      // 将服务器返回的game_over状态保存但不立即显示对话框
      if (response.data.game_over) {
        game_state.value = {
          ...game_state.value,
          completed: true
        }
      }
    }
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      sender: 'system',
      text: 'Server error. Please try again later.',
      time: new Date().toLocaleTimeString()
    })
  } finally {
    isLoading.value = false
    isSending.value = false
    
    // Force scroll to bottom after all states are updated
    setTimeout(() => {
      scrollToBottom()
    }, 100)
  }
}

// Start a new game
const playAgain = async () => {
  isLoading.value = true
  gameOver.value = false
  messages.value = []
  score.value = 0
  game_state.value = {
    completed: false,
    answered: false
  }
  await startNewGame()
}

// 手动完成游戏
const completeGame = () => {
  if (game_state.value.answered) {
    gameOver.value = true
  }
}

// Show answer button handler
const showAnswer = async () => {
  if (gameOver.value) return
  
  isLoading.value = true
  isSending.value = true
  
  try {
    const response = await axios.post(`${API_URL}/get_solution`, {
      session_id: sessionId.value
    })
    
    if (response.data.success) {
      // Add AI response with the solution
      messages.value.push({
        sender: 'ai',
        text: `💡 The answer is revealed: The complete solution to the puzzle is: ${response.data.solution}`,
        time: new Date().toLocaleTimeString()
      })
      
      // 标记游戏已获得解答，但不立即显示游戏结束对话框
      game_state.value = {
        ...game_state.value,
        answered: true,
        completed: true
      }
    } else {
      messages.value.push({
        sender: 'system',
        text: response.data.error || 'Cannot get answer',
        time: new Date().toLocaleTimeString()
      })
      
      ElMessage.error('Cannot get answer')
    }
  } catch (error) {
    console.error('Error getting solution:', error)
    messages.value.push({
      sender: 'system',
      text: 'Server error, please try again later',
      time: new Date().toLocaleTimeString()
    })
    
    ElMessage.error('Server error, please try again later')
  } finally {
    isLoading.value = false
    isSending.value = false
    scrollToBottom()
  }
}

// Check if message input should be disabled
const isInputDisabled = computed(() => {
  return isLoading.value || gameOver.value
})

const messagesContainer = ref(null)

// Auto-scroll to the bottom of the message container
const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 50)
}

// Watch for new messages and scroll to bottom
const watchMessages = (val, oldVal) => {
  if (val.length !== oldVal.length || isLoading.value) {
    scrollToBottom()
  }
}

// Watch for loading state changes
watch(isLoading, (newVal) => {
  if (!newVal) {
    // When loading finishes, scroll to bottom
    scrollToBottom()
  }
})

// Return to home page
const goHome = () => {
  router.push('/')
}

// Initialize the component
onMounted(() => {
  startNewGame()
  // Set initial scroll position
  scrollToBottom()
})

// Set up watcher for messages
const unwatchMessages = watch(
  () => messages.value,
  watchMessages,
  { deep: true }
)

// Clean up when component is unmounted
onUnmounted(() => {
  if (unwatchMessages) {
    unwatchMessages()
  }
})
</script>

<template>
  <div class="game-view">
    <div class="game-layout">
      <!-- 游戏头部 -->
      <div class="game-header">
        <div class="title-section">
          <h1>Lateral Thinking Puzzles</h1>
          <div class="game-meta">
            <span>Score: {{ score }}</span>
          </div>
        </div>
        <div class="action-buttons">
          <el-button-group>
            <el-button @click="() => router.push('/')" type="info" plain>
              <el-icon><ArrowLeft /></el-icon> Back to Home
            </el-button>
            <el-button @click="showAnswer" type="warning" plain v-if="!game_state.answered">
              <el-icon><QuestionFilled /></el-icon> Show Answer
            </el-button>
            <el-button @click="completeGame" type="success" plain v-if="game_state.answered && !gameOver">
              <el-icon><Check /></el-icon> Complete Game
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <!-- 游戏内容区域 -->
      <div class="game-content">
        <!-- 谜题区域 -->
        <div class="puzzle-section">
          <el-card shadow="hover" class="puzzle-card">
            <template #header>
              <div class="puzzle-header">
                <el-icon><QuestionFilled /></el-icon>
                <span>Puzzle</span>
              </div>
            </template>
            <p class="puzzle-text">{{ puzzle }}</p>
          </el-card>
        </div>
        
        <!-- 聊天区域 -->
        <div class="chat-section">
          <el-card shadow="hover" class="chat-card">
            <div class="message-container" ref="messagesContainer">
              <div
                v-for="(message, index) in messages"
                :key="index"
                :class="['message', `message-${message.sender}`, 'fade-in']"
              >
                <div class="message-content">
                  <p v-html="message.text.replace(/\n/g, '<br>')"></p>
                </div>
                <span class="message-time">{{ message.time }}</span>
              </div>
              
              <div v-if="isLoading" class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
              </div>
            </div>
            
            <div class="message-input-container">
              <el-input
                v-model="newMessage"
                type="textarea"
                :rows="2"
                placeholder="Type your question..."
                :disabled="isInputDisabled"
                @keyup.enter.native="sendMessage"
                resize="none"
              ></el-input>
              <el-button
                type="primary"
                @click="sendMessage"
                :loading="isSending"
                :disabled="isInputDisabled || !newMessage.trim()"
                icon="Position"
                round
              >
                Send
              </el-button>
            </div>
            
            <div v-if="gameOver" class="game-over-container">
              <el-alert
                title="Puzzle Solved!"
                type="success"
                :closable="false"
                show-icon
                center
              >
                <template #default>
                  <p>Congratulations! You've solved this puzzle!</p>
                </template>
              </el-alert>
              <el-button type="primary" @click="sendMessage" :loading="isSending" :disabled="isInputDisabled" icon="Position" round>
                Send
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>
      
    <!-- Portrait mode hint -->
    <div class="portrait-hint">
      <p><el-icon><ArrowUp /></el-icon> Swipe up to see more of the puzzle</p>
    </div>
      
    <!-- Game Over Dialog -->
    <el-dialog
      v-model="gameOver"
      title="Puzzle Solved!"
      width="80%"
      center
      :show-close="false"
      class="game-over-dialog"
    >
      <div class="game-over-content">
        <el-icon class="success-icon"><SuccessFilled /></el-icon>
        <h2>Congratulations on solving the puzzle!</h2>
        <p class="score-text">Your score: <span class="highlight">{{ score }}</span></p>
        <div class="dialog-buttons">
          <el-button @click="playAgain" type="success" class="play-again-btn" round>
            Play Again
          </el-button>
          <el-button @click="() => router.push('/')" plain round>
            Back to Home
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
/* 全局游戏样式 */
.game-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 0;
  position: relative;
}

.game-layout {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 游戏头部样式 */
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

h1 {
  margin: 0;
  color: #409EFF;
  font-size: 1.8rem;
  font-weight: 600;
}

.game-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.score-tag {
  padding: 6px 12px;
  font-weight: 600;
}

.settings-tag {
  text-transform: capitalize;
  padding: 6px 12px;
}

/* 游戏内容区域样式 */
.game-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  flex: 1;
}

/* 横屏布局 */
@media (min-width: 768px) {
  .game-content {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }
  
  .portrait-hint {
    display: none;
  }
}

/* 谜题区域样式 */
.puzzle-card {
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border-left: 3px solid #409EFF;
  transition: all 0.3s ease;
}

.puzzle-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #409EFF;
  padding: 5px 0;
}

.puzzle-text {
  font-size: 1.1rem;
  line-height: 1.7;
  padding: 10px;
  margin: 0;
  color: #303133;
  white-space: pre-wrap;
}

/* 聊天区域样式 */
.chat-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 20px 80px 20px; 
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-user {
  align-self: flex-end;
  background-color: #409EFF;
  color: white;
  border-bottom-right-radius: 2px;
}

.message-ai {
  align-self: flex-start;
  background-color: #f2f6fc;
  color: #606266;
  border-bottom-left-radius: 2px;
}

.message-system {
  align-self: center;
  background-color: #fef0f0;
  color: #f56c6c;
  border-radius: 8px;
  text-align: center;
  max-width: 90%;
}

.message-content p {
  margin: 0;
  line-height: 1.5;
  word-break: break-word;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  position: absolute;
  bottom: -20px;
  right: 10px;
}

.message-ai .message-time {
  left: 10px;
  right: auto;
}

.typing-indicator {
  align-self: flex-start;
  display: flex;
  gap: 6px;
  padding: 12px 16px;
  background-color: #f2f6fc;
  border-radius: 12px;
  border-bottom-left-radius: 2px;
  margin: 10px 0 30px 0;
}

@keyframes typing {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
  100% { transform: translateY(0px); }
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  animation: typing 1s infinite;
}

.typing-dot:nth-child(1) { animation-delay: 0.1s; }
.typing-dot:nth-child(2) { animation-delay: 0.3s; }
.typing-dot:nth-child(3) { animation-delay: 0.5s; }

.message-input-container {
  display: flex;
  gap: 10px;
  padding: 15px;
  border-top: 1px solid #ebeef5;
  background-color: white;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.el-textarea {
  flex: 1;
}

/* 竖屏提示 */
.portrait-hint {
  display: none;
  position: fixed;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 20px;
  margin: 0 auto;
  width: 200px;
  z-index: 100;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.portrait-hint .el-icon {
  margin-right: 5px;
  animation: arrowUp 1s infinite;
}

@keyframes arrowUp {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 竖屏模式下显示提示并调整布局 */
@media (max-width: 767px) {
  .game-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .action-buttons {
    width: 100%;
    display: flex;
    justify-content: space-between;
  }
  
  .portrait-hint {
    display: block;
  }
  
  .puzzle-card {
    margin-bottom: 15px;
  }
  
  .chat-section {
    margin-bottom: 60px;
  }
}

/* 游戏结束对话框样式 */
.game-over-dialog {
  border-radius: 20px;
}

.game-over-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 60px;
  color: #67C23A;
  margin-bottom: 20px;
}

.game-over-content h2 {
  font-size: 24px;
  color: #67C23A;
  margin: 10px 0;
}

.score-text {
  font-size: 18px;
  margin: 20px 0;
  color: #606266;
}

.highlight {
  color: #409EFF;
  font-weight: bold;
  font-size: 24px;
}

.dialog-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.play-again-btn {
  font-size: 16px;
  padding: 12px 24px;
}
</style>
