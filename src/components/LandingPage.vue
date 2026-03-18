<template>
  <div class="landing-container">
    <!-- 背景粒子（与登录页一致） -->
    <div class="particles-bg">
      <vue-particles class="login-bg" color="#AEAEAE" linesColor="#AEAEAE" :particlesNumber="150" shapeType="circle" clickMode="repulse" hoverMode="repulse"></vue-particles>
    </div>

    <!-- 顶部导航 -->
    <header class="landing-header">
      <div class="header-logo">DeepCoke</div>
      <div class="header-right">
        <span class="user-name">{{ userName }}</span>
        <el-button class="logout-btn" @click="logout">退出</el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="landing-main">
      <!-- 标题区 -->
      <section class="hero-section">
        <h1 class="hero-title">DeepCoke</h1>
        <p class="hero-subtitle">智能焦化决策平台</p>
        <p class="hero-desc">融合配煤优化、数字孪生、知识图谱与智能对话，为焦化全流程提供 AI 驱动的决策支持</p>
      </section>

      <!-- 四大产品卡片 -->
      <section class="products-section">
        <div class="product-card" v-for="product in products" :key="product.id">
          <div class="card-icon-wrapper" :style="{ background: product.gradient }">
            <i :class="product.icon" class="card-icon"></i>
          </div>
          <h3 class="card-title">{{ product.title }}</h3>
          <p class="card-desc">{{ product.desc }}</p>
          <div class="card-tags">
            <span class="tag" v-for="tag in product.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </section>

      <!-- 进入对话按钮 -->
      <section class="cta-section">
        <button class="cta-button" @click="enterChat">
          <i class="el-icon-chat-dot-round"></i>
          开始智能对话
        </button>
        <p class="cta-hint">输入您的焦化问题，DeepCoke 将自动调用合适的工具为您解答</p>
      </section>

      <!-- 能力概览 -->
      <section class="capabilities-section">
        <h2 class="section-title">您可以这样问</h2>
        <div class="examples-grid">
          <div class="example-item" v-for="example in examples" :key="example" @click="enterChatWithQuestion(example)">
            <i class="el-icon-right"></i>
            <span>{{ example }}</span>
          </div>
        </div>
      </section>
    </main>

    <!-- 底部 -->
    <footer class="landing-footer">
      <img class="footer-logo" src="../assets/imgs/CompanyLogo.png" alt="Logo" />
      <span class="footer-text">苏州龙泰氢一能源科技有限公司</span>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  data () {
    return {
      userName: window.sessionStorage.getItem('nickname') || window.sessionStorage.getItem('username') || 'user',
      products: [
        {
          id: 'blend',
          icon: 'el-icon-s-operation',
          title: '智能配煤',
          desc: '基于煤质指标与焦炭质量模型，AI 自动推算最优配煤方案，降低成本、稳定焦炭质量。',
          gradient: 'linear-gradient(135deg, #1a3a5c 0%, #2a6496 100%)',
          tags: ['配方优化', '成本控制', '质量预测']
        },
        {
          id: 'twin',
          icon: 'el-icon-monitor',
          title: '数字孪生',
          desc: '基于 UE5 构建的焦炉三维温度场可视化系统，实时监控炼焦过程工况与温度分布。',
          gradient: 'linear-gradient(135deg, #ff8a00 0%, #e06b10 100%)',
          tags: ['三维可视化', '温度场', '实时监控']
        },
        {
          id: 'chat',
          icon: 'el-icon-microphone',
          title: '智能对话',
          desc: '支持文字与语音交互，理解焦化领域专业问题，调用多种工具综合回答。',
          gradient: 'linear-gradient(135deg, #149efa 0%, #0d6efd 100%)',
          tags: ['语音识别', '多轮对话', '工具调度']
        },
        {
          id: 'knowledge',
          icon: 'el-icon-notebook-2',
          title: '知识图谱',
          desc: '基于焦化文献构建的专业知识库，回答附带文献来源引用，确保可溯源。',
          gradient: 'linear-gradient(135deg, #1a5c3a 0%, #28a06a 100%)',
          tags: ['文献检索', '知识问答', '来源引用']
        }
      ],
      examples: [
        '这批煤灰分12%、挥发分28%，如何配煤？',
        '焦炉温度场异常，可能的原因有哪些？',
        '配煤中肥煤比例过高会怎样？',
        '查看当前焦炉实时温度分布',
        '关于捣固焦工艺的文献有哪些？',
        '如何降低焦炭灰分同时保证强度？'
      ]
    }
  },
  methods: {
    enterChat () {
      this.$router.push({ name: 'MainDia', params: { sessionId: 'new' } })
    },
    enterChatWithQuestion (question) {
      this.$router.push({
        name: 'MainDia',
        params: { sessionId: 'new' },
        query: { q: question }
      })
    },
    logout () {
      window.sessionStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style lang="less" scoped>
.landing-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #132240 40%, #1a1a2e 100%);
  position: relative;
  overflow-x: hidden;
}

.particles-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* 顶部导航 */
.landing-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 48px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-logo {
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  font-weight: bold;
  background: linear-gradient(90deg, #ff8a00, #149efa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  color: rgba(255, 255, 255, 0.6) !important;
  font-size: 13px;
  border-radius: 8px;
  padding: 6px 16px;
  transition: all 0.2s;
  &:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    color: #fff !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
  }
}

/* 主内容 */
.landing-main {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 100px 32px 60px;
}

/* 标题区 */
.hero-section {
  text-align: center;
  padding: 60px 0 40px;
}

.hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 72px;
  font-weight: 900;
  background: linear-gradient(90deg, #ff8a00, #149efa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 12px;
  letter-spacing: 4px;
}

.hero-subtitle {
  font-size: 28px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 300;
  margin: 0 0 16px;
  letter-spacing: 8px;
}

.hero-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.8;
}

/* 产品卡片 */
.products-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 40px 0;
}

.product-card {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: default;

  &:hover {
    transform: translateY(-6px);
    background: rgba(0, 0, 0, 0.45);
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  }
}

.card-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.card-icon {
  font-size: 28px;
  color: #fff;
}

.card-title {
  font-size: 18px;
  color: #fff;
  margin: 0 0 12px;
  font-weight: 600;
}

.card-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.7;
  margin: 0 0 16px;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
}

.tag {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.65);
  background: rgba(255, 255, 255, 0.1);
  padding: 3px 10px;
  border-radius: 20px;
}

/* CTA 按钮 */
.cta-section {
  text-align: center;
  padding: 20px 0 40px;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 48px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(90deg, #ff8a00, #149efa);
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(20, 158, 250, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(20, 158, 250, 0.45);
  }

  &:active {
    transform: translateY(0);
  }

  i {
    font-size: 22px;
  }
}

.cta-hint {
  margin-top: 16px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

/* 示例问题 */
.capabilities-section {
  padding: 20px 0 60px;
}

.section-title {
  text-align: center;
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
  margin: 0 0 28px;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.example-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.4);
    color: rgba(255, 255, 255, 0.9);
    border-color: rgba(255, 255, 255, 0.18);
  }

  i {
    color: #ff8a00;
    font-size: 14px;
    flex-shrink: 0;
  }
}

/* 底部 */
.landing-footer {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-logo {
  width: 140px;
  height: auto;
  margin-bottom: 8px;
  opacity: 0.7;
}

.footer-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 响应式 */
@media (max-width: 900px) {
  .products-section {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero-title {
    font-size: 48px;
  }
}

@media (max-width: 600px) {
  .products-section {
    grid-template-columns: 1fr;
  }
  .examples-grid {
    grid-template-columns: 1fr;
  }
}
</style>
