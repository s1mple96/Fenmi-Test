<template>
  <div class="province-map">
    <!-- ECharts地图容器 -->
    <div ref="mapContainer" class="map-container"></div>
    
    <!-- 备用省份选择方案 -->
    <div v-if="showFallback" class="fallback-selection">
      <div class="fallback-header">
        <h3>选择省份</h3>
        <p>地图加载失败，请使用下方按钮选择省份</p>
      </div>
      
      <!-- 热门省份 -->
      <div class="hot-provinces">
        <h4>热门省份</h4>
        <div class="province-grid">
          <button 
            v-for="province in hotProvinces" 
            :key="province.code"
            :class="['province-btn', { active: selectedProvince === province.code }]"
            @click="selectProvince(province.code, province.name)"
          >
            <span style="font-size: 16px; font-weight: bold; color: #1890ff;">{{ province.code }}</span><br>
            <span style="font-size: 10px; color: #666;">{{ province.name }}</span>
          </button>
        </div>
      </div>
      
      <!-- 所有省份 -->
      <div class="all-provinces">
        <h4>所有省份</h4>
        <div class="province-grid all">
          <button 
            v-for="province in allProvinces" 
            :key="province.code"
            :class="['province-btn small', { active: selectedProvince === province.code }]"
            @click="selectProvince(province.code, province.name)"
          >
            <span style="font-size: 14px; font-weight: bold; color: #1890ff;">{{ province.code }}</span><br>
            <span style="font-size: 9px; color: #666;">{{ province.name }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

// 省份名称到代码的映射
const provinceNameToCode = {
  // 直辖市
  '北京': '京', '北京市': '京', '天津': '津', '天津市': '津', 
  '上海': '沪', '上海市': '沪', '重庆': '渝', '重庆市': '渝',
  
  // 省份
  '河北': '冀', '河北省': '冀', '山西': '晋', '山西省': '晋', 
  '辽宁': '辽', '辽宁省': '辽', '吉林': '吉', '吉林省': '吉', 
  '黑龙江': '黑', '黑龙江省': '黑', '江苏': '苏', '江苏省': '苏',
  '浙江': '浙', '浙江省': '浙', '安徽': '皖', '安徽省': '皖', 
  '福建': '闽', '福建省': '闽', '江西': '赣', '江西省': '赣', 
  '山东': '鲁', '山东省': '鲁', '河南': '豫', '河南省': '豫', 
  '湖北': '鄂', '湖北省': '鄂', '湖南': '湘', '湖南省': '湘', 
  '广东': '粤', '广东省': '粤', '海南': '琼', '海南省': '琼',
  '四川': '川', '四川省': '川', '贵州': '贵', '贵州省': '贵', 
  '云南': '云', '云南省': '云', '陕西': '陕', '陕西省': '陕', 
  '甘肃': '甘', '甘肃省': '甘', '青海': '青', '青海省': '青',
  
  // 自治区
  '内蒙古': '蒙', '内蒙古自治区': '蒙', '广西': '桂', '广西壮族自治区': '桂',
  '西藏': '藏', '西藏自治区': '藏', '宁夏': '宁', '宁夏回族自治区': '宁',
  '新疆': '新', '新疆维吾尔自治区': '新',
  
  // 特别行政区
  '香港': '港', '香港特别行政区': '港', '澳门': '澳', '澳门特别行政区': '澳',
  
  // 台湾
  '台湾': '台', '台湾省': '台'
}

// 完整的省份数据（包含所有省份、自治区、直辖市、特别行政区）
const allProvincesData = [
  // 直辖市
  { code: '京', name: '北京' }, { code: '津', name: '天津' }, { code: '沪', name: '上海' }, { code: '渝', name: '重庆' },
  
  // 华北地区
  { code: '冀', name: '河北' }, { code: '晋', name: '山西' }, { code: '蒙', name: '内蒙古' },
  
  // 东北地区
  { code: '辽', name: '辽宁' }, { code: '吉', name: '吉林' }, { code: '黑', name: '黑龙江' },
  
  // 华东地区
  { code: '苏', name: '江苏' }, { code: '浙', name: '浙江' }, { code: '皖', name: '安徽' },
  { code: '闽', name: '福建' }, { code: '赣', name: '江西' }, { code: '鲁', name: '山东' },
  
  // 华中地区
  { code: '豫', name: '河南' }, { code: '鄂', name: '湖北' }, { code: '湘', name: '湖南' },
  
  // 华南地区
  { code: '粤', name: '广东' }, { code: '桂', name: '广西' }, { code: '琼', name: '海南' },
  
  // 西南地区
  { code: '川', name: '四川' }, { code: '贵', name: '贵州' }, { code: '云', name: '云南' }, { code: '藏', name: '西藏' },
  
  // 西北地区
  { code: '陕', name: '陕西' }, { code: '甘', name: '甘肃' }, { code: '青', name: '青海' }, 
  { code: '宁', name: '宁夏' }, { code: '新', name: '新疆' },
  
  // 特别行政区
  { code: '港', name: '香港' }, { code: '澳', name: '澳门' },
  
  // 台湾地区
  { code: '台', name: '台湾' },
  
  // 特殊车牌
  { code: '使', name: '使馆' }, { code: '领', name: '领馆' }
]

// 热门省份
const hotProvincesData = [
  { code: '京', name: '北京' }, { code: '沪', name: '上海' }, { code: '粤', name: '广东' },
  { code: '苏', name: '江苏' }, { code: '浙', name: '浙江' }, { code: '鲁', name: '山东' },
  { code: '川', name: '四川' }, { code: '湘', name: '湖南' }, { code: '桂', name: '广西' },
  { code: '黑', name: '黑龙江' }, { code: '蒙', name: '内蒙古' }, { code: '豫', name: '河南' }
]

export default {
  name: 'ProvinceMap',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'select'],
  setup(props, { emit }) {
    const mapContainer = ref(null)
    const selectedProvince = ref(props.modelValue)
    const showFallback = ref(false)
    const allProvinces = ref(allProvincesData)
    const hotProvinces = ref(hotProvincesData)
    let chart = null
    
    const selectProvince = (code, name) => {
      selectedProvince.value = code
      emit('update:modelValue', code)
      emit('select', { code, name })
    }
    
    // 创建简化的地图数据
    const createSimpleMapData = () => {
      // 由于无法加载外部地图数据，直接显示备用界面
      console.log('使用备用省份选择界面')
      showFallback.value = true
      return null
    }
    
    // 初始化ECharts地图
    const initMap = async () => {
      if (!mapContainer.value) return
      
      try {
        let geoData = null
        
        // 尝试多个地图数据源
        const mapSources = [
          'https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json',
          'https://raw.githubusercontent.com/hujiaweibujidao/china-geojson/master/china.json',
          'https://raw.githubusercontent.com/adyliu/china_area/master/china.geojson'
        ]
        
        let geoDataLoaded = false
        
        for (const source of mapSources) {
          try {
            console.log(`尝试加载地图数据源: ${source}`)
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 3000)
            
            const response = await fetch(source, {
              signal: controller.signal,
              mode: 'cors'
            })
            
            clearTimeout(timeoutId)
            
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}`)
            }
            
            geoData = await response.json()
            console.log(`地图数据加载成功，数据源: ${source}`)
            geoDataLoaded = true
            break
          } catch (error) {
            console.warn(`地图数据源 ${source} 加载失败:`, error)
          }
        }
        
        if (!geoDataLoaded) {
          console.warn('所有地图数据源都加载失败，使用备用方案')
          // 直接显示备用界面
          createSimpleMapData()
          return
        }
        
        echarts.registerMap('china', geoData)
        chart = echarts.init(mapContainer.value)
        
        const option = {
          tooltip: {
            trigger: 'item',
            formatter: function(params) {
              const provinceName = params.name
              const provinceCode = provinceNameToCode[provinceName] || provinceName
              return `${provinceName} (${provinceCode})<br/>点击选择此省份`
            }
          },
          geo: {
            map: 'china',
            roam: false,
            zoom: 1.2,
            center: [104.1954, 37.5436],
            labelLayout: {
              hideOverlap: true,
              moveOverlap: 'shiftY'
            },
            itemStyle: {
              areaColor: '#e6f3ff',
              borderColor: '#1890ff',
              borderWidth: 1
            },
            emphasis: {
              itemStyle: {
                areaColor: '#bae7ff',
                borderColor: '#096dd9',
                borderWidth: 2
              }
            },
            select: {
              itemStyle: {
                areaColor: '#1890ff',
                borderColor: '#096dd9'
              }
            },
            label: {
              show: true,
              fontSize: 16,
              color: '#333',
              fontWeight: 'bold',
              distance: 5,
              formatter: function(params) {
                const provinceName = params.name
                const code = provinceNameToCode[provinceName] || provinceName
                // 对于面积较小的地区，只显示前缀避免重叠
                const smallAreas = ['香港', '澳门', '台湾', '海南']
                if (smallAreas.includes(provinceName)) {
                  return code
                }
                return code
              }
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 18,
                color: '#096dd9',
                fontWeight: 'bold',
                distance: 5,
                formatter: function(params) {
                  const provinceName = params.name
                  return provinceNameToCode[provinceName] || provinceName
                }
              }
            }
          }
        }
        
        chart.setOption(option)
        
        // 点击事件
        chart.on('click', function(params) {
          if (params.componentType === 'geo') {
            const provinceName = params.name
            const provinceCode = provinceNameToCode[provinceName] || provinceName
            selectProvince(provinceCode, provinceName)
          }
        })
        
        // 响应式调整
        const resizeHandler = () => {
          chart && chart.resize()
        }
        window.addEventListener('resize', resizeHandler)
        
        // 清理函数
        const cleanup = () => {
          window.removeEventListener('resize', resizeHandler)
          if (chart) {
            chart.dispose()
            chart = null
          }
        }
        
        // 组件卸载时清理
        return cleanup
        
      } catch (error) {
        console.error('地图初始化失败，显示备用选择界面:', error)
        showFallback.value = true
      }
    }
    
    onMounted(async () => {
      console.log('省份地图组件加载，优先尝试显示地图')
      
      // 延迟初始化，确保在对话框中也能正确渲染
      setTimeout(async () => {
        await nextTick()
        
        // 等待DOM元素完全渲染并有尺寸
        const waitForDOMReady = () => {
          return new Promise((resolve, reject) => {
            let attempts = 0
            const maxAttempts = 30 // 最多尝试3秒
            
            const checkDOM = () => {
              attempts++
              const rect = mapContainer.value?.getBoundingClientRect()
              console.log(`DOM检查第${attempts}次:`, {
                exists: !!mapContainer.value,
                clientWidth: mapContainer.value?.clientWidth || 0,
                clientHeight: mapContainer.value?.clientHeight || 0,
                rectWidth: rect?.width || 0,
                rectHeight: rect?.height || 0
              })
              
                             // 如果高度正常但宽度为0，尝试强制设置宽度
              if (mapContainer.value && mapContainer.value.clientHeight > 0 && mapContainer.value.clientWidth === 0) {
                console.log('检测到宽度为0，强制设置宽度和样式')
                
                // 获取父容器宽度
                const parentWidth = mapContainer.value.parentElement?.clientWidth || 600
                console.log('父容器宽度:', parentWidth)
                
                // 强制设置多种宽度属性
                mapContainer.value.style.width = `${Math.max(parentWidth - 20, 1000)}px`
                mapContainer.value.style.minWidth = '1000px'
                mapContainer.value.style.display = 'block'
                mapContainer.value.style.position = 'relative'
                mapContainer.value.style.flexShrink = '0'
                
                // 强制重新计算布局
                mapContainer.value.offsetHeight // 触发重排
                
                // 等待一个渲染周期后再次检查
                setTimeout(() => {
                  const newWidth = mapContainer.value?.clientWidth || 0
                  console.log('强制设置样式后的宽度:', newWidth)
                  if (newWidth > 0) {
                    console.log('DOM准备就绪，开始初始化地图')
                    resolve()
                  } else if (attempts >= maxAttempts) {
                    console.warn('强制设置后宽度仍为0，显示备用界面')
                    reject(new Error('DOM宽度始终为0'))
                  } else {
                    setTimeout(checkDOM, 100)
                  }
                }, 150)
                return
              }
              
              // 正常情况：宽度和高度都大于0
              if (mapContainer.value && 
                  mapContainer.value.clientWidth > 0 && 
                  mapContainer.value.clientHeight > 0) {
                console.log('DOM准备就绪，开始初始化地图')
                resolve()
              } else if (attempts >= maxAttempts) {
                console.warn('DOM准备超时，显示备用界面')
                reject(new Error('DOM准备超时'))
              } else {
                setTimeout(checkDOM, 100)
              }
            }
            checkDOM()
          })
        }
        
        try {
          // 等待DOM准备就绪
          await waitForDOMReady()
          
          // 设置地图加载超时
          const mapLoadTimeout = setTimeout(() => {
            if (!chart && !showFallback.value) {
              console.warn('地图加载超时，显示备用界面')
              showFallback.value = true
            }
          }, 5000) // 5秒超时
          
          // 尝试初始化地图
          await initMap()
          clearTimeout(mapLoadTimeout)
          
          console.log('地图初始化成功')
        } catch (error) {
          console.error('地图初始化失败，显示备用界面:', error)
          showFallback.value = true
        }
      }, 300) // 延迟300ms确保对话框完全渲染
    })
    
    return {
      mapContainer,
      selectedProvince,
      selectProvince,
      showFallback,
      allProvinces,
      hotProvinces
    }
  }
}
</script>

<style scoped>
.province-map {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.map-container {
  width: 100%;
  min-width: 1000px;
  max-width: 100%;
  height: 700px;
  background: #f5f5f5;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  box-sizing: border-box;
  display: block;
  position: relative;
  flex-shrink: 0;
}

.fallback-selection {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
}

.fallback-header {
  text-align: center;
  margin-bottom: 20px;
}

.fallback-header h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.fallback-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.hot-provinces, .all-provinces {
  margin-bottom: 20px;
}

.hot-provinces h4, .all-provinces h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 5px;
}

.province-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.province-grid.all {
  gap: 6px;
}

.province-btn {
  min-width: 80px;
  height: 50px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #fff;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1.2;
}

.province-btn.small {
  min-width: 60px;
  height: 40px;
  font-size: 11px;
}

.province-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
  background: #f0f8ff;
}

.province-btn.active {
  border-color: #1890ff;
  background: #1890ff;
  color: #fff;
}

.province-btn:active {
  transform: scale(0.98);
}
</style> 