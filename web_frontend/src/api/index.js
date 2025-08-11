import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    // 对请求错误做些什么
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    return response
  },
  (error) => {
    // 对响应错误做点什么
    console.error('响应错误:', error)
    
    let message = '网络请求失败'
    if (error.response) {
      // 服务器返回错误状态码
      message = error.response.data?.message || `请求失败 (${error.response.status})`
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message = '网络连接失败，请检查网络设置'
    } else {
      // 其他错误
      message = error.message || '未知错误'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API方法定义
const apiMethods = {
  // 通用接口
  getProvinces() {
    return api.get('/common/provinces')
  },
  
  getPlateLetters(province) {
    return api.get(`/common/plate_letters/${province}`)
  },
  
  validateField(type, value) {
    return api.post('/common/validate', { type, value })
  },
  
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/common/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 客车ETC接口
  applyETC(data) {
    return api.post('/etc/apply', data)
  },
  
  saveETCData(data) {
    return api.post('/etc/save_data', data)
  },
  
  getETCDefaultData() {
    return api.get('/etc/get_default_data')
  },
  
  sendVerifyCode(phone) {
    return api.post('/etc/verify_code', { phone })
  },
  
  getProducts(operatorCode = 'TXB', vehicleType = '0') {
    return api.get(`/etc/products?operator_code=${operatorCode}&vehicle_type=${vehicleType}`)
  },
  
  getOperators(vehicleType = '0') {
    return api.get(`/etc/operators?vehicle_type=${vehicleType}`)
  },
  
  confirmVerifyCode(data) {
    return api.post('/etc/confirm_verify_code', data)
  },
  
  getProgress(taskId) {
    return api.get(`/etc/progress/${taskId}`)
  },
  
  // 货车申办接口
  applyTruck(data) {
    return api.post('/truck/apply', data)
  },
  
  saveTruckData(data) {
    return api.post('/truck/save_data', data)
  },
  
  getTruckDefaultData() {
    return api.get('/truck/get_default_data')
  },
  
  getTruckOperators() {
    return api.get('/truck/operators')
  },
  
  getTruckProducts(operatorCode) {
    return api.get(`/truck/products?operator_code=${operatorCode}`)
  }
}

export default apiMethods 