<template>
  <div class="truck-apply">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon>
          <Van />
        </el-icon>
        货车ETC申办
      </h2>
      <p class="page-desc">请填写准确的货车和个人信息，确保申办成功</p>
    </div>

    <el-card class="form-card">
      <el-form 
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="apply-form"
      >
        <!-- 个人信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><User /></el-icon>
            个人信息
          </h3>
          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-form-item label="姓名" prop="name">
                <el-input 
                  v-model="formData.name"
                  placeholder="请输入真实姓名"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item label="身份证号" prop="idCode">
                <el-input 
                  v-model="formData.idCode"
                  placeholder="请输入18位身份证号"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-form-item label="手机号" prop="phone">
                <el-input 
                  v-model="formData.phone"
                  placeholder="请输入手机号"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 产品信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Box /></el-icon>
            产品信息
          </h3>
          <el-form-item label="请选择产品">
            <el-cascader
              v-model="cascaderValue"
              :options="cascaderOptions"
              :props="cascaderProps"
              placeholder="请选择运营商和产品"
              style="width: 300px"
              @change="onCascaderChange"
              clearable
            />
          </el-form-item>
        </div>

        <!-- 银行信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><CreditCard /></el-icon>
            银行信息
          </h3>
          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-form-item label="银行卡号" prop="bankNo">
                <el-input 
                  v-model="formData.bankNo"
                  placeholder="请输入银行卡号"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item label="开户银行" prop="bankName">
                <el-select 
                  v-model="formData.bankName"
                  placeholder="请选择开户银行"
                  clearable
                  filterable
                >
                  <el-option 
                    v-for="bank in bankOptions"
                    :key="bank.value"
                    :label="bank.label"
                    :value="bank.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 车辆信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Truck /></el-icon>
            货车信息
          </h3>
          <el-row :gutter="20">
            <el-col :xs="24" :md="8">
              <el-form-item label="车牌省份" prop="plateProvince">
                <el-select 
                  v-model="formData.plateProvince"
                  placeholder="选择省份"
                  @change="onProvinceChange"
                >
                  <el-option-group label="热门省份">
                    <el-option 
                      v-for="province in hotProvinces"
                      :key="province"
                      :label="province"
                      :value="province"
                    />
                  </el-option-group>
                  <el-option-group label="全部省份">
                    <el-option 
                      v-for="province in allProvinces"
                      :key="province"
                      :label="province"
                      :value="province"
                    />
                  </el-option-group>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item label="车牌字母" prop="plateLetter">
                <el-select 
                  v-model="formData.plateLetter"
                  placeholder="选择字母"
                >
                  <el-option 
                    v-for="letter in plateLetters"
                    :key="letter"
                    :label="letter"
                    :value="letter"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item label="车牌号码" prop="plateNumber">
                <el-input 
                  v-model="formData.plateNumber"
                  placeholder="请输入车牌号码"
                  clearable
                  style="text-transform: uppercase"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-form-item label="车架号" prop="vin">
                <el-input 
                  v-model="formData.vin"
                  placeholder="请输入17位车架号"
                  clearable
                  style="text-transform: uppercase"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item label="车辆颜色" prop="vehicleColor">
                <div class="color-selection">
                  <el-select 
                    v-model="formData.vehicleColor"
                    placeholder="请选择车辆颜色"
                    style="width: 150px"
                  >
                    <el-option 
                      v-for="color in vehicleColors"
                      :key="color"
                      :label="color"
                      :value="color"
                    >
                      <div class="color-option">
                        <span 
                          class="color-preview" 
                          :style="{ backgroundColor: getColorHex(color) }"
                        ></span>
                        <span class="color-name">{{ color }}</span>
                      </div>
                    </el-option>
                  </el-select>
                  
                  <!-- 颜色按钮选择 -->
                  <div class="color-buttons">
                    <button 
                      v-for="color in vehicleColors"
                      :key="color"
                      :class="['color-btn', { active: formData.vehicleColor === color }]"
                      :style="{ backgroundColor: getColorHex(color) }"
                      @click="selectColor(color)"
                      :title="color"
                    >
                      <span v-if="formData.vehicleColor === color" class="check-icon">✓</span>
                    </button>
                  </div>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 货车规格 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Box /></el-icon>
            货车规格
          </h3>
          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-form-item label="载重量(吨)" prop="loadWeight">
                <el-input 
                  v-model="formData.loadWeight"
                  placeholder="请输入载重量"
                  clearable
                >
                  <template #append>吨</template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item label="车长(米)" prop="length">
                <el-input 
                  v-model="formData.length"
                  placeholder="请输入车长"
                  clearable
                >
                  <template #append>米</template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-form-item label="车宽(米)" prop="width">
                <el-input 
                  v-model="formData.width"
                  placeholder="请输入车宽"
                  clearable
                >
                  <template #append>米</template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item label="车高(米)" prop="height">
                <el-input 
                  v-model="formData.height"
                  placeholder="请输入车高"
                  clearable
                >
                  <template #append>米</template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :xs="24" :md="8">
              <el-form-item label="车辆类型" prop="vehicleType">
                <el-select 
                  v-model="formData.vehicleType"
                  placeholder="请选择车辆类型"
                >
                  <el-option 
                    v-for="type in vehicleTypes"
                    :key="type"
                    :label="type"
                    :value="type"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item label="轴数" prop="axleCount">
                <el-select 
                  v-model="formData.axleCount"
                  placeholder="请选择轴数"
                >
                  <el-option 
                    v-for="count in axleCounts"
                    :key="count"
                    :label="`${count}轴`"
                    :value="count"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item label="轮胎数" prop="tireCount">
                <el-select 
                  v-model="formData.tireCount"
                  placeholder="请选择轮胎数"
                >
                  <el-option 
                    v-for="count in tireCounts"
                    :key="count"
                    :label="`${count}个`"
                    :value="count"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 申办进度 -->
        <div v-if="applyStatus.isApplying || applyStatus.taskId" class="progress-section">
          <h3 class="section-title">
            <el-icon><Loading /></el-icon>
            申办进度
          </h3>
          <el-progress 
            :percentage="applyStatus.progress"
            :status="applyStatus.progress >= 100 ? 'success' : 'primary'"
            :stroke-width="8"
          />
          <p class="progress-message">{{ applyStatus.message }}</p>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button 
            type="warning" 
            size="large"
            :loading="applyStatus.isApplying"
            @click="submitApply"
          >
            <el-icon><Check /></el-icon>
            {{ applyStatus.isApplying ? '申办中...' : '提交申办' }}
          </el-button>
          
          <el-button 
            type="success" 
            size="large"
            @click="saveData"
          >
            <el-icon><Document /></el-icon>
            保存五要素
          </el-button>
          
          <el-button 
            size="large"
            @click="resetForm"
          >
            <el-icon><Refresh /></el-icon>
            重置表单
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Van, User, CreditCard, Box, Loading, Check, Document, Refresh } from '@element-plus/icons-vue'
import api from '../api'

