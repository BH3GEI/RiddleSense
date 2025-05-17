<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'

const router = useRouter()
const isLoading = ref(false)

// Game settings
const gameSettings = reactive({
  difficulty: 'medium',
  puzzleLength: 'medium',
  theme: 'random'
})

const difficultyOptions = [
  { label: 'Easy', value: 'easy' },
  { label: 'Medium', value: 'medium' },
  { label: 'Hard', value: 'hard' }
]

const lengthOptions = [
  { label: 'Short', value: 'short' },
  { label: 'Medium', value: 'medium' },
  { label: 'Long', value: 'long' }
]

const themeOptions = [
  { label: 'Random', value: 'random' },
  { label: 'Mystery', value: 'mystery' },
  { label: 'Adventure', value: 'adventure' },
  { label: 'Sci-fi', value: 'scifi' },
  { label: 'Historical', value: 'historical' }
]

const startGame = () => {
  isLoading.value = true
  
  // Pass game settings to the game view via router
  router.push({
    path: '/game',
    query: {
      difficulty: gameSettings.difficulty,
      puzzleLength: gameSettings.puzzleLength,
      theme: gameSettings.theme
    }
  })
  
  ElNotification({
    title: 'Starting Game',
    message: `Creating a ${gameSettings.difficulty} difficulty puzzle...`,
    type: 'info',
    duration: 2000
  })
}
</script>

<template>
  <div class="home-view">
    <el-container>
      <el-main>
        <div class="game-container">
          <el-row justify="center">
            <el-col :xs="24" :sm="22" :md="18" :lg="16" :xl="14">
            <el-card class="welcome-card">
              <template #header>
                <div class="card-header">
                  <el-row align="middle" justify="center">
                    <el-col :span="24">
                      <h1>Lateral Thinking Puzzles</h1>
                      <p class="subtitle">Challenge your lateral thinking skills with mysterious puzzles!</p>
                    </el-col>
                  </el-row>
                </div>
              </template>
              
              <div class="card-content">
                <el-row :gutter="20" class="features">
                  <el-col :span="8">
                    <el-card shadow="hover" class="feature-card">
                      <template #header>
                        <div class="feature-header">
                          <el-icon size="24"><Puzzle /></el-icon>
                          <h3>Intriguing Puzzles</h3>
                        </div>
                      </template>
                      <p>Each puzzle presents a mysterious situation with a surprising explanation.</p>
                    </el-card>
                  </el-col>
                  
                  <el-col :span="8">
                    <el-card shadow="hover" class="feature-card">
                      <template #header>
                        <div class="feature-header">
                          <el-icon size="24"><ChatDotRound /></el-icon>
                          <h3>Ask Questions</h3>
                        </div>
                      </template>
                      <p>Ask questions to unravel the mystery behind each puzzle with yes/no answers.</p>
                    </el-card>
                  </el-col>
                  
                  <el-col :span="8">
                    <el-card shadow="hover" class="feature-card">
                      <template #header>
                        <div class="feature-header">
                          <el-icon size="24"><Star /></el-icon>
                          <h3>Earn Points</h3>
                        </div>
                      </template>
                      <p>Solve puzzles quickly to earn more points and challenge yourself.</p>
                    </el-card>
                  </el-col>
                </el-row>
                
                <el-divider>Game Settings</el-divider>
                
                <el-form :model="gameSettings" label-position="top" class="settings-form">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="Difficulty">
                        <el-select v-model="gameSettings.difficulty" placeholder="Select difficulty" class="w-100">
                          <el-option 
                            v-for="option in difficultyOptions" 
                            :key="option.value" 
                            :label="option.label" 
                            :value="option.value" 
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    
                    <el-col :span="8">
                      <el-form-item label="Puzzle Length">
                        <el-select v-model="gameSettings.puzzleLength" placeholder="Select length" class="w-100">
                          <el-option 
                            v-for="option in lengthOptions" 
                            :key="option.value" 
                            :label="option.label" 
                            :value="option.value" 
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    
                    <el-col :span="8">
                      <el-form-item label="Theme">
                        <el-select v-model="gameSettings.theme" placeholder="Select theme" class="w-100">
                          <el-option 
                            v-for="option in themeOptions" 
                            :key="option.value" 
                            :label="option.label" 
                            :value="option.value" 
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>
                
                <div class="start-section">
                  <h2>Ready to begin?</h2>
                  <el-button 
                    type="primary" 
                    size="large" 
                    :loading="isLoading"
                    @click="startGame" 
                    class="start-button"
                  >
                    {{ isLoading ? 'Creating puzzle...' : 'Start New Game' }}
                  </el-button>
                </div>
                
                <el-collapse class="rules-collapse">
                  <el-collapse-item title="How to Play" name="1">
                    <ol class="rules-list">
                      <li>You'll be presented with a mysterious situation (the "puzzle").</li>
                      <li>Ask questions that can be answered with "Yes" or "No".</li>
                      <li>Use logic and creativity to figure out what happened.</li>
                      <li>Keep asking questions until you solve the puzzle!</li>
                    </ol>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
/* 全局样式 */
.home-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.game-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 欢迎卡片样式 */
.welcome-card {
  margin-bottom: 20px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.card-header {
  text-align: center;
  margin-bottom: 10px;
  padding: 20px 0;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  color: white;
}

h1 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 0.8rem;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 0;
}

.card-content {
  padding: 20px;
}

/* 功能卡片样式 */
.features {
  margin-bottom: 40px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 12px;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.feature-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #409EFF;
}

.feature-header .el-icon {
  font-size: 24px;
  color: #67C23A;
  background-color: rgba(103, 194, 58, 0.1);
  padding: 10px;
  border-radius: 50%;
}

/* 设置表单样式 */
.settings-form {
  margin: 40px 0 30px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 12px;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.03);
}

.w-100 {
  width: 100%;
}

/* 开始按钮区域 */
.start-section {
  text-align: center;
  margin: 40px 0 30px;
}

.start-section h2 {
  margin-bottom: 25px;
  font-size: 1.8rem;
  color: #67C23A;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.start-button {
  padding: 15px 40px;
  font-size: 1.2rem;
  font-weight: 600;
  border-radius: 50px;
  box-shadow: 0 4px 15px rgba(103, 194, 58, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.start-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4);
}

/* 规则区域 */
.rules-collapse {
  margin: 30px 0;
  border-radius: 8px;
  overflow: hidden;
}

.rules-list {
  padding-left: 25px;
  margin: 15px 0;
}

.rules-list li {
  margin-bottom: 12px;
  line-height: 1.6;
  font-size: 1.05rem;
  color: #606266;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .el-col {
    margin-bottom: 15px;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .feature-card {
    margin-bottom: 15px;
  }
  
  .features {
    display: flex;
    flex-direction: column;
  }
  
  .settings-form {
    padding: 15px 10px;
  }
  
  .start-section h2 {
    font-size: 1.5rem;
  }
  
  .start-button {
    width: 100%;
    padding: 12px 20px;
  }
}

/* 横屏特殊处理 */
@media (min-width: 768px) and (max-height: 600px) {
  .welcome-card {
    margin-top: 10px;
  }
  
  .card-header {
    padding: 10px 0;
  }
  
  h1 {
    font-size: 2rem;
    margin-bottom: 0.4rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .settings-form {
    margin: 20px 0;
    padding: 10px;
  }
  
  .features {
    margin-bottom: 20px;
  }
  
  .start-section {
    margin: 20px 0;
  }
  
  .start-section h2 {
    font-size: 1.4rem;
    margin-bottom: 15px;
  }
}
</style>
