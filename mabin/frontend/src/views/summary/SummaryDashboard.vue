<template>
  <div class="summary-dashboard">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="iconify text-2xl" data-icon="solar:Square-academic-cap-bold"></span>
        </div>
        <h1 class="sidebar-title">总结管理系统</h1>
      </div>
      <nav class="sidebar-nav">
        <a class="nav-item active" href="#">
          <span class="iconify text-xl" data-icon="solar:home-2-linear"></span>
          控制面板
        </a>
        <a class="nav-item" href="#">
          <span class="iconify text-xl" data-icon="solar:document-text-linear"></span>
          我的总结
        </a>
        <a class="nav-item" href="#">
          <span class="iconify text-xl" data-icon="solar:chart-2-linear"></span>
          学情分析
        </a>
        <a class="nav-item" href="#">
          <span class="iconify text-xl" data-icon="solar:users-group-rounded-linear"></span>
          协作小组
        </a>
        <div class="nav-divider">系统设置</div>
        <a class="nav-item" href="#">
          <span class="iconify text-xl" data-icon="solar:settings-linear"></span>
          个人设置
        </a>
      </nav>
      <div class="sidebar-footer">
        <div class="storage-info">
          <p class="storage-label">当前存储空间</p>
          <div class="storage-bar">
            <div class="storage-progress" style="width: 65%"></div>
          </div>
          <p class="storage-value">12.8 GB / 20 GB</p>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航 -->
            <header class="top-header">
              <div class="header-left">
                <button class="menu-btn">
                  <span class="iconify text-xl" data-icon="solar:align-justify-bold"></span>
                </button>
                <div class="search-box">
                  <span class="iconify text-lg" data-icon="solar:magnifer-bold"></span>
                  <input type="text" class="search-input" placeholder="全局搜索... (Ctrl+K)" />
                </div>
              </div>
              <div class="header-right">
                <button class="icon-btn">
                  <span class="iconify text-xl" data-icon="solar:bell-bold"></span>
                  <span class="badge">4</span>
                </button>
                <button class="icon-btn" @click="toggleDarkMode">
                  <span class="iconify text-xl" :data-icon="isDarkMode ? 'solar:sun-bold' : 'solar:moon-bold'"></span>
                </button>
                <button class="icon-btn">
                  <span class="iconify text-xl" data-icon="solar:settings-bold"></span>
                </button>
                <div class="user-info">
                  <span class="iconify text-xl" data-icon="solar:user-bold"></span>
                  <span class="user-name">张教授</span>
                </div>
              </div>
            </header>

      <!-- 内容滚动区 -->
      <div class="content-scroll">
        <!-- 骨架屏加载状态 -->
        <div v-if="isLoading" class="skeleton-container">
          <div class="skeleton-welcome">
            <div class="skeleton-title"></div>
            <div class="skeleton-subtitle"></div>
          </div>

          <div class="skeleton-kpi-grid">
            <div class="skeleton-kpi-card"></div>
            <div class="skeleton-kpi-card"></div>
            <div class="skeleton-kpi-card"></div>
            <div class="skeleton-kpi-card"></div>
          </div>

          <div class="skeleton-main-grid">
            <div class="skeleton-chart-card">
              <div class="skeleton-chart-header">
                <div class="skeleton-chart-title"></div>
                <div class="skeleton-chart-select"></div>
              </div>
              <div class="skeleton-chart-container"></div>
            </div>

            <div class="skeleton-ai-dashboard">
              <div class="skeleton-ai-header">
                <div class="skeleton-ai-icon"></div>
                <div class="skeleton-ai-title"></div>
              </div>
              <div class="skeleton-ai-content"></div>
              <div class="skeleton-ai-button"></div>
            </div>
          </div>

          <div class="skeleton-ai-summary"></div>
          <div class="skeleton-table"></div>
        </div>

        <!-- 实际内容 -->
        <div v-else>
          <!-- 欢迎及AI看板区 -->
          <div class="welcome-section">
            <h2 class="welcome-title">早安，张教授 👋</h2>
            <p class="welcome-subtitle">今天是 2026年02月28日，您有 4 个待审批的总结报告。</p>
          </div>

        <!-- 数据 KPI 卡片 -->
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon blue">
                <span class="iconify text-2xl" data-icon="solar:document-bold"></span>
              </div>
              <span class="kpi-trend positive">+12% <span class="iconify ml-1" data-icon="solar:arrow-right-up-linear"></span></span>
            </div>
            <p class="kpi-label">本月提交总量</p>
            <h3 class="kpi-value">1,284</h3>
          </div>
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon green">
                <span class="iconify text-2xl" data-icon="solar:check-circle-bold"></span>
              </div>
              <span class="kpi-trend positive">+5% <span class="iconify ml-1" data-icon="solar:arrow-right-up-linear"></span></span>
            </div>
            <p class="kpi-label">已完成总结</p>
            <h3 class="kpi-value">856</h3>
          </div>
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon amber">
                <span class="iconify text-2xl" data-icon="solar:clock-circle-bold"></span>
              </div>
              <span class="kpi-trend negative">-2% <span class="iconify ml-1" data-icon="solar:arrow-right-down-linear"></span></span>
            </div>
            <p class="kpi-label">平均处理时长</p>
            <h3 class="kpi-value">4.2h</h3>
          </div>
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon purple">
                <span class="iconify text-2xl" data-icon="solar:stars-bold"></span>
              </div>
              <span class="kpi-trend positive">+18% <span class="iconify ml-1" data-icon="solar:arrow-right-up-linear"></span></span>
            </div>
            <p class="kpi-label">AI 协作率</p>
            <h3 class="kpi-value">92.4%</h3>
          </div>
        </div>

        <!-- 主图表与 AI 看板 -->
        <div class="main-grid">
          <!-- 图表 -->
          <div class="chart-card">
            <div class="chart-header">
              <div>
                <h3 class="chart-title">学情总结效能趋势</h3>
                <p class="chart-subtitle">展示 2026年 以来各月份的协作效率对比</p>
              </div>
              <select class="chart-select">
                <option>最近六个月</option>
                <option>全年数据</option>
              </select>
            </div>
            <div class="chart-container" id="mainChart"></div>
          </div>

          <!-- AI 智能看板小贴纸 -->
          <div class="ai-dashboard">
            <div class="ai-header">
              <span class="iconify text-2xl text-emerald-300" data-icon="solar:magic-stick-3-bold"></span>
              <h3 class="ai-title">AI 智能分析看板</h3>
            </div>
            <div class="ai-content">
              <div class="ai-card">
                <p class="ai-label">今日洞察</p>
                <p class="ai-text">"智能体3的工作已经完成效率优化，系统响应速度提升了 30%。"</p>
              </div>
              <div class="ai-card">
                <p class="ai-label">待关注异常</p>
                <p class="ai-text">"发现 2 个协作小组的总结频率在过去48小时内显著下降，建议及时介入。"</p>
              </div>
            </div>
            <button class="ai-button">
              呼叫 AI 助手
              <span class="iconify" data-icon="solar:alt-arrow-right-linear"></span>
            </button>
          </div>
        </div>

        <!-- AI 智能总结输入框 -->
        <div class="ai-summary-section">
          <div class="ai-header">
            <span class="iconify text-2xl text-emerald-300" data-icon="solar:magic-stick-3-bold"></span>
            <h3 class="ai-title">智能总结助手</h3>
          </div>
          <div class="ai-input-container">
            <div 
              class="ai-summary-input-wrapper" 
              :class="{ 'drag-over': isDragOver }"
              @dragover.prevent="handleDragOver"
              @dragleave="handleDragLeave"
              @drop.prevent="handleDrop"
            >
              <textarea 
                class="ai-summary-input" 
                placeholder="输入总结内容或使用斜杠命令（/summary）快速生成..."
                @keydown="handleSlashCommand"
              ></textarea>
              <div v-if="isDragOver" class="drag-overlay">
                <span class="iconify text-4xl text-emerald-300" data-icon="solar:cloud-upload-bold"></span>
                <p>松开鼠标上传文件</p>
              </div>
            </div>
            <div class="ai-input-actions">
              <button class="ai-btn-primary">
                <span class="iconify text-lg" data-icon="solar:rocket-bold"></span>
                生成总结
              </button>
              <label class="ai-btn-secondary">
                <span class="iconify text-lg" data-icon="solar:attach-circle-bold"></span>
                上传附件
                <input 
                  type="file" 
                  multiple 
                  style="display: none;"
                  @change="handleFileSelect"
                />
              </label>
            </div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-card">
          <div class="table-header">
            <div>
              <h3 class="table-title">最近总结列表</h3>
              <p class="table-subtitle">共计 128 份待标记总结</p>
            </div>
            <div class="table-actions">
              <button class="action-btn secondary">
                <span class="iconify text-lg" data-icon="solar:filter-linear"></span>
                筛选
              </button>
              <button class="action-btn primary">
                <span class="iconify text-lg" data-icon="solar:add-circle-linear"></span>
                新建总结
              </button>
            </div>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>文件名称</th>
                  <th>提交人</th>
                  <th>提交日期</th>
                  <th>状态</th>
                  <th>优先级</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr class="table-row" @touchstart="handleTouchStart" @touchmove="handleTouchMove" @touchend="handleTouchEnd">
                  <td>
                    <div class="file-info">
                      <div class="file-icon red">
                        <span class="iconify text-xl" data-icon="solar:file-text-bold"></span>
                      </div>
                      <div class="file-details">
                        <p class="file-name">2026年Q1学情研究报告.pdf</p>
                        <p class="file-size">1.2 MB · 文档</p>
                      </div>
                    </div>
                  </td>
                  <td>李华 (研究员)</td>
                  <td>2026-02-27</td>
                  <td>
                    <span class="status-badge green">
                      <span class="status-dot pulse"></span>
                      已审阅
                    </span>
                  </td>
                  <td>
                    <span class="priority-badge high">高</span>
                  </td>
                  <td>
                    <button class="action-btn minimal">
                      <span class="iconify" data-icon="solar:menu-dots-bold"></span>
                    </button>
                  </td>
                </tr>
                <tr class="table-row" @touchstart="handleTouchStart" @touchmove="handleTouchMove" @touchend="handleTouchEnd">
                  <td>
                    <div class="file-info">
                      <div class="file-icon blue">
                        <span class="iconify text-xl" data-icon="solar:file-send-bold"></span>
                      </div>
                      <div class="file-details">
                        <p class="file-name">人工智能伦理课程总结.docx</p>
                        <p class="file-size">856 KB · 文档</p>
                      </div>
                    </div>
                  </td>
                  <td>王小明 (本科生)</td>
                  <td>2026-02-28</td>
                  <td>
                    <span class="status-badge amber">
                      <span class="status-dot"></span>
                      待审批
                    </span>
                  </td>
                  <td>
                    <span class="priority-badge medium">中</span>
                  </td>
                  <td>
                    <button class="action-btn minimal">
                      <span class="iconify" data-icon="solar:menu-dots-bold"></span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <p class="footer-info">显示第 1 至 2 条结果，共 128 条记录</p>
            <div class="pagination">
              <button class="pagination-btn disabled">上一页</button>
              <button class="pagination-btn active">1</button>
              <button class="pagination-btn">2</button>
              <button class="pagination-btn">3</button>
              <button class="pagination-btn">下一页</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 右侧动态侧边栏 Context Bar -->
    <aside class="context-bar">
      <div class="context-header">
        <h3 class="context-title">实时协作动态</h3>
      </div>
      <div class="context-content">
        <!-- 协作小组成员 -->
        <div class="context-section">
          <div class="section-header">
            <h4 class="section-title">小组成员</h4>
            <button class="section-action">管理</button>
          </div>
          <div class="member-list">
            <div class="member-item">
              <div class="member-info">
                <div class="member-avatar">
                  <img src="https://modao.cc/agent-py/media/generated_images/2026-02-28/f1041e4c884d4cc89799a08a9c2bc436.jpg" alt="Member" />
                  <span class="member-status online"></span>
                </div>
                <div class="member-details">
                  <p class="member-name">陈默言</p>
                  <p class="member-status-text">正在撰写总结...</p>
                </div>
              </div>
              <span class="iconify text-slate-300" data-icon="solar:chat-round-line-linear"></span>
            </div>
            <div class="member-item">
              <div class="member-info">
                <div class="member-avatar">
                  <img src="https://modao.cc/agent-py/media/generated_images/2026-02-28/f1041e4c884d4cc89799a08a9c2bc436.jpg" alt="Member" />
                  <span class="member-status offline"></span>
                </div>
                <div class="member-details">
                  <p class="member-name">林溪云</p>
                  <p class="member-status-text">30分钟前在线</p>
                </div>
              </div>
              <span class="iconify text-slate-300" data-icon="solar:chat-round-line-linear"></span>
            </div>
          </div>
        </div>

        <div class="context-divider"></div>

        <!-- 智能建议区 -->
        <div class="context-section">
          <h4 class="section-title">AI 优化建议</h4>
          <div class="ai-suggestion">
            <div class="suggestion-header">
              <span class="iconify" data-icon="solar:lightbulb-bold"></span>
              撰写提示
            </div>
            <p class="suggestion-text">
              检测到您正在处理 "AI 伦理" 的相关总结。建议引入最新的 2026年 行业治理架构图表以增强学术性。
            </p>
            <button class="suggestion-action">应用此建议</button>
          </div>
        </div>

        <!-- 待办清单 -->
        <div class="context-section">
          <h4 class="section-title">今日待处理</h4>
          <div class="todo-list">
            <label class="todo-item">
              <input type="checkbox" />
              <span class="todo-text">审批李华的研究报告</span>
            </label>
            <label class="todo-item">
              <input type="checkbox" checked />
              <span class="todo-text completed">回复校务办公室邮件</span>
            </label>
            <label class="todo-item">
              <input type="checkbox" />
              <span class="todo-text">更新实验室设备清册</span>
            </label>
          </div>
        </div>
      </div>
      <div class="context-footer">
        <div class="footer-info">
          <span>系统版本 v2.0-2026</span>
          <span class="system-status">
            <span class="status-dot green"></span>
            运行正常
          </span>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
        import { ref, onMounted, computed } from 'vue'
        import * as echarts from 'echarts'

        // 深色模式状态
        const isDarkMode = ref(false)

        // 切换深色模式
        const toggleDarkMode = () => {
          isDarkMode.value = !isDarkMode.value
          document.documentElement.classList.toggle('dark', isDarkMode.value)
          initChart() // 重新初始化图表以适配深色模式
        }

        // 初始化图表
        const initChart = () => {
          const chartDom = document.getElementById('mainChart')
          if (!chartDom) return
          const myChart = echarts.init(chartDom)
  
  const option = {
            backgroundColor: isDarkMode.value ? '#1A1C1E' : '#F8FAFC',
            tooltip: {
              trigger: 'axis',
              axisPointer: { type: 'shadow' },
              backgroundColor: isDarkMode.value ? '#2D3748' : '#FFFFFF',
              borderColor: isDarkMode.value ? '#4A5568' : '#E2E8F0',
              textStyle: { color: isDarkMode.value ? '#E2E8F0' : '#2D3748' }
            },
            grid: {
              top: '10%',
              left: '2%',
              right: '2%',
              bottom: '5%',
              containLabel: true
            },
            xAxis: {
              type: 'category',
              data: ['9月', '10月', '11月', '12月', '1月', '2月'],
              axisLine: { show: false },
              axisTick: { show: false },
              axisLabel: { color: isDarkMode.value ? '#A0AEC0' : '#94a3b8' }
            },
            yAxis: {
              type: 'value',
              splitLine: { lineStyle: { type: 'dashed', color: isDarkMode.value ? '#2D3748' : '#f1f5f9' } },
              axisLabel: { color: isDarkMode.value ? '#A0AEC0' : '#94a3b8' }
            },
            series: [
              {
                data: [120, 200, 150, 80, 70, 110],
                type: 'bar',
                barWidth: '15px',
                itemStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: isDarkMode.value ? '#1E40AF' : '#2A5CAA' },
                    { offset: 1, color: isDarkMode.value ? '#3B82F6' : '#6390cf' }
                  ]),
                  borderRadius: [4, 4, 0, 0]
                },
                name: '提交量'
              },
              {
                data: [80, 150, 120, 60, 55, 95],
                type: 'bar',
                barWidth: '15px',
                itemStyle: {
                  color: isDarkMode.value ? '#059669' : '#00A676',
                  borderRadius: [4, 4, 0, 0]
                },
                name: '已通过'
              }
            ]
          }
  
  myChart.setOption(option)
  
  // 窗口大小变化自适应
  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

