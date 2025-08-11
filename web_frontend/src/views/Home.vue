<template>
  <div class="home">
    <div class="welcome-section">
      <el-card class="welcome-card">
        <div class="welcome-content">
          <div class="welcome-icon">
            <el-icon size="60" color="#409EFF">
                              <Van />
            </el-icon>
          </div>
          <h2 class="welcome-title">欢迎使用ETC申办系统</h2>
          <p class="welcome-desc">
            快速便捷的ETC申办服务，支持客车和货车两种车型的在线申办
          </p>
        </div>
      </el-card>
    </div>

    <div class="service-section">
      <h3 class="section-title">选择申办类型</h3>
      <el-row :gutter="30" class="service-cards">
        <!-- 客车申办 -->
        <el-col :xs="24" :sm="12" :md="12" class="service-col">
          <el-card 
            class="service-card passenger-card" 
            shadow="hover"
            @click="navigateTo('/passenger')"
          >
            <div class="service-icon">
              <el-icon size="48" color="#67C23A">
                <Van />
              </el-icon>
            </div>
            <h4 class="service-title">客车申办</h4>
            <p class="service-desc">
              适用于私家车、轿车等客运车辆的ETC申办服务
            </p>
            <div class="service-features">
              <el-tag size="small" type="success">快速申办</el-tag>
              <el-tag size="small" type="info">在线办理</el-tag>
              <el-tag size="small" type="warning">实时进度</el-tag>
            </div>
            <div class="service-action">
              <el-button type="primary" size="large" round>
                立即申办
                <el-icon class="el-icon--right">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
          </el-card>
        </el-col>

        <!-- 货车申办 -->
        <el-col :xs="24" :sm="12" :md="12" class="service-col">
          <el-card 
            class="service-card truck-card" 
            shadow="hover"
            @click="navigateTo('/truck')"
          >
            <div class="service-icon">
              <el-icon size="48" color="#E6A23C">
                <Van />
              </el-icon>
            </div>
            <h4 class="service-title">货车申办</h4>
            <p class="service-desc">
              适用于货车、卡车等货运车辆的ETC申办服务
            </p>
            <div class="service-features">
              <el-tag size="small" type="success">专业服务</el-tag>
              <el-tag size="small" type="info">多种套餐</el-tag>
              <el-tag size="small" type="warning">便捷高效</el-tag>
            </div>
            <div class="service-action">
              <el-button type="warning" size="large" round>
                立即申办
                <el-icon class="el-icon--right">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="features-section">
      <h3 class="section-title">服务特色</h3>
      <el-row :gutter="20" class="features-grid">
        <el-col :xs="24" :sm="8" :md="8">
          <div class="feature-item">
            <el-icon size="32" color="#409EFF">
              <Clock />
            </el-icon>
            <h5>7x24小时服务</h5>
            <p>全天候在线申办服务，随时随地提交申请</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8" :md="8">
          <div class="feature-item">
            <el-icon size="32" color="#67C23A">
                              <Lightning />
            </el-icon>
            <h5>安全可靠</h5>
            <p>采用银行级加密技术，保障您的个人信息安全</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8" :md="8">
          <div class="feature-item">
            <el-icon size="32" color="#E6A23C">
              <Lightning />
            </el-icon>
            <h5>快速办理</h5>
            <p>智能化流程，最快当天完成ETC设备申办</p>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { Van, ArrowRight, Clock, Lightning } from '@element-plus/icons-vue'

export default {
  name: 'Home',
  components: {
    Van, 
    ArrowRight,
    Clock,
    Lightning
  },
  methods: {
    navigateTo(path) {
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 欢迎区域 */
.welcome-section {
  margin-bottom: 40px;
}

.welcome-card {
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border: none;
}

.welcome-content {
  padding: 40px 20px;
}

.welcome-icon {
  margin-bottom: 20px;
}

.welcome-title {
  color: #303133;
  margin: 20px 0 15px;
  font-size: 28px;
  font-weight: 600;
}

.welcome-desc {
  color: #606266;
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
}

/* 服务选择区域 */
.service-section {
  margin-bottom: 50px;
}

.section-title {
  text-align: center;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 30px;
}

.service-cards {
  display: flex;
  justify-content: center;
}

.service-col {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.service-card {
  width: 100%;
  max-width: 400px;
  text-align: center;
  padding: 30px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.passenger-card:hover {
  border-color: #67C23A;
}

.truck-card:hover {
  border-color: #E6A23C;
}

.service-icon {
  margin-bottom: 20px;
}

.service-title {
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  margin: 15px 0;
}

.service-desc {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
}

.service-features {
  margin-bottom: 25px;
}

.service-features .el-tag {
  margin: 0 5px 8px;
}

.service-action {
  padding-top: 10px;
}

/* 特色功能区域 */
.features-section {
  margin-bottom: 40px;
}

.features-grid {
  display: flex;
  justify-content: center;
}

.feature-item {
  text-align: center;
  padding: 30px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.feature-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.feature-item h5 {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  margin: 15px 0 10px;
}

.feature-item p {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-desc {
    font-size: 14px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .service-card {
    padding: 25px 15px;
  }
  
  .feature-item {
    padding: 25px 15px;
  }
}
</style> 