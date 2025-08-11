<template>
  <div class="passenger-apply">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon>
          <Van />
        </el-icon>
        客车ETC申办
      </h2>
      <p class="page-desc">请填写准确的车辆和个人信息，确保申办成功</p>
    </div>

    <el-card class="form-card">
      <el-form 
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="apply-form"
      >
        <!-- 产品信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Box /></el-icon>
            产品信息
          </h3>
          <el-form-item label="请选择产品" prop="productId">
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

        <!-- 车辆信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><Van /></el-icon>
            车辆信息
          </h3>
                        <el-form-item label="车牌省份" prop="plateProvince">
            <el-input 
              v-model="formData.plateProvince"
              placeholder="请输入车牌省份前缀（如：粤、京、沪）"
              style="width: 300px"
              @input="onProvinceInput"
              @blur="validateProvince"
            />
            <el-button 
              @click="showProvinceDialog"
              style="margin-left: 10px"
            >
              选择省份
            </el-button>
          </el-form-item>
          
          <el-form-item label="车牌字母" prop="plateLetter">
            <el-input 
              v-model="formData.plateLetter"
              placeholder="请输入车牌字母"
              style="width: 300px"
              @input="onLetterInput"
              @blur="validateLetter"
              :disabled="!formData.plateProvince"
            />
            <el-button 
              @click="showLetterDialog"
              style="margin-left: 10px"
              :disabled="!formData.plateProvince"
            >
              选择字母
            </el-button>
          </el-form-item>
          
              <el-form-item label="车牌号码" prop="plateNumber">
                <el-input 
                  v-model="formData.plateNumber"
                  placeholder="请输入车牌号码"
                  clearable
              style="text-transform: uppercase; width: 300px"
            />
            <el-button 
              @click="generateRandomPlate"
              style="margin-left: 10px"
            >
              随机
            </el-button>
              </el-form-item>

              <el-form-item label="车辆颜色" prop="vehicleColor">
                <div class="color-selection">
                  <el-select 
                    v-model="formData.vehicleColor"
                    placeholder="请选择车辆颜色"
                    style="width: 200px"
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

          <el-form-item label="VIN码" prop="vin">
            <el-input 
              v-model="formData.vin"
              placeholder="请输入17位VIN码"
              clearable
              style="text-transform: uppercase; width: 300px"
              @blur="validateVin"
            />
            <el-button 
              @click="autoFetchVin"
              style="margin-left: 10px"
            >
              自动获取VIN
            </el-button>
          </el-form-item>
        </div>

        <!-- 五要素信息 (支持拖拽文件自动填充) -->
        <div class="form-section">
          <h3 class="section-title">
            <el-icon><User /></el-icon>
            五要素信息 (支持拖拽文件自动填充)
          </h3>
          <el-form-item label="姓名" prop="name">
            <el-input 
              v-model="formData.name"
              placeholder="请输入真实姓名"
              clearable
              style="width: 300px"
            />
          </el-form-item>
          
          <el-form-item label="身份证" prop="idCode">
            <el-input 
              v-model="formData.idCode"
              placeholder="请输入18位身份证号"
              clearable
              @blur="validateIdCode"
              style="width: 300px"
            />
          </el-form-item>
          
          <el-form-item label="手机号" prop="phone">
            <el-input 
              v-model="formData.phone"
              placeholder="请输入手机号"
              clearable
              @blur="validatePhone"
              style="width: 300px"
            />
          </el-form-item>

          <el-form-item label="银行卡号" prop="bankNo">
            <el-input 
              v-model="formData.bankNo"
              placeholder="请输入银行卡号"
              clearable
              @blur="validateBankCard"
              style="width: 300px"
            />
          </el-form-item>
          
          <el-form-item label="银行名称" prop="bankName">
            <el-input 
              v-model="formData.bankName"
              placeholder="请输入银行名称"
              clearable
              style="width: 300px"
            />
          </el-form-item>

          <el-button 
            type="success"
            @click="saveData"
          >
            保存五要素
          </el-button>
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
            type="primary" 
            size="large"
            :loading="applyStatus.isApplying"
            @click="submitApply"
          >
            <el-icon><Check /></el-icon>
            {{ applyStatus.isApplying ? '申办中...' : '提交申办' }}
          </el-button>
          
          <el-button 
            type="warning" 
            size="large"
            @click="showVerifyCodeDialog"
          >
            <el-icon><Key /></el-icon>
            验证码确认
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
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Van, User, CreditCard, Box, Loading, Check, Document, Refresh, Key } from '@element-plus/icons-vue'
import api from '../api'
import ProvinceMap from '../components/ProvinceMap.vue'