// 骨架屏状态
        const isLoading = ref(true)

        // 拖拽上传状态
        const isDragOver = ref(false)

        // 滑动手势状态
        const touchStartX = ref(0)
        const touchEndX = ref(0)

        // 全局搜索快捷键模拟 (Ctrl+K)
        const initKeyboardShortcuts = () => {
          document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
              e.preventDefault()
              const searchInput = document.querySelector('.search-input')
              if (searchInput) {
                searchInput.focus()
              }
            }
          })
        }

        // 模拟数据加载
        const loadData = () => {
          isLoading.value = true
          // 模拟API请求延迟
          setTimeout(() => {
            isLoading.value = false
          }, 1500)
        }

        // 拖拽上传处理
        const handleDragOver = (e) => {
          isDragOver.value = true
        }

        const handleDragLeave = (e) => {
          isDragOver.value = false
        }

        const handleDrop = (e) => {
          isDragOver.value = false
          const files = e.dataTransfer.files
          if (files.length > 0) {
            handleFiles(files)
          }
        }

        const handleFileSelect = (e) => {
          const files = e.target.files
          if (files.length > 0) {
            handleFiles(files)
          }
        }

        const handleFiles = (files) => {
          // 处理上传的文件
          console.log('上传的文件:', files)
          // 可以在这里添加文件上传逻辑
          alert(`成功选择 ${files.length} 个文件`)
        }

        // 滑动手势处理
        const handleTouchStart = (e) => {
          touchStartX.value = e.touches[0].clientX
        }

        const handleTouchMove = (e) => {
          touchEndX.value = e.touches[0].clientX
        }

        const handleTouchEnd = (e) => {
          const touchDiff = touchStartX.value - touchEndX.value
          const minSwipeDistance = 50

          if (touchDiff > minSwipeDistance) {
            // 左滑 - 显示操作菜单
            showSwipeActions(e.currentTarget)
          } else if (touchDiff < -minSwipeDistance) {
            // 右滑 - 隐藏操作菜单
            hideSwipeActions()
          }
        }

        const showSwipeActions = (row) => {
          // 显示滑动操作菜单
          console.log('显示滑动操作菜单')
          // 可以在这里实现滑动菜单的显示
          alert('左滑操作：可以删除或归档')
        }

        const hideSwipeActions = () => {
          // 隐藏滑动操作菜单
          console.log('隐藏滑动操作菜单')
        }

        // 斜杠命令处理
        const handleSlashCommand = (e) => {
          if (e.key === '/') {
            const textarea = e.target
            const value = textarea.value
            const cursorPosition = textarea.selectionStart
            const beforeCursor = value.substring(0, cursorPosition)
            const afterCursor = value.substring(cursorPosition)
            
            // 检查是否在行首或空格后
            if (beforeCursor.endsWith('\n') || beforeCursor.endsWith(' ') || beforeCursor === '') {
              // 显示斜杠命令菜单
              showSlashCommands(textarea, cursorPosition)
            }
          }
        }

        // 显示斜杠命令菜单
        const showSlashCommands = (textarea, position) => {
          // 这里可以实现斜杠命令菜单的显示
          console.log('显示斜杠命令菜单')
          // 示例：插入/summary命令
          textarea.value = textarea.value.substring(0, position) + 'summary ' + textarea.value.substring(position)
          textarea.selectionStart = textarea.selectionEnd = position + 8
        }

