<template>
    <el-container>
        <!--侧边栏-->
        <el-aside :style="{ width: isCollapese ? '0px' : '260px' }">
            <!-- 侧边栏完整内容 -->
            <div v-if="!isCollapese" class="sidebar-inner">
                <!-- 顶部：logo + 折叠 + 新对话 -->
                <div class="sidebar-top">
                    <div class="sidebar-header">
                        <div class="logo">DeepCoke</div>
                        <button class="icon-btn" @click="toggleCollapse" title="收起侧边栏">
                            <i class="el-icon-s-fold"></i>
                        </button>
                    </div>
                    <button class="new-chat-btn" @click="startNewChat">
                        <i class="el-icon-plus"></i>
                        <span>新对话</span>
                    </button>
                </div>

                <!-- 历史对话记录 -->
                <div class="chat-history">
                    <div
                      v-for="session in chatSessions"
                      :key="session.session_id"
                      class="chat-item"
                      :class="{ active: sessionId === session.session_id }"
                      @click="selectSession(session.session_id)"
                    >
                        <span class="chat-title">{{ session.title }}</span>
                        <el-dropdown trigger="click" @command="handleMenuCommand($event, session.session_id)">
                            <span class="chat-menu-btn" @click.stop><i class="el-icon-more"></i></span>
                            <el-dropdown-menu slot="dropdown">
                                <el-dropdown-item command="rename">重命名</el-dropdown-item>
                                <el-dropdown-item command="delete">删除</el-dropdown-item>
                            </el-dropdown-menu>
                        </el-dropdown>
                    </div>
                </div>
            </div>
        </el-aside>

        <!--右侧内容主体区域-->
        <el-main>
            <!-- 顶栏 -->
            <div class="top-bar">
                <button v-if="isCollapese" class="icon-btn" @click="toggleCollapse" title="展开侧边栏">
                    <i class="el-icon-s-unfold"></i>
                </button>
                <div class="top-bar-right">
                    <button class="voice-top-btn" @click="goVoiceChat">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                            <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/>
                        </svg>
                        <span>语音对话</span>
                    </button>
                </div>
            </div>
            <router-view :sessionId="sessionId" :isCollapese="isCollapese" @update-sessions="fetchChatSessions"></router-view>
        </el-main>
    </el-container>
</template>

<script>

export default {
  data () {
    return {
      isCollapese: false,
      chatSessions: [],
      sessionId: '',
      userId: 'user123',
      apiBaseUrl: 'http://127.0.0.1:8000'
    }
  },
  methods: {
    toggleCollapse () {
      this.isCollapese = !this.isCollapese
    },
    async startNewChat () {
      try {
        const response = await fetch(`${this.apiBaseUrl}/new_session/?user_id=${this.userId}`, {
          method: 'POST'
        })
        const data = await response.json()
        this.sessionId = data.session_id

        this.chatSessions.unshift({
          session_id: this.sessionId,
          title: '新对话'
        })

        if (this.$route.path !== `/Home/MainDia/${this.sessionId}`) {
          setTimeout(() => {
            this.$router.push({ path: `/Home/MainDia/${this.sessionId}` })
          }, 100)
        }
      } catch (error) {
        console.error('创建会话失败:', error)
      }
    },
    goVoiceChat () {
      this.$router.push('/Home/VoiceAgent')
    },
    async selectSession (sessionId) {
      this.sessionId = sessionId
      if (this.$route.params.sessionId !== sessionId) {
        this.$router.push(`/Home/MainDia/${sessionId}`)
      }
    },
    async fetchChatSessions () {
      try {
        const response = await fetch(`${this.apiBaseUrl}/user_sessions/?user_id=${this.userId}`)
        const data = await response.json()
        if (!Array.isArray(data)) return

        this.chatSessions = data.map(session => ({
          session_id: session.session_id,
          title: session.title || `对话 ${session.session_id.slice(0, 6)}`
        }))
      } catch (error) {
        console.error('加载历史会话失败:', error)
      }
    },
    async handleMenuCommand (command, sessionId) {
      if (command === 'rename') {
        this.renameSession(sessionId)
      } else if (command === 'delete') {
        this.deleteSession(sessionId)
      }
    },
    async renameSession (sessionId) {
      const newTitle = prompt('请输入新的会话名称:')
      if (!newTitle) return

      try {
        const response = await fetch(`${this.apiBaseUrl}/rename_session/?session_id=${sessionId}&new_title=${encodeURIComponent(newTitle)}`, {
          method: 'PUT'
        })

        if (response.ok) {
          const session = this.chatSessions.find(s => s.session_id === sessionId)
          if (session) session.title = newTitle
        }
      } catch (error) {
        console.error('网络错误:', error)
      }
    },
    async deleteSession (sessionId) {
      if (!confirm('确定要删除这个会话吗？')) return

      try {
        const response = await fetch(`${this.apiBaseUrl}/delete_session/?session_id=${sessionId}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          this.chatSessions = this.chatSessions.filter(s => s.session_id !== sessionId)

          if (this.sessionId === sessionId) {
            this.sessionId = this.chatSessions.length > 0 ? this.chatSessions[0].session_id : ''
          }
        }
      } catch (error) {
        console.error('网络错误:', error)
      }
    }
  },
  mounted () {
    this.fetchChatSessions()
  }
}
</script>

<style lang="less" scoped>

/* ===== 布局 ===== */
.el-container {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100vh;
}

/* ===== 侧边栏（深色科技风） ===== */
.el-aside {
  background: #171717;
  width: 260px;
  position: relative;
  height: 100vh;
  transition: width 0.2s ease;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 260px;
}

.sidebar-top {
  padding: 12px;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 4px 0;
}

.logo {
  font-family: 'Orbitron', sans-serif;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(90deg, #ff8a00, #149efa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ===== 通用图标按钮 ===== */
.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  font-size: 18px;
  flex-shrink: 0;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* ===== 新对话按钮 ===== */
.new-chat-btn {
  width: 100%;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  background: transparent;
  color: #e0e0e0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  cursor: pointer;
  transition: all 0.15s;
}

.new-chat-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.25);
}

.new-chat-btn i {
  font-size: 14px;
  opacity: 0.7;
}

/* ===== 历史记录 ===== */
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 8px 8px;
}

.chat-history::-webkit-scrollbar {
  width: 4px;
}

.chat-history::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.chat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  margin: 1px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s;
}

.chat-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.chat-item.active {
  background: rgba(255, 255, 255, 0.1);
}

.chat-title {
  flex: 1;
  font-size: 13px;
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
}

.chat-item.active .chat-title {
  color: #fff;
}

.chat-menu-btn {
  opacity: 0;
  color: #888;
  font-size: 14px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.12s;
  cursor: pointer;
  flex-shrink: 0;
}

.chat-item:hover .chat-menu-btn {
  opacity: 1;
}

.chat-menu-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

/* ===== 右侧主体 ===== */
.el-main {
  background: #212121;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  padding: 0;
  position: relative;
}

/* ===== 顶栏 ===== */
.top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 100;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.voice-top-btn {
  height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  background: transparent;
  color: #ccc;
  font-size: 13px;
  padding: 0 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.voice-top-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.25);
}

.voice-top-btn svg {
  opacity: 0.7;
}

</style>