export default {
  name: 'PassengerApply',
  components: {
    Van, User, CreditCard, Box, Loading, Check, Document, Refresh, Key,
    ProvinceMap
  },
  setup() {
    const store = useStore()
    const formRef = ref(null)
    
    // 省份前缀到全名的映射
    const provinceCodeToName = {
      '京': '北京市', '津': '天津市', '沪': '上海市', '渝': '重庆市',
      '冀': '河北省', '晋': '山西省', '蒙': '内蒙古自治区', '辽': '辽宁省',
      '吉': '吉林省', '黑': '黑龙江省', '苏': '江苏省', '浙': '浙江省',
      '皖': '安徽省', '闽': '福建省', '赣': '江西省', '鲁': '山东省',
      '豫': '河南省', '鄂': '湖北省', '湘': '湖南省', '粤': '广东省',
      '桂': '广西壮族自治区', '琼': '海南省', '川': '四川省', '贵': '贵州省',
      '云': '云南省', '藏': '西藏自治区', '陕': '陕西省', '甘': '甘肃省',
      '青': '青海省', '宁': '宁夏回族自治区', '新': '新疆维吾尔自治区',
      '港': '香港特别行政区', '澳': '澳门特别行政区', '台': '台湾省',
      '使': '使馆', '领': '领馆'
    }
    
    // 表单数据
    const formData = reactive({
      name: '',
      idCode: '',
      phone: '',
      verifyCode: '',
      bankNo: '',
      bankName: '',
      operatorCode: 'TXB', // 默认运营商
      productId: '',
      plateProvince: '',
      plateLetter: '',
      plateNumber: '',
      vin: '',
      vehicleColor: ''
    })
    
    // 选中的产品显示
    const selectedProductDisplay = ref('')

    // 验证码倒计时
    const verifyCodeCooldown = ref(0)

    // 车牌字母选项
    const plateLetters = ref([])
    
    // 运营商选项
    const operatorOptions = ref([])
    
    // 产品选项
    const allProducts = ref([])
    const filteredProducts = ref([])
    
    // 级联选择器相关
    const cascaderValue = ref([])
    const cascaderOptions = ref([])
    const cascaderProps = {
      value: 'value',
      label: 'label',
      children: 'children'
    }

    // 银行选项
    const bankOptions = [
      { label: '中国工商银行', value: '中国工商银行' },
      { label: '中国农业银行', value: '中国农业银行' },
      { label: '中国银行', value: '中国银行' },
      { label: '中国建设银行', value: '中国建设银行' },
      { label: '交通银行', value: '交通银行' },
      { label: '招商银行', value: '招商银行' },
      { label: '浦发银行', value: '浦发银行' },
      { label: '中信银行', value: '中信银行' },
      { label: '中国光大银行', value: '中国光大银行' },
      { label: '华夏银行', value: '华夏银行' }
    ]

    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' },
        { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
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
        { required: true, message: '请输入银行卡号', trigger: 'blur' },
        { pattern: /^\d{13,19}$/, message: '请输入正确的银行卡号', trigger: 'blur' }
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
        { required: true, message: '请输入车牌号码', trigger: 'blur' },
        { min: 5, max: 5, message: '车牌号码必须是5位', trigger: 'blur' }
      ],
      vin: [
        { required: true, message: '请输入车架号', trigger: 'blur' },
        { pattern: /^[A-Z0-9]{17}$/, message: '请输入正确的17位车架号', trigger: 'blur' }
      ],
      vehicleColor: [
        { required: true, message: '请选择车辆颜色', trigger: 'change' }
      ],
      productId: [
        { required: true, message: '请选择产品', trigger: 'change' }
      ]
    }

    // 计算属性
    const applyStatus = computed(() => store.getters.getApplyStatus)
    const defaultData = computed(() => store.getters.getDefaultData)
    const hotProvinces = computed(() => defaultData.value.hotProvinces || [])
    const allProvinces = computed(() => defaultData.value.provinces || [])
    const vehicleColors = computed(() => Object.keys(defaultData.value.vehicleColors || {}))
    
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
        await store.dispatch('loadDefaultData', 'passenger')
        // 设置默认值
        if (defaultData.value.default_province) {
          formData.plateProvince = defaultData.value.default_province
          onProvinceChange(defaultData.value.default_province)
        }
        if (defaultData.value.default_letter) {
          formData.plateLetter = defaultData.value.default_letter
        }
        if (defaultData.value.default_plate_number) {
          formData.plateNumber = defaultData.value.default_plate_number
        }
        if (defaultData.value.default_vehicle_color) {
          formData.vehicleColor = defaultData.value.default_vehicle_color
        }
      } catch (error) {
        console.error('加载默认数据失败:', error)
      }
    }

    // 省份输入处理
    const onProvinceInput = async (value) => {
      // 自动转换为大写
      formData.plateProvince = value.toUpperCase()
      // 清空字母，因为省份改变了
      formData.plateLetter = ''
      plateLetters.value = []
      
      // 如果输入了有效的省份，自动加载对应的字母
      if (formData.plateProvince.length === 1) {
        const provincePattern = /^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼港澳台使领]$/
        if (provincePattern.test(formData.plateProvince)) {
          await onProvinceChange(formData.plateProvince)
        }
      }
    }
    
    // 省份验证
    const validateProvince = async () => {
      if (formData.plateProvince) {
        // 验证省份格式
        const provincePattern = /^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼港澳台使领]$/
        if (!provincePattern.test(formData.plateProvince)) {
          ElMessage.warning('请输入正确的车牌省份前缀')
          return
        }
        
        // 获取对应的车牌字母
        await onProvinceChange(formData.plateProvince)
      }
    }
    
    // 字母输入处理
    const onLetterInput = (value) => {
      // 自动转换为大写
      formData.plateLetter = value.toUpperCase()
    }
    
    // 字母验证
    const validateLetter = () => {
      if (formData.plateLetter) {
        const letterPattern = /^[A-Z]$/
        if (!letterPattern.test(formData.plateLetter)) {
          ElMessage.warning('请输入正确的车牌字母（A-Z）')
          return
        }
        
        // 检查字母是否在可用列表中
        if (plateLetters.value.length > 0 && !plateLetters.value.includes(formData.plateLetter)) {
          ElMessage.warning(`该省份不支持字母 ${formData.plateLetter}，请选择其他字母`)
        }
      }
    }
    
    const onProvinceChange = async (province) => {
      if (province) {
        try {
          console.log(`正在获取省份 ${province} 的车牌字母...`)
          const response = await api.getPlateLetters(province)
          if (response.data.success) {
            plateLetters.value = response.data.data
            console.log(`${province} 省可用字母:`, plateLetters.value)
            
            // 如果当前选择的字母不在新的字母列表中，清空字母选择
            if (formData.plateLetter && !plateLetters.value.includes(formData.plateLetter)) {
              formData.plateLetter = ''
              console.log('当前字母不在新省份的可用字母中，已清空')
            }
          } else {
            console.error('获取车牌字母失败:', response.data.message)
            plateLetters.value = []
          }
        } catch (error) {
          console.error('获取车牌字母失败:', error)
          plateLetters.value = []
          ElMessage.error('获取车牌字母失败，请稍后重试')
        }
      } else {
        plateLetters.value = []
      }
    }

    const validateIdCode = async () => {
      if (formData.idCode) {
        try {
          await api.validateField('id_code', formData.idCode)
        } catch (error) {
          console.error('身份证验证失败:', error)
        }
      }
    }

    const validatePhone = async () => {
      if (formData.phone) {
        try {
          await api.validateField('phone', formData.phone)
        } catch (error) {
          console.error('手机号验证失败:', error)
        }
      }
    }

    const validateBankCard = async () => {
      if (formData.bankNo) {
        try {
          await api.validateField('bank_card', formData.bankNo)
        } catch (error) {
          console.error('银行卡验证失败:', error)
        }
      }
    }

    const validateVin = async () => {
      if (formData.vin) {
        try {
          await api.validateField('vin', formData.vin.toUpperCase())
          formData.vin = formData.vin.toUpperCase()
        } catch (error) {
          console.error('车架号验证失败:', error)
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

    // 运营商变化处理
    const onOperatorChange = (operatorCode) => {
      formData.productId = '' // 清空产品选择
      loadProductsByOperator(operatorCode)
    }
    
    // 根据运营商加载产品
    const loadProductsByOperator = async (operatorCode) => {
      try {
        const response = await api.getProducts(operatorCode)
        if (response.data.success) {
          filteredProducts.value = response.data.data || []
          
          // 如果只有一个产品，自动选择
          if (filteredProducts.value.length === 1) {
            formData.productId = filteredProducts.value[0].id
            selectedProductDisplay.value = filteredProducts.value[0].name
          }
        } else {
          ElMessage.error(response.data.message || '获取产品列表失败')
        }
      } catch (error) {
        ElMessage.error('加载产品列表失败')
        console.error('加载产品列表失败:', error)
      }
    }
    
    // 加载运营商列表并构建级联选择器数据
    const loadOperators = async () => {
      try {
        // 客车页面传递车辆类型为 '0'
        const response = await api.getOperators('0')
        if (response.data.success) {
          operatorOptions.value = response.data.data || []
          console.log('客车运营商列表:', operatorOptions.value)
          await buildCascaderOptions()
        } else {
          ElMessage.error('获取运营商列表失败')
        }
      } catch (error) {
        console.error('获取运营商列表失败:', error)
        ElMessage.error('获取运营商列表失败')
      }
    }
    
    // 构建级联选择器选项
    const buildCascaderOptions = async () => {
      const options = []
      
      for (const operator of operatorOptions.value) {
        try {
          // 获取该运营商的产品列表 (车辆类型: 0=客车)
          const response = await api.getProducts(operator.code, '0')
          if (response.data.success) {
            const products = response.data.data || []
            const children = products.map(product => ({
              value: product.id,
              label: product.name,
              operatorCode: operator.code
            }))
            
            if (children.length > 0) {
              options.push({
                value: operator.code,
                label: operator.name,
                children: children
              })
            }
          }
        } catch (error) {
          console.warn(`获取运营商 ${operator.name} 的产品失败:`, error)
        }
      }
      
      cascaderOptions.value = options
      
      // 尝试恢复用户上次的选择
      await nextTick()
      restoreLastSelection()
    }
    
    // 恢复上次选择
    const restoreLastSelection = () => {
      const lastOp = lastSelection.value.operatorCode
      const lastProd = lastSelection.value.productId
      
      if (lastOp && lastProd && cascaderOptions.value.length > 0) {
        // 查找上次选择的运营商和产品是否还存在
        const operator = cascaderOptions.value.find(op => op.value === lastOp)
        if (operator) {
          const product = operator.children.find(prod => prod.value === lastProd)
          if (product) {
            cascaderValue.value = [lastOp, lastProd]
            formData.operatorCode = lastOp
            formData.productId = lastProd
            selectedProductDisplay.value = lastSelection.value.productName
            console.log(`恢复上次选择: ${lastSelection.value.productName}`)
            return
          }
        }
      }
      
      // 如果没有上次选择或上次选择不存在，使用默认逻辑
      setDefaultSelection()
    }
    
    // 设置默认选择
    const setDefaultSelection = () => {
      if (cascaderOptions.value.length === 0) return
      
      // 优先选择TXB运营商
      let targetOperator = cascaderOptions.value.find(op => op.value === 'TXB')
      if (!targetOperator) {
        targetOperator = cascaderOptions.value[0] // 如果没有TXB，选择第一个
      }
      
      if (targetOperator && targetOperator.children.length > 0) {
        let selectedProduct = null
        
        // 如果是TXB运营商，优先选择包含"江苏会员"的产品
        if (targetOperator.value === 'TXB') {
          selectedProduct = targetOperator.children.find(prod => 
            prod.label.includes('江苏会员')
          )
        }
        
        // 如果没找到特定产品，选择第一个
        if (!selectedProduct) {
          selectedProduct = targetOperator.children[0]
        }
        
        cascaderValue.value = [targetOperator.value, selectedProduct.value]
        formData.operatorCode = targetOperator.value
        formData.productId = selectedProduct.value
        selectedProductDisplay.value = selectedProduct.label
        
        console.log(`默认选择产品: ${selectedProduct.label}`)
      }
    }
    
    // 产品选择记忆功能
    const lastSelection = ref({
      operatorCode: localStorage.getItem('lastOperatorCode') || 'TXB',
      productId: localStorage.getItem('lastProductId') || '',
      productName: localStorage.getItem('lastProductName') || ''
    })
    
    // 级联选择器变化处理
    const onCascaderChange = (value) => {
      if (value && value.length === 2) {
        const [operatorCode, productId] = value
        formData.operatorCode = operatorCode
        formData.productId = productId
        
        // 找到选中的产品名称
        const operator = cascaderOptions.value.find(op => op.value === operatorCode)
        if (operator) {
          const product = operator.children.find(prod => prod.value === productId)
          if (product) {
            selectedProductDisplay.value = product.label
            
            // 保存用户选择到localStorage
            lastSelection.value = {
              operatorCode: operatorCode,
              productId: productId,
              productName: product.label
            }
            localStorage.setItem('lastOperatorCode', operatorCode)
            localStorage.setItem('lastProductId', productId)
            localStorage.setItem('lastProductName', product.label)
            
            ElMessage.success(`已选择产品：${product.label}`)
          }
        }
      } else {
        formData.operatorCode = ''
        formData.productId = ''
        selectedProductDisplay.value = ''
      }
    }
    
    // 显示产品选择对话框
    const showProductDialog = async () => {
      try {
        // 确保运营商列表已加载
        if (operatorOptions.value.length === 0) {
          await loadOperators()
        }
        
        if (operatorOptions.value.length === 0) {
          ElMessage.error('无可用运营商')
          return
        }
        
        // 第一步：选择运营商
        let operatorText = '请选择运营商：\n'
        operatorOptions.value.forEach((operator, index) => {
          operatorText += `${index + 1}. ${operator.name}\n`
        })
        
        const { value: operatorIndex } = await ElMessageBox.prompt(
          operatorText,
          '运营商选择',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            inputPattern: /^[1-9]\d*$/,
            inputErrorMessage: '请输入有效的数字'
          }
        )
        
        const opIndex = parseInt(operatorIndex) - 1
        if (opIndex < 0 || opIndex >= operatorOptions.value.length) {
          ElMessage.error('选择的运营商序号无效')
          return
        }
        
        const selectedOperator = operatorOptions.value[opIndex]
        formData.operatorCode = selectedOperator.code
        await loadProductsByOperator(selectedOperator.code)
        
        if (filteredProducts.value.length > 0) {
          // 第二步：选择产品
          let productOptions = '请选择产品：\n'
          filteredProducts.value.forEach((product, index) => {
            productOptions += `${index + 1}. ${product.name}\n`
          })
          
          const { value: productIndex } = await ElMessageBox.prompt(
            productOptions,
            '产品选择',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              inputPattern: /^[1-9]\d*$/,
              inputErrorMessage: '请输入有效的数字'
            }
          )
          
          const index = parseInt(productIndex) - 1
          if (index >= 0 && index < filteredProducts.value.length) {
            const selectedProduct = filteredProducts.value[index]
            formData.productId = selectedProduct.id
            selectedProductDisplay.value = selectedProduct.name
            ElMessage.success(`已选择产品：${selectedProduct.name}`)
          } else {
            ElMessage.error('选择的产品序号无效')
          }
        } else {
          ElMessage.warning('该运营商暂无可用产品')
        }
        
      } catch (error) {
        // 用户取消或其他错误
        console.log('用户取消选择')
      }
    }
    
    // 显示省份选择对话框
    const showProvinceDialog = async () => {
      try {
        const { h } = await import('vue')
        
        await ElMessageBox({
          title: '选择省份',
          message: h('div', { 
            style: 'width: 100%; min-height: 700px; padding: 10px; box-sizing: border-box; display: flex; flex-direction: column;' 
          }, [
            h(ProvinceMap, {
              modelValue: formData.plateProvince,
              onSelect: ({ code, name }) => {
                formData.plateProvince = code
                onProvinceChange(code)
                ElMessageBox.close()
                ElMessage.success(`已选择车牌省份前缀：${code} (${name})`)
              },
              style: 'flex: 1; width: 100%;'
            })
          ]),
          showCancelButton: false,
          showConfirmButton: false,
          closeOnClickModal: true,
          customStyle: {
            width: '1100px',
            maxWidth: '95vw',
            minWidth: '1050px'
          }
        })
        
      } catch (error) {
        // 用户取消
        console.log('用户取消选择省份')
      }
    }
    
    // 显示字母选择对话框
    const showLetterDialog = async () => {
      if (!formData.plateProvince) {
        ElMessage.warning('请先输入车牌省份')
        return
      }
      
      // 确保有可用的字母列表
      if (plateLetters.value.length === 0) {
        await onProvinceChange(formData.plateProvince)
      }
      
      if (plateLetters.value.length === 0) {
        ElMessage.warning('该省份暂无可用字母')
        return
      }
      
      try {
        const { h } = await import('vue')
        
        // 构建字母网格布局 (优化为5列，减少右侧空旷)
        const letterGrid = h('div', { 
          style: 'display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; padding: 20px; max-width: 400px; margin: 0 auto;' 
        }, plateLetters.value.map(letter => 
          h('button', {
            style: `
              padding: 15px; 
              border: 2px solid ${formData.plateLetter === letter ? '#1890ff' : '#d9d9d9'}; 
              background: ${formData.plateLetter === letter ? '#1890ff' : '#fff'};
              color: ${formData.plateLetter === letter ? '#fff' : '#333'};
              border-radius: 8px; 
              cursor: pointer; 
              font-size: 18px; 
              font-weight: bold;
              transition: all 0.3s ease;
              min-height: 50px;
              display: flex;
              align-items: center;
              justify-content: center;
            `,
            onClick: () => {
              formData.plateLetter = letter
              ElMessageBox.close()
              ElMessage.success(`已选择字母：${letter}`)
            },
            onMouseenter: (e) => {
              if (formData.plateLetter !== letter) {
                e.target.style.borderColor = '#40a9ff'
                e.target.style.background = '#f0f8ff'
              }
            },
            onMouseleave: (e) => {
              if (formData.plateLetter !== letter) {
                e.target.style.borderColor = '#d9d9d9'
                e.target.style.background = '#fff'
              }
            }
          }, letter)
        ))
        
        await ElMessageBox({
          title: '选择车牌字母',
          message: h('div', { style: 'width: 100%;' }, [
            h('p', { style: 'margin: 0 0 15px 0; text-align: center; color: #666;' }, 
              `${provinceCodeToName[formData.plateProvince] || formData.plateProvince}可用车牌字母（共${plateLetters.value.length}个）：`),
            letterGrid
          ]),
          showCancelButton: false,
          showConfirmButton: false,
          closeOnClickModal: true,
          customStyle: {
            width: '460px',
            maxWidth: '90vw'
          }
        })
        
      } catch (error) {
        // 用户取消
        console.log('用户取消选择字母')
      }
    }
    
    // 生成随机车牌号
    const generateRandomPlate = () => {
      const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      let result = ''
      for (let i = 0; i < 5; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      formData.plateNumber = result
      ElMessage.success('已生成随机车牌号')
    }
    
    // 自动获取VIN码
    const autoFetchVin = () => {
      // 生成随机17位VIN码
      const chars = '0123456789ABCDEFGHJKLMNPRSTUVWXYZ'
      let result = ''
      for (let i = 0; i < 17; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      formData.vin = result
      ElMessage.success('已自动获取VIN码')
    }
    
    // 显示验证码弹窗
    const showVerifyCodeDialog = () => {
      // 检查是否已经启动了申办流程
      if (!applyStatus.value.taskId) {
        ElMessage.warning('请先提交申办，获取验证码')
        return
      }
      
      // 检查是否在等待验证码状态
      if (applyStatus.value.status !== 'waiting_verify') {
        ElMessage.warning('当前状态不需要验证码确认')
        return
      }

      ElMessageBox.prompt('请输入验证码', '验证码确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入6位验证码',
        beforeClose: async (action, instance, done) => {
          if (action === 'confirm') {
            if (!instance.inputValue) {
              ElMessage.warning('请输入验证码')
              return
            }
            
            try {
              const result = await store.dispatch('confirmVerifyCode', instance.inputValue)
              
              if (result.success) {
                ElMessage.success('验证码确认成功，申办完成')
                done()
              } else {
                ElMessage.error(result.message || '验证码确认失败')
              }
            } catch (error) {
              ElMessage.error('验证码确认失败，请稍后重试')
            }
          } else {
            done()
          }
        }
      }).catch(() => {
        // 用户取消
      })
    }

    const startCooldown = () => {
      verifyCodeCooldown.value = 60
      const timer = setInterval(() => {
        verifyCodeCooldown.value--
        if (verifyCodeCooldown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    }

    const submitApply = async () => {
      try {
        const valid = await formRef.value.validate()
        if (!valid) return

        // 更新store中的表单数据
        store.commit('UPDATE_FORM_DATA', { type: 'passenger', data: formData })
        
        const result = await store.dispatch('applyETC')
        
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
        store.commit('UPDATE_FORM_DATA', { type: 'passenger', data: formData })
        
        const result = await store.dispatch('saveData', 'passenger')
        
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
        store.commit('RESET_FORM_DATA', 'passenger')
        ElMessage.success('表单已重置')
      }).catch(() => {
        // 用户取消
      })
    }

    // 生命周期
    onMounted(() => {
      loadProvinces()
      loadDefaultData()
      loadOperators()
    })

    return {
      formRef,
      formData,
      rules,
      verifyCodeCooldown,
      plateLetters,
      bankOptions,
      operatorOptions,
      filteredProducts,
      
      // 级联选择器
      cascaderValue,
      cascaderOptions,
      cascaderProps,
      onCascaderChange,
      selectedProductDisplay,
      applyStatus,
      hotProvinces,
      allProvinces,
      vehicleColors,
      onProvinceChange,
      onOperatorChange,
      onProvinceInput,
      validateProvince,
      onLetterInput,
      validateLetter,
      loadOperators,
      showProductDialog,
      showProvinceDialog,
      showLetterDialog,
      generateRandomPlate,
      autoFetchVin,
      validateIdCode,
      validatePhone,
      validateBankCard,
      validateVin,
      getColorHex,
      selectColor,
      showVerifyCodeDialog,
      submitApply,
      saveData,
      resetForm
    }
  }
}
</script>

<style scoped>
.passenger-apply {
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
  border-bottom: 2px solid #409EFF;
}

.progress-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
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

.product-selection {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.selected-product {
  margin-top: 10px;
  padding: 8px 0;
}

.selected-product .el-tag {
  font-size: 14px;
  padding: 8px 16px;
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