onMounted(() => {
  initKeyboardShortcuts()
  loadData()
  // 延迟初始化图表确保DOM已渲染
  setTimeout(() => {
    initChart()
  }, 100)
})
</script>

<style scoped>
/* 全局变量 */
:root {
  --brand-blue: #2A5CAA;
  --smart-green: #00A676;
  --bg-slate: #F8FAFC;
  --white: #FFFFFF;
  --shadow-soft: 0 8px 30px rgba(0, 0, 0, 0.04);
}

/* 深色模式变量 */
:root.dark {
  --bg-slate: #1A1C1E;
  --white: #2D3748;
  --shadow-soft: 0 8px 30px rgba(0, 0, 0, 0.3);
  --brand-blue: #1E40AF;
  --smart-green: #059669;
}

/* 整体布局 */
.summary-dashboard {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: var(--bg-slate);
  font-family: 'Inter', 'Microsoft YaHei', sans-serif;
  transition: background-color 0.3s ease;
}

/* 深色模式文本颜色 */
:root.dark .summary-dashboard {
  color: #E2E8F0;
}

:root.dark .sidebar-title,
:root.dark .welcome-title,
:root.dark .chart-title,
:root.dark .ai-title {
  color: #F7FAFC;
}

:root.dark .welcome-subtitle,
:root.dark .chart-subtitle,
:root.dark .ai-content p {
  color: #A0AEC0;
}

