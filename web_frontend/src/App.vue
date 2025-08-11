<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 头部 -->
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">ETC申办系统</h1>
          <div class="header-nav">
            <el-button 
              v-if="$route.name !== 'Home'" 
              type="primary" 
              @click="$router.push('/')"
              icon="House"
            >
              返回首页
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主体内容 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <p>&copy; 2024 ETC申办系统 - Web版本</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  height: 100vh;
  margin: 0;
  padding: 0;
}

.app-container {
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.app-footer {
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  color: #6c757d;
  font-size: 14px;
}

.footer-content p {
  margin: 0;
}

/* 全局样式重置 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-title {
    font-size: 20px;
  }
  
  .app-main {
    padding: 15px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 10px;
  }
}
</style> 