export default {
  name: 'TruckApply',
  components: {
    Van, User, CreditCard, Box, Loading, Check, Document, Refresh
  },
  setup() {
    const store = useStore()
    const formRef = ref(null)
    
    // 表单数据
    const formData = reactive({
      name: '',
      idCode: '',
      phone: '',
      bankNo: '',
      bankName: '',
      plateProvince: '',
      plateLetter: '',
      plateNumber: '',
      vin: '',
      vehicleColor: '黄色',
      loadWeight: '',
      length: '',
      width: '',
      height: '',
      vehicleType: '',
      axleCount: '2',
      tireCount: '6'
    })

    // 车牌字母选项
    const plateLetters = ref([])

    // 银行选项
    const bankOptions = [
      { label: '中国工商银行', value: '中国工商银行' },
      { label: '中国农业银行', value: '中国农业银行' },
      { label: '中国银行', value: '中国银行' },
      { label: '中国建设银行', value: '中国建设银行' },
      { label: '交通银行', value: '交通银行' },
      { label: '招商银行', value: '招商银行' },
      { label: '浦发银行', value: '浦发银行' },
      { label: '中信银行', value: '中信银行' }
    ]

    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      idCode: [
        { required: true, message: '请输入身份证号', trigger: 'blur' },
        { pattern: /^\d{17}[\dXx]$/, message: '请输入正确的身份证号', trigger: 'blur' }
      ],
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ],
      bankNo: [
        { required: true, message: '请输入银行卡号', trigger: 'blur' }
      ],
      bankName: [
        { required: true, message: '请选择开户银行', trigger: 'change' }
      ],
      plateProvince: [
        { required: true, message: '请选择车牌省份', trigger: 'change' }
      ],
      plateLetter: [
        { required: true, message: '请选择车牌字母', trigger: 'change' }
      ],
      plateNumber: [
        { required: true, message: '请输入车牌号码', trigger: 'blur' }
      ],
      vin: [
        { required: true, message: '请输入车架号', trigger: 'blur' },
        { pattern: /^[A-Z0-9]{17}$/, message: '请输入正确的17位车架号', trigger: 'blur' }
      ],
      loadWeight: [
        { required: true, message: '请输入载重量', trigger: 'blur' }
      ],
      length: [
        { required: true, message: '请输入车长', trigger: 'blur' }
      ],
      width: [
        { required: true, message: '请输入车宽', trigger: 'blur' }
      ],
      height: [
        { required: true, message: '请输入车高', trigger: 'blur' }
      ]
    }

    // 计算属性
    const applyStatus = computed(() => store.getters.getApplyStatus)
    const defaultData = computed(() => store.getters.getDefaultData)
    const hotProvinces = computed(() => defaultData.value.hotProvinces || [])
    const allProvinces = computed(() => defaultData.value.provinces || [])
    const vehicleColors = computed(() => Object.keys(defaultData.value.vehicleColors || {}))
    const vehicleTypes = computed(() => defaultData.value.vehicle_types || ['重型货车', '中型货车', '轻型货车', '微型货车'])
    const axleCounts = computed(() => defaultData.value.axle_counts || ['2', '3', '4', '5', '6'])
    const tireCounts = computed(() => defaultData.value.tire_counts || ['4', '6', '8', '10', '12', '14', '16', '18', '20', '22'])
    
    // 颜色映射 - 按照实际车牌颜色标准
    const colorMap = {
      '蓝色': '#4A90E2',  // 蓝色车牌（普通小型车）
      '黄色': '#F5D62D',  // 黄色车牌（大型车、货车、教练车等）
      '绿色': '#7ED321',  // 绿色车牌（新能源车）
      '白色': '#FFFFFF',  // 白色车牌（军车、警车等）
      '黑色': '#2C2C2C'   // 黑色车牌（港澳车、领事馆车等）
    }

    // 方法
    const loadProvinces = async () => {
      try {
        await store.dispatch('loadProvinces')
      } catch (error) {
        console.error('加载省份失败:', error)
      }
    }

    const loadDefaultData = async () => {
      try {
        await store.dispatch('loadDefaultData', 'truck')
        // 设置默认值
        if (defaultData.value.default_province) {
          formData.plateProvince = defaultData.value.default_province
          onProvinceChange(defaultData.value.default_province)
        }
        if (defaultData.value.default_letter) {
          formData.plateLetter = defaultData.value.default_letter
        }
      } catch (error) {
        console.error('加载默认数据失败:', error)
      }
    }

    const onProvinceChange = async (province) => {
      if (province) {
        try {
          const response = await api.getPlateLetters(province)
          if (response.data.success) {
            plateLetters.value = response.data.data
          }
        } catch (error) {
          console.error('获取车牌字母失败:', error)
        }
      }
    }
    
    // 颜色选择相关方法
    const getColorHex = (colorName) => {
      return colorMap[colorName] || '#CCCCCC'
    }
    
    const selectColor = (color) => {
      formData.vehicleColor = color
    }

    const submitApply = async () => {
      try {
        const valid = await formRef.value.validate()
        if (!valid) return

        // 更新store中的表单数据
        store.commit('UPDATE_FORM_DATA', { type: 'truck', data: formData })
        
        const result = await store.dispatch('applyTruck')
        
        if (result.success) {
          ElMessage.success(result.message || '申办提交成功')
        } else {
          ElMessage.error(result.message || '申办提交失败')
        }
      } catch (error) {
        ElMessage.error('申办提交失败，请稍后重试')
      }
    }

    const saveData = async () => {
      try {
        // 更新store中的表单数据
        store.commit('UPDATE_FORM_DATA', { type: 'truck', data: formData })
        
        const result = await store.dispatch('saveData', 'truck')
        
        if (result.success) {
          ElMessage.success(result.message || '数据保存成功')
        } else {
          ElMessage.error(result.message || '数据保存失败')
        }
      } catch (error) {
        ElMessage.error('数据保存失败，请稍后重试')
      }
    }

    const resetForm = () => {
      ElMessageBox.confirm(
        '确定要重置表单吗？这将清空所有已填写的数据。',
        '确认重置',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        formRef.value.resetFields()
        store.commit('RESET_FORM_DATA', 'truck')
        ElMessage.success('表单已重置')
      }).catch(() => {
        // 用户取消
      })
    }

    // 生命周期
    onMounted(() => {
      loadProvinces()
      loadDefaultData()
    })

    return {
      formRef,
      formData,
      rules,
      plateLetters,
      bankOptions,
      applyStatus,
      hotProvinces,
      allProvinces,
      vehicleColors,
      vehicleTypes,
      axleCounts,
      tireCounts,
      onProvinceChange,
      getColorHex,
      selectColor,
      submitApply,
      saveData,
      resetForm
    }
  }
}
</script>

