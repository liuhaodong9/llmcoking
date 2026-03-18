<template>
  <div class="chat-wrapper">
    <!-- 聊天内容区域 -->
    <div class="chat-scroll" ref="chatScroll">
      <div class="chat-content">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-row"
          :class="message.type"
          ref="lastMessage"
        >
          <!-- bot 头像 -->
          <div v-if="message.type === 'bot'" class="avatar bot-avatar">
            <img src="../assets/imgs/DeepCoke_logo.png" alt="DC" />
          </div>

          <div class="message-bubble">
            <span v-if="message.text" v-html="renderMarkdown(message.text)"></span>
            <div v-else-if="message.type === 'bot'" class="loading-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-wrapper">
        <!-- 隐藏文件选择器 -->
        <input
          ref="filePicker"
          type="file"
          multiple
          style="display:none"
          @change="onFilesSelected"
        />

        <!-- 附件按钮 -->
        <button class="input-icon-btn" @click="openFilePicker" title="添加文件">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M11 11V5h2v6h6v2h-6v6h-2v-6H5v-2z"/>
          </svg>
        </button>

        <el-input
          ref="inputBox"
          v-model="newMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 6 }"
          placeholder="给 DeepCoke 发送消息..."
          @keydown.enter.native.prevent="sendMessage"
          class="input-box"
        ></el-input>

        <!-- 听写按钮 -->
        <button
          class="input-icon-btn"
          :class="{ active: isDictating }"
          @click="toggleDictation"
          title="语音输入"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/>
          </svg>
        </button>

        <!-- 发送按钮 -->
        <button class="send-btn" :class="{ 'has-text': newMessage.trim() }" @click="sendMessage">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94l18.06-8.5a.75.75 0 0 0 0-1.38L3.478 2.405z"/>
          </svg>
        </button>
      </div>
      <div class="input-footer">内容由 AI 生成，请仔细甄别</div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import katex from 'katex'
import 'katex/dist/katex.min.css'

