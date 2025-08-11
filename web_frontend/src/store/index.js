import { createStore } from 'vuex'
import api from '../api'

export default createStore({
  state: {
    // 默认数据
    defaultData: {
      provinces: [],
      hotProvinces: [],
      vehicleColors: []
    },
    
    // 申办状态
    applyStatus: {
      isApplying: false,
      progress: 0,
      message: '',
      taskId: null
    },
    
    // 用户输入数据
    formData: {
      passenger: {
        name: '',
        idCode: '',
        phone: '',
        bankNo: '',
        bankName: '',
        plateProvince: '',
        plateLetter: '',
        plateNumber: '',
        vin: '',
        vehicleColor: ''
      },
      truck: {
        name: '',
        idCode: '',
        phone: '',
        bankNo: '',
        bankName: '',
        plateProvince: '',
        plateLetter: '',
        plateNumber: '',
        vin: '',
        loadWeight: '',
        length: '',
        width: '',
        height: '',
        vehicleColor: '黄色',
        vehicleType: '',
        usePurpose: '货运',
        axleCount: '2',
        tireCount: '6'
      }
    }
  },
  
  mutations: {
    // 设置默认数据
    SET_DEFAULT_DATA(state, data) {
      state.defaultData = { ...state.defaultData, ...data }
    },
    
    // 设置申办状态
    SET_APPLY_STATUS(state, status) {
      state.applyStatus = { ...state.applyStatus, ...status }
    },
    
    // 更新表单数据
    UPDATE_FORM_DATA(state, { type, data }) {
      if (state.formData[type]) {
        state.formData[type] = { ...state.formData[type], ...data }
      }
    },
    
    // 重置表单数据
    RESET_FORM_DATA(state, type) {
      if (type === 'passenger') {
        state.formData.passenger = {
          name: '',
          idCode: '',
          phone: '',
          bankNo: '',
          bankName: '',
          plateProvince: '',
          plateLetter: '',
          plateNumber: '',
          vin: '',
          vehicleColor: ''
        }
      } else if (type === 'truck') {
        state.formData.truck = {
          name: '',
          idCode: '',
          phone: '',
          bankNo: '',
          bankName: '',
          plateProvince: '',
          plateLetter: '',
          plateNumber: '',
          vin: '',
          loadWeight: '',
          length: '',
          width: '',
          height: '',
          vehicleColor: '黄色',
          vehicleType: '',
          usePurpose: '货运',
          axleCount: '2',
          tireCount: '6'
        }
      }
    }
  },
  
  actions: {
    // 加载默认数据
    async loadDefaultData({ commit }, type = 'passenger') {
      try {
        let response
        if (type === 'passenger') {
          response = await api.getETCDefaultData()
        } else {
          response = await api.getTruckDefaultData()
        }
        
        if (response.data.success) {
          commit('SET_DEFAULT_DATA', response.data.data)
        }
        return response.data
      } catch (error) {
        console.error('加载默认数据失败:', error)
        throw error
      }
    },
    
    // 获取省份列表
    async loadProvinces({ commit }) {
      try {
        const response = await api.getProvinces()
        if (response.data.success) {
          commit('SET_DEFAULT_DATA', {
            provinces: response.data.data.all_provinces,
            hotProvinces: response.data.data.hot_provinces
          })
        }
        return response.data
      } catch (error) {
        console.error('加载省份列表失败:', error)
        throw error
      }
    },
    
    // 客车申办
    async applyETC({ commit, state }) {
      try {
        commit('SET_APPLY_STATUS', { isApplying: true, progress: 0, message: '正在提交申办...' })
        
        const response = await api.applyETC(state.formData.passenger)
        
        if (response.data.success) {
          const taskId = response.data.data.apply_id
          commit('SET_APPLY_STATUS', {
            taskId: taskId,
            progress: response.data.data.progress || 10,
            message: response.data.message || '申办流程已启动',
            orderId: response.data.data.order_id,
            signOrderId: response.data.data.sign_order_id,
            verifyCodeNo: response.data.data.verify_code_no,
            status: response.data.data.status
          })
          
          // 启动进度轮询
          if (taskId) {
            store.dispatch('startProgressPolling', taskId)
          }
        } else {
          commit('SET_APPLY_STATUS', { isApplying: false, message: response.data.message })
        }
        
        return response.data
      } catch (error) {
        commit('SET_APPLY_STATUS', { isApplying: false, message: '申办失败，请稍后重试' })
        console.error('客车申办失败:', error)
        throw error
      }
    },
    
    // 进度轮询
    async startProgressPolling({ commit }, taskId) {
      const pollInterval = setInterval(async () => {
        try {
          const response = await api.getProgress(taskId)
          if (response.data.success) {
            const progressData = response.data.data
            commit('SET_APPLY_STATUS', {
              progress: progressData.progress,
              message: progressData.message,
              status: progressData.status
            })
            
            // 如果进度完成或失败，停止轮询
            if (progressData.progress >= 100 || progressData.status === 'completed' || progressData.status === 'failed') {
              clearInterval(pollInterval)
            }
          }
        } catch (error) {
          console.error('进度轮询失败:', error)
          clearInterval(pollInterval)
        }
      }, 2000) // 每2秒轮询一次
    },
    
    // 确认验证码
    async confirmVerifyCode({ commit, state }, verifyCode) {
      try {
        commit('SET_APPLY_STATUS', { isApplying: true, message: '正在确认验证码...' })
        
        const data = {
          verifyCode: verifyCode,
          orderId: state.applyStatus.orderId,
          signOrderId: state.applyStatus.signOrderId,
          verifyCodeNo: state.applyStatus.verifyCodeNo
        }
        
        const response = await api.confirmVerifyCode(data)
        
        if (response.data.success) {
          commit('SET_APPLY_STATUS', {
            isApplying: false,
            progress: 100,
            message: response.data.message || '申办成功完成',
            status: 'completed'
          })
        } else {
          commit('SET_APPLY_STATUS', { isApplying: false, message: response.data.message })
        }
        
        return response.data
      } catch (error) {
        commit('SET_APPLY_STATUS', { isApplying: false, message: '验证码确认失败，请稍后重试' })
        console.error('验证码确认失败:', error)
        throw error
      }
    },
    
    // 货车申办
    async applyTruck({ commit, state }) {
      try {
        commit('SET_APPLY_STATUS', { isApplying: true, progress: 0, message: '正在提交申办...' })
        
        const response = await api.applyTruck(state.formData.truck)
        
        if (response.data.success) {
          commit('SET_APPLY_STATUS', {
            taskId: response.data.data.task_id,
            progress: response.data.data.progress || 10,
            message: response.data.message || '申办流程已启动'
          })
        } else {
          commit('SET_APPLY_STATUS', { isApplying: false, message: response.data.message })
        }
        
        return response.data
      } catch (error) {
        commit('SET_APPLY_STATUS', { isApplying: false, message: '申办失败，请稍后重试' })
        console.error('货车申办失败:', error)
        throw error
      }
    },
    
    // 保存数据
    async saveData({ state }, type) {
      try {
        let response
        if (type === 'passenger') {
          response = await api.saveETCData(state.formData.passenger)
        } else {
          response = await api.saveTruckData(state.formData.truck)
        }
        return response.data
      } catch (error) {
        console.error('保存数据失败:', error)
        throw error
      }
    },
    
    // 发送验证码
    async sendVerifyCode({ state }, { phone, type }) {
      try {
        const response = await api.sendVerifyCode(phone)
        return response.data
      } catch (error) {
        console.error('发送验证码失败:', error)
        throw error
      }
    }
  },
  
  getters: {
    // 获取表单数据
    getFormData: (state) => (type) => {
      return state.formData[type] || {}
    },
    
    // 获取申办状态
    getApplyStatus: (state) => {
      return state.applyStatus
    },
    
    // 获取默认数据
    getDefaultData: (state) => {
      return state.defaultData
    }
  }
}) 