/* AI 智能总结输入框样式 */
.ai-summary-section {
  background-color: var(--white);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-soft);
}

.ai-input-container {
  margin-top: 16px;
}

.ai-summary-input-wrapper {
  position: relative;
  width: 100%;
}

.ai-summary-input {
  width: 100%;
  min-height: 120px;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.3s ease;
  background-color: var(--white);
  color: #2d3748;
}

.ai-summary-input:focus {
  outline: none;
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 3px rgba(42, 92, 170, 0.1);
}

.ai-input-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.ai-btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: var(--brand-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ai-btn-primary:hover {
  background-color: #1e40af;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(42, 92, 170, 0.2);
}

.ai-btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ai-btn-secondary:hover {
  background-color: #edf2f7;
  border-color: #cbd5e0;
}

/* 拖拽上传样式 */
.ai-summary-input-wrapper.drag-over .ai-summary-input {
  border-color: var(--smart-green);
  box-shadow: 0 0 0 3px rgba(0, 166, 118, 0.1);
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 166, 118, 0.9);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 600;
  z-index: 10;
  animation: fadeIn 0.3s ease;
}

.drag-overlay p {
  margin-top: 12px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 深色模式下的AI输入框样式 */
:root.dark .ai-summary-input {
  background-color: #2d3748;
  border-color: #4a5568;
  color: #e2e8f0;
}

:root.dark .ai-summary-input:focus {
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.3);
}