export default {
  props: ['sessionId', 'isCollapese'],
  data () {
    return {
      messages: [],
      newMessage: '',
      apiBaseUrl: 'http://127.0.0.1:8000',
      isUserScrolling: false,
      localSessionId: '',
      attachments: [],
      isDictating: false,
      voiceMode: false,
      recognition: null
    }
  },
  methods: {
    renderMarkdown (text) {
      let preprocessed = text
        .replace(/\s*<br\s*\/?>\s*/gi, '\n\n')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      preprocessed = preprocessed
        .replace(/\$\$(.*?)\$\$/gs, (_, equation) => {
          return katex.renderToString(equation.trim(), {
            throwOnError: false,
            displayMode: true
          })
        })
        .replace(/(^|[^\d])\$(\S+?)\$(?!\d)/g, (_, before, equation) => {
          return before + katex.renderToString(equation.trim(), {
            throwOnError: false,
            displayMode: false
          })
        })

      const html = marked(preprocessed, {
        breaks: true,
        gfm: true,
        highlight: function (code, lang) {
          const language = hljs.getLanguage(lang) ? lang : 'plaintext'
          return hljs.highlight(code, { language }).value
        }
      })

      return html
    },
    scrollToBottom () {
      this.$nextTick(() => {
        const el = this.$refs.chatScroll
        if (el) el.scrollTop = el.scrollHeight
      })
    },
    openFilePicker () {
      if (this.$refs.filePicker) this.$refs.filePicker.click()
    },
    onFilesSelected (e) {
      const files = Array.from(e.target.files || [])
      if (!files.length) return
      this.attachments.push(...files)
      const names = files.map(f => f.name).join('、')
      this.$message && this.$message.success(`已选择 ${files.length} 个文件：${names}`)
      e.target.value = ''
    },
    toggleDictation () {
      if (this.isDictating) {
        if (this.recognition) this.recognition.stop()
        this.isDictating = false
        return
      }
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!SR) {
        this.$message && this.$message.warning('当前浏览器不支持语音输入')
        return
      }
      this.recognition = new SR()
      this.recognition.lang = 'zh-CN'
      this.recognition.continuous = true
      this.recognition.interimResults = true

      this.recognition.onstart = () => { this.isDictating = true }
      this.recognition.onresult = (event) => {
        let txt = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          txt += event.results[i][0].transcript
        }
        if (txt) this.newMessage = (this.newMessage + ' ' + txt).trim()
      }
      this.recognition.onerror = () => { this.isDictating = false }
      this.recognition.onend = () => { this.isDictating = false }
      this.recognition.start()
    },
    toggleVoiceMode () {
      this.voiceMode = !this.voiceMode
      if (!this.voiceMode) window.speechSynthesis.cancel()
    },
    speak (text) {
      if (!this.voiceMode || !window.speechSynthesis) return
      const u = new SpeechSynthesisUtterance(text)
      u.lang = 'zh-CN'
      window.speechSynthesis.cancel()
      window.speechSynthesis.speak(u)
    },
    async sendMessage () {
      if (!this.newMessage.trim()) return
      const userText = this.newMessage
      this.newMessage = ''
      this.messages.push({ text: userText, type: 'user' })

      const botMessage = { text: '', type: 'bot' }
      this.messages.push(botMessage)
      this.scrollToBottom()

      let sessionToUse = this.sessionId
      if (this.sessionId === 'new') {
        try {
          const response = await fetch(`${this.apiBaseUrl}/new_session/?user_id=user123`, { method: 'POST' })
          const data = await response.json()
          this.localSessionId = data.session_id
          this.$emit('update-sessions')
          sessionToUse = this.localSessionId
        } catch (error) {
          console.error('创建新会话失败:', error)
          return
        }
      }

      try {
        const response = await fetch(
          `${this.apiBaseUrl}/chat/?session_id=${sessionToUse}&user_message=${encodeURIComponent(userText)}`,
          { method: 'POST' }
        )
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let botReply = ''

        while (true) {
          const { value, done } = await reader.read()
          if (done) break
          botReply += decoder.decode(value, { stream: true })
          botMessage.text = botReply
          this.$nextTick(() => this.scrollToBottom())
        }

        if (this.voiceMode && botReply.trim()) this.speak(botReply)
      } catch (error) {
        console.error('发送消息失败:', error)
        this.streamReply(botMessage, '对不起，网络异常，请稍后再试。')
      }

      this.attachments = []
      this.scrollToBottom()
    },
    async loadChatHistory () {
      if (!this.sessionId) return
      try {
        const response = await fetch(`${this.apiBaseUrl}/messages/?session_id=${this.sessionId}`)
        const data = await response.json()
        this.messages = data
          .filter(msg => msg.type !== 'user' || msg.text.trim() !== '')
          .map(msg => ({ text: msg.text, type: msg.type }))
        if (this.sessionId === 'new') {
          this.streamWelcomeMessage()
        }
        this.scrollToBottom()
      } catch (error) {
        console.error('加载聊天记录失败:', error)
      }
    },
    streamReply (botMessage, fullText) {
      let i = 0
      const interval = setInterval(() => {
        if (i < fullText.length) {
          botMessage.text += fullText[i]
          i++
        } else {
          clearInterval(interval)
        }
      }, 50)
    },
    streamWelcomeMessage () {
      const botMessage = { text: '', type: 'bot' }
      this.messages.push(botMessage)
      this.streamReply(botMessage, '您好！我是焦化大语言智能问答与分析系统DeepCoke，有什么可以帮助你的？')
    }
  },
  watch: {
    sessionId () {
      this.loadChatHistory()
    },
    messages () {
      this.scrollToBottom()
    }
  },
  mounted () {
    if (this.sessionId === 'new') {
      const botMessage = { text: '', type: 'bot' }
      this.messages.push(botMessage)
      this.streamReply(botMessage, '您好！我是焦化大语言智能问答与分析系统DeepCoke，有什么可以帮助你的？')
    } else {
      this.loadChatHistory()
    }
  }
}
</script>

<style scoped>
/* ===== 整体布局 ===== */
.chat-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #212121;
}

/* ===== 消息滚动区 ===== */
.chat-scroll {
  flex: 1;
  overflow-y: auto;
  padding-top: 56px;
}