<style scoped>
.truck-apply {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 10px;
}

.page-desc {
  color: #606266;
  font-size: 16px;
  margin: 0;
}

.form-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #E6A23C;
}

.progress-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fff7e6;
  border-radius: 8px;
  border-left: 4px solid #E6A23C;
}

.progress-message {
  text-align: center;
  margin: 15px 0 0;
  color: #606266;
  font-size: 14px;
}

.form-actions {
  text-align: center;
  padding: 30px 0;
  border-top: 1px solid #EBEEF5;
}

.form-actions .el-button {
  margin: 0 10px;
  min-width: 120px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .form-section {
    padding: 15px;
  }
  
  .form-actions .el-button {
  margin: 5px;
  width: 100%;
  max-width: 200px;
}

/* 颜色选择样式 */
.color-selection {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.color-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-preview {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #ddd;
  display: inline-block;
}

.color-name {
  font-size: 14px;
}

.color-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #ddd;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
}

.color-btn:hover {
  border-color: #409EFF;
  transform: scale(1.1);
}

.color-btn.active {
  border-color: #409EFF;
  border-width: 3px;
  transform: scale(1.1);
}

.color-btn .check-icon {
  color: white;
  font-weight: bold;
  font-size: 14px;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.5);
}

/* 白色按钮的特殊处理 */
.color-btn[style*="rgb(255, 255, 255)"] .check-icon,
.color-btn[style*="#FFFFFF"] .check-icon {
  color: #333;
  text-shadow: none;
}
}
</style> 