:root.dark .ai-btn-secondary {
  background-color: #2d3748;
  color: #e2e8f0;
  border-color: #4a5568;
}

:root.dark .ai-btn-secondary:hover {
  background-color: #4a5568;
  border-color: #718096;
}

/* 骨架屏样式 */
.skeleton-container {
  padding: 0 24px;
}

.skeleton-welcome {
  margin-bottom: 24px;
}

.skeleton-title {
  width: 30%;
  height: 32px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 8px;
}

.skeleton-subtitle {
  width: 60%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.skeleton-kpi-card {
  height: 120px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
}

.skeleton-main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.skeleton-chart-card {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
  padding: 24px;
}

.skeleton-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.skeleton-chart-title {
  width: 40%;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-chart-select {
  width: 20%;
  height: 32px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.skeleton-chart-container {
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.skeleton-ai-dashboard {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
  padding: 24px;
}

.skeleton-ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-ai-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.skeleton-ai-title {
  width: 70%;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-ai-content {
  margin-bottom: 24px;
}

.skeleton-ai-content::before {
  content: '';
  display: block;
  height: 120px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.skeleton-ai-button {
  width: 100%;
  height: 48px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.skeleton-ai-summary {
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
  margin-bottom: 24px;
}

.skeleton-table {
  height: 400px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 深色模式下的骨架屏 */
:root.dark .skeleton-title,
:root.dark .skeleton-subtitle,
:root.dark .skeleton-kpi-card,
:root.dark .skeleton-chart-card,
:root.dark .skeleton-chart-title,
:root.dark .skeleton-chart-select,
:root.dark .skeleton-chart-container,
:root.dark .skeleton-ai-dashboard,
:root.dark .skeleton-ai-icon,
:root.dark .skeleton-ai-title,
:root.dark .skeleton-ai-content::before,
:root.dark .skeleton-ai-button,
:root.dark .skeleton-ai-summary,
:root.dark .skeleton-table {
  background: linear-gradient(90deg, #2d3748 25%, #4a5568 50%, #2d3748 75%);
  background-size: 200% 100%;
}

/* 左侧侧边栏 */
.sidebar {
  width: 256px;
  background-color: var(--white);
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.sidebar-header {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 40px;
  height: 40px;
  background-color: var(--brand-blue);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(42, 92, 170, 0.2);
}

.sidebar-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.sidebar-nav {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  color: #64748b;
  font-weight: 500;
  transition: all 0.2s ease;
  text-decoration: none;
}

.nav-item:hover {
  background-color: #f1f5f9;
  color: #334155;
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(42, 92, 170, 0.1) 0%, rgba(42, 92, 170, 0) 100%);
  border-right: 4px solid var(--brand-blue);
  color: var(--brand-blue);
}

.nav-divider {
  margin: 16px 0;
  padding: 0 16px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-footer {
  padding: 24px;
  border-top: 1px solid #e2e8f0;
}

.storage-info {
  background-color: #f8fafc;
  border-radius: 16px;
  padding: 16px;
}

.storage-label {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 8px;
}

.storage-bar {
  width: 100%;
  height: 6px;
  background-color: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.storage-progress {
  height: 100%;
  background-color: var(--brand-blue);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.storage-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #334155;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  height: 64px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-btn {
  padding: 8px;
  background-color: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: none;
}

.menu-btn:hover {
  background-color: #f1f5f9;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 384px;
  padding: 8px 16px 8px 40px;
  background-color: #f1f5f9;
  border: 2px solid transparent;
  border-radius: 16px;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  background-color: var(--white);
  border-color: var(--brand-blue);
  box-shadow: 0 0 0 4px rgba(42, 92, 170, 0.1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-btn {
  position: relative;
  padding: 8px;
  background-color: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: #64748b;
}

.notification-btn:hover {
  background-color: #f1f5f9;
}

.notification-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  border: 2px solid white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  text-align: right;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
}

.user-role {
  font-size: 0.75rem;
  color: #64748b;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 内容滚动区 */
.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}

.welcome-section {
  margin-bottom: 32px;
}

.welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.welcome-subtitle {
  color: #64748b;
}

/* KPI 卡片 */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.kpi-card {
  background-color: var(--white);
  padding: 24px;
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  border: 1px solid #e2e8f0;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.kpi-icon.blue {
  background-color: #eff6ff;
  color: var(--brand-blue);
}

.kpi-icon.green {
  background-color: #f0fdf4;
  color: var(--smart-green);
}

.kpi-icon.amber {
  background-color: #fffbeb;
  color: #f59e0b;
}

.kpi-icon.purple {
  background-color: #faf5ff;
  color: #9333ea;
}

.kpi-trend {
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.kpi-trend.positive {
  color: #10b981;
}

.kpi-trend.negative {
  color: #ef4444;
}

.kpi-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

/* 主图表与 AI 看板 */
.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.chart-card {
  background-color: var(--white);
  padding: 32px;
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
  border: 1px solid #e2e8f0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.chart-subtitle {
  font-size: 0.875rem;
  color: #64748b;
}

.chart-select {
  padding: 8px 16px;
  background-color: #f1f5f9;
  border: none;
  border-radius: 12px;
  font-size: 0.875rem;
  color: #374151;
  outline: none;
  cursor: pointer;
}

.chart-container {
  height: 320px;
}

/* AI 智能看板 */
.ai-dashboard {
  background: linear-gradient(135deg, var(--brand-blue) 0%, #1e4682 100%);
  padding: 32px;
  border-radius: 24px;
  color: white;
  box-shadow: 0 12px 40px rgba(42, 92, 170, 0.3);
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.ai-title {
  font-size: 1.125rem;
  font-weight: 700;
}

.ai-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.ai-card {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 16px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.ai-label {
  font-size: 0.75rem;
  color: #bfdbfe;
  margin-bottom: 4px;
}

.ai-text {
  font-size: 0.875rem;
  line-height: 1.6;
}

.ai-button {
  width: 100%;
  padding: 12px;
  background-color: #059669;
  color: white;
  border: none;
  border-radius: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.ai-button:hover {
  background-color: #047857;
}

/* 数据表格 */
.table-card {
  background-color: var(--white);
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-header {
  padding: 32px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.table-subtitle {
  font-size: 0.875rem;
  color: #64748b;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 10px 20px;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.action-btn.primary {
  background-color: var(--brand-blue);
  color: white;
}

.action-btn.primary:hover {
  background-color: #234d8f;
}

.action-btn.secondary {
  background-color: #f1f5f9;
  color: #475569;
}

.action-btn.secondary:hover {
  background-color: #e2e8f0;
}

.action-btn.minimal {
  padding: 8px;
  background-color: transparent;
  color: #94a3b8;
  border-radius: 8px;
}

.action-btn.minimal:hover {
  background-color: #f1f5f9;
  color: #64748b;
}

/* 表格内容 */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background-color: rgba(241, 245, 249, 0.5);
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table th {
  padding: 16px 32px;
  text-align: left;
}

.data-table tbody {
  border-top: 1px solid #e2e8f0;
}

.table-row {
  border-bottom: 1px solid #e2e8f0;
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background-color: rgba(241, 245, 249, 0.5);
}

.data-table td {
  padding: 16px 32px;
  color: #374151;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.file-icon.red {
  background-color: #fef2f2;
  color: #ef4444;
}

.file-icon.blue {
  background-color: #eff6ff;
  color: var(--brand-blue);
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-weight: 600;
  color: #1e293b;
}

.file-size {
  font-size: 0.75rem;
  color: #64748b;
}

/* 状态和优先级标签 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.green {
  background-color: #f0fdf4;
  color: #16a34a;
}

.status-badge.amber {
  background-color: #fffbeb;
  color: #d97706;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-dot.green {
  background-color: #10b981;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
}

.priority-badge.high {
  background-color: #fef2f2;
  color: #dc2626;
}

.priority-badge.medium {
  background-color: #fef3c7;
  color: #d97706;
}

.priority-badge.low {
  background-color: #f3f4f6;
  color: #6b7280;
}

/* 表格页脚 */
.table-footer {
  padding: 24px;
  background-color: rgba(241, 245, 249, 0.5);
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  font-size: 0.875rem;
  color: #64748b;
}

.pagination {
  display: flex;
  gap: 8px;
}

.pagination-btn {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  background-color: var(--white);
  color: #64748b;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover {
  background-color: #f1f5f9;
}

.pagination-btn.active {
  background-color: var(--brand-blue);
  color: white;
  border-color: var(--brand-blue);
}

.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 右侧动态侧边栏 */
.context-bar {
  width: 320px;
  background-color: var(--white);
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.context-header {
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.context-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.context-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.context-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
}

.section-action {
  font-size: 0.75rem;
  color: var(--brand-blue);
  cursor: pointer;
  text-decoration: underline;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-avatar {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.member-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid white;
}

.member-status.online {
  background-color: #10b981;
}

.member-status.offline {
  background-color: #9ca3af;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
}

.member-status-text {
  font-size: 0.6875rem;
  color: #6b7280;
}

.context-divider {
  height: 1px;
  background-color: #e2e8f0;
  margin: 24px 0;
}

/* AI 建议区 */
.ai-suggestion {
  background-color: rgba(239, 246, 255, 0.5);
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #bfdbfe;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--brand-blue);
  font-weight: 600;
  font-size: 0.75rem;
  margin-bottom: 8px;
}

.suggestion-text {
  font-size: 0.75rem;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 12px;
}

.suggestion-action {
  font-size: 0.75rem;
  color: var(--brand-blue);
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

/* 待办清单 */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.todo-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
}

.todo-text {
  font-size: 0.75rem;
  color: #374151;
  transition: all 0.2s ease;
}

.todo-text.completed {
  text-decoration: line-through;
  color: #9ca3af;
}

/* 侧边栏页脚 */
.context-footer {
  padding: 24px;
  border-top: 1px solid #e2e8f0;
}

.footer-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: #6b7280;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .context-bar {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }
  
  .sidebar-title {
    display: none;
  }
  
  .nav-item span:last-child {
    display: none;
  }
  
  .nav-divider {
    display: none;
  }
  
  .top-header {
    padding: 0 16px;
  }
  
  .search-input {
    width: 240px;
  }
  
  .content-scroll {
    padding: 16px;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .menu-btn {
    display: block;
  }
  
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 50;
    transform: translateX(-100%);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .search-input {
    width: 200px;
  }
}
</style>