.chat-scroll::-webkit-scrollbar {
  width: 6px;
}

.chat-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
}

.chat-content {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 24px 24px;
}

/* ===== 消息行 ===== */
.message-row {
  display: flex;
  gap: 14px;
  margin: 20px 0;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

/* ===== 头像 ===== */
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.bot-avatar {
  background: linear-gradient(135deg, #ff8a00, #149efa);
  display: flex;
  align-items: center;
  justify-content: center;
}

.bot-avatar img {
  width: 24px;
  height: 24px;
  object-fit: contain;
  filter: brightness(10);
}

/* ===== 消息气泡 ===== */
.message-bubble {
  max-width: 85%;
  font-size: 15px;
  line-height: 1.7;
  word-wrap: break-word;
  text-align: left;
}

.message-row.bot .message-bubble {
  color: #e0e0e0;
  padding: 0;
}

.message-row.user .message-bubble {
  background: #2f2f2f;
  color: #e0e0e0;
  padding: 12px 18px;
  border-radius: 18px 18px 4px 18px;
}

/* ===== Markdown 内容样式 ===== */
.message-bubble span { word-break: break-word; }

::v-deep .message-bubble h1 { font-size: 20px; font-weight: 600; color: #fff; margin: 16px 0 8px; }
::v-deep .message-bubble h2 { font-size: 18px; font-weight: 600; color: #fff; margin: 14px 0 6px; }
::v-deep .message-bubble h3 { font-size: 16px; font-weight: 600; color: #fff; margin: 12px 0 4px; }
::v-deep .message-bubble p { margin: 8px 0; }
::v-deep .message-bubble ul,
::v-deep .message-bubble ol { padding-left: 20px; margin: 8px 0; }
::v-deep .message-bubble code {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #e8ab6a;
}
::v-deep .message-bubble pre {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 14px;
  margin: 10px 0;
  overflow-x: auto;
}
::v-deep .message-bubble pre code {
  background: transparent;
  padding: 0;
  color: #e0e0e0;
}
::v-deep .message-bubble a { color: #58a6ff; }
::v-deep .message-bubble table {
  border-collapse: collapse;
  margin: 10px 0;
  width: 100%;
}
::v-deep .message-bubble th,
::v-deep .message-bubble td {
  border: 1px solid #3a3a3a;
  padding: 8px 12px;
  text-align: left;
}
::v-deep .message-bubble th {
  background: #2a2a2a;
  color: #fff;
}

/* ===== 加载动画 ===== */
.loading-dots {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #666;
  animation: dots 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(1) { animation-delay: 0s; }
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dots {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* ===== 输入区域 ===== */
.input-area {
  flex-shrink: 0;
  padding: 0 24px 16px;
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  background: #2f2f2f;
  border: 1px solid #3a3a3a;
  border-radius: 24px;
  padding: 8px 8px 8px 4px;
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: #555;
}

/* ===== 输入框 ===== */
.input-box {
  flex: 1;
  font-size: 15px;
}

::v-deep .el-textarea__inner {
  border: none !important;
  border-radius: 0 !important;
  padding: 6px 8px;
  box-shadow: none !important;
  resize: none;
  font-family: "Microsoft YaHei", -apple-system, sans-serif;
  font-size: 15px;
  line-height: 1.5;
  background: transparent !important;
  color: #e0e0e0;
}

::v-deep .el-textarea__inner::placeholder {
  color: #666;
}

::v-deep .el-textarea__inner:focus {
  border: none !important;
  box-shadow: none !important;
}

/* ===== 输入框内图标按钮 ===== */
.input-icon-btn {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #888;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.input-icon-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ccc;
}

.input-icon-btn.active {
  color: #149efa;
  background: rgba(20, 158, 250, 0.15);
}

/* ===== 发送按钮 ===== */
.send-btn {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: #555;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: default;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn.has-text {
  background: #fff;
  color: #212121;
  cursor: pointer;
}

.send-btn.has-text:hover {
  background: #e0e0e0;
}

/* ===== 底部提示 ===== */
.input-footer {
  text-align: center;
  font-size: 12px;
  color: #555;
  padding-top: 8px;
}
</style>
