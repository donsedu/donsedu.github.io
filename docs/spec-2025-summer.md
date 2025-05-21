# 2025 AI創意無限營 Landing Page 開發規格書

## 1. 專案概述

### 1.1 專案目標
設計並開發「2025 AI創意無限營」的官方Landing Page，以向目標用戶提供營隊的全面信息，並促進線上報名轉化。

### 1.2 目標受眾
- 主要：5-15歲孩童的家長，尤其是關注孩子未來競爭力的父母
- 次要：對AI創意教育感興趣的教育工作者和機構

### 1.3 核心功能
- 展示營隊介紹、特色、課程規劃
- 提供費用和報名信息
- 連接Google表單進行報名
- 自適應不同設備的響應式設計

## 2. 技術架構

### 2.1 使用技術
- **前端開發**：HTML5, CSS3, JavaScript (ES6+)
- **框架/庫**：
  - 未使用框架，純vanilla HTML/CSS/JS實現
  - Font Awesome 6.4.0 (圖標庫)
- **開發方法**：響應式設計，移動優先

### 2.2 第三方服務/整合
- **Google Forms**：用於報名表單 (`https://forms.gle/3UFymH4M7dm5n7uPA`)
- **CDN 資源**：
  - Font Awesome 6.4.0 (通過Cloudflare CDN)

### 2.3 文件結構
本項目是單頁應用，主要包含以下文件：
- `index.html`：主HTML文件
- 內部樣式表：嵌入在HTML中
- 內部JavaScript：嵌入在HTML底部
- 圖片資源：
  - `/images/generated-image.png`：主視覺圖片
  - `/images/core-image.png`：營隊介紹圖片
  - `/images/steps.png`：報名步驟示意圖
  - `/images/2025/Week-1.png` 到 `/images/2025/Week-9.png`：各梯次課程圖片

## 3. 用戶界面設計

### 3.1 設計理念
網站採用現代、清新的視覺風格，搭配高科技感元素，反映AI主題，同時保持親和力以吸引家長和孩子。使用藍色和粉色為主色調，象徵科技與創意的結合。

### 3.2 色彩方案
- **主色**：藍色 `#4b6cff`
- **次色**：粉色 `#ff6b8b`
- **強調色**：紫色 `#7c4dff`
- **中性色**：
  - 淺灰 `#f8f9fa`
  - 深灰 `#343a40`
- **功能色**：
  - 成功 `#28a745`

### 3.3 排版
- **主標題**：微軟正黑體，粗體，大小 3.2rem
- **次標題**：微軟正黑體，粗體，大小 2.5rem
- **內文**：微軟正黑體，標準，大小 1rem
- **行高**：1.6（適合中文閱讀）

### 3.4 響應式斷點
- **大螢幕**：992px以上
- **平板**：768px到991px
- **手機**：767px以下
- **小型手機**：480px以下

## 4. 組件詳細說明

### 4.1 導航欄 (Navbar)
- **位置**：頁面頂部，固定位置
- **內容**：品牌名稱、導航連結到各區段、報名按鈕
- **行為**：
  - 在大螢幕上水平展示所有選項
  - 在小螢幕上使用漢堡選單，點擊展開側邊導航
- **技術實現**：
  - CSS Flexbox布局
  - JavaScript控制漢堡選單的開關
  - 使用Font Awesome圖標增強視覺效果
- **CSS類**：`.navbar`, `.navbar-brand`, `.navbar-nav`, `.nav-item`, `.nav-link`, `.menu-toggle`
- **圖標**：
  - 品牌名稱：`fa-solid fa-robot`
  - 營隊介紹：`fa-solid fa-info-circle`
  - 營隊特色：`fa-solid fa-star`
  - 課程規劃：`fa-solid fa-book-open`
  - 費用資訊：`fa-solid fa-tags`
  - 注意事項：`fa-solid fa-exclamation-circle`
  - 立即報名：`fa-solid fa-user-plus`

### 4.2 主視覺區 (Hero Section)
- **位置**：導航欄下方，頁面最上方
- **內容**：營隊標題、簡短介紹、號召性用語按鈕、主視覺圖片
- **設計**：
  - 漸變背景
  - 左文右圖布局（在移動設備上變為上文下圖）
- **技術實現**：
  - Flexbox布局
  - 漸變背景使用CSS linear-gradient
  - 響應式圖片
- **CSS類**：`.hero`, `.hero-content`, `.hero-text`, `.hero-image`, `.hero-title`, `.hero-subtitle`, `.hero-btn`
- **圖片**：`/images/generated-image.png`

### 4.3 營隊介紹區塊
- **位置**：主視覺區下方
- **內容**：標題、多段營隊介紹文字、配圖
- **設計**：淺色背景、左文右圖布局
- **技術實現**：Flexbox布局
- **CSS類**：`.about`, `.about-content`, `.about-text`, `.about-image`

### 4.4 營隊特色區塊
- **位置**：營隊介紹下方
- **內容**：4個特色卡片，每個包含圖標、標題和描述
- **設計**：
  - 漸變背景
  - 網格布局的卡片
  - 懸停效果：卡片上移、陰影增強
- **技術實現**：
  - CSS Grid布局
  - Transform和box-shadow實現懸停效果
  - Font Awesome圖標
- **CSS類**：`.features`, `.features-grid`, `.feature-card`, `.feature-icon`, `.feature-title`
- **圖標**：
  - 小班制：`fa-solid fa-users`
  - 專業師資：`fa-solid fa-chalkboard-teacher`
  - 安心環境：`fa-solid fa-shield-alt`
  - 獨特主題：`fa-solid fa-lightbulb`

### 4.5 課程規劃區塊
- **位置**：營隊特色下方
- **內容**：9個課程卡片，每個包含圖片、標題、描述和日期資訊
- **設計**：
  - 白色背景
  - 網格布局
  - 卡片懸停效果：上移、圖片放大
- **技術實現**：
  - CSS Grid布局
  - Transform和overflow:hidden實現圖片放大效果
- **CSS類**：`.courses`, `.courses-grid`, `.course-card`, `.course-image`, `.course-content`, `.course-title`, `.course-desc`, `.course-date`
- **圖片**：
  - 第一梯次：`/images/2025/Week-1.png`
  - 第二梯次：`/images/2025/Week-2.png`
  - 第三梯次：`/images/2025/Week-3.png`
  - 第四梯次：`/images/2025/Week-4.png`
  - 第五梯次：`/images/2025/Week-5.png`
  - 第六梯次：`/images/2025/Week-6.png`
  - 第七梯次：`/images/2025/Week-7.png`
  - 第八梯次：`/images/2025/Week-8.png`
  - 第九梯次：`/images/2025/Week-9.png`

### 4.6 費用資訊區塊
- **位置**：課程規劃下方
- **內容**：2個價格卡片（四天半日營、五天半日營），每個包含標題、價格、特點和按鈕
- **設計**：
  - 漸變背景
  - 居中對齊的卡片
  - 早鳥優惠徽章
- **技術實現**：
  - Flexbox布局
  - 徽章使用絕對定位
- **CSS類**：`.pricing`, `.pricing-cards`, `.pricing-card`, `.pricing-header`, `.pricing-title`, `.pricing-price`, `.pricing-features`, `.pricing-badge`
- **費用方案**：
  - 四天半日營：4,250元（原價5,000元）
  - 五天半日營：5,300元（原價6,250元）
- **包含項目**：
  - 營期時間
  - 上課時間（09:00～12:30）
  - 專業師資授課
  - 小班制教學
  - 課程教材費用全包

### 4.7 注意事項區塊
- **位置**：費用資訊下方
- **內容**：分組的注意事項列表（權責說明、防疫須知、其他注意事項）
- **設計**：白色背景、淺色卡片
- **技術實現**：
  - 有序列表
  - 使用Font Awesome圖標增強可讀性
- **CSS類**：`.notices`, `.notices-content`, `.notices-group`, `.notices-title`, `.notices-list`, `.notices-item`, `.notices-highlight`
- **圖標**：
  - 列表項：`fa-solid fa-check-circle`
  - 防疫相關：`fa-solid fa-spray-can-sparkles`, `fa-solid fa-wind`, `fa-solid fa-hands-bubbles`, `fa-solid fa-thermometer`
  - 其他項目：`fa-solid fa-clock`, `fa-solid fa-cloud-rain`, `fa-solid fa-file-alt`, `fa-solid fa-exchange-alt`

### 4.8 報名表單區塊
- **位置**：注意事項下方
- **內容**：報名按鈕連結到Google表單，報名流程圖，3個功能說明卡片
- **設計**：
  - 漸變背景
  - 白色表單容器
  - 突出的藍色報名按鈕
- **技術實現**：
  - 外部連結到Google表單
  - 使用圖片展示報名流程
  - Grid布局的功能卡片
- **CSS類**：`.registration`, `.form-container`, `.google-form-container`, `.registration-process-image`, `.google-form-button`, `.form-features`
- **圖片**：`/images/steps.png`
- **圖標**：
  - 表單標題：`fa-solid fa-paper-plane`
  - 報名按鈕：`fa-solid fa-external-link-alt`
  - 功能卡片：`fa-solid fa-check-circle`, `fa-solid fa-envelope`, `fa-solid fa-shield-alt`

### 4.9 頁尾區塊
- **位置**：頁面底部
- **內容**：logo、簡短描述、社交媒體連結、聯絡資訊、營隊快速連結
- **設計**：深色背景、三欄布局
- **技術實現**：
  - Flexbox布局
  - Font Awesome社交媒體圖標
- **CSS類**：`.footer`, `.footer-container`, `.footer-column`, `.footer-logo`, `.footer-links`, `.footer-social`
- **圖標**：
  - Logo：`fa-solid fa-robot`
  - 社交媒體：`fa-brands fa-facebook-f`, `fa-brands fa-instagram`, `fa-brands fa-line`
  - 聯絡資訊：`fa-solid fa-phone`, `fa-brands fa-line`, `fa-solid fa-map-marker-alt`
- **聯絡資訊**：
  - 電話：(02) 7742-0040
  - LINE ID：@dons（連結：https://lin.ee/f7t7DtS）
  - 地址：新北市淡水區濱海路二段218號一樓
  - Facebook：https://www.facebook.com/DONS.education/
  - Instagram：https://www.instagram.com/dons.education/

### 4.10 回到頂部按鈕
- **位置**：右下角固定位置
- **內容**：上箭頭圖標
- **行為**：
  - 頁面滾動超過300px時顯示
  - 點擊後平滑滾動到頁面頂部
- **技術實現**：
  - 固定定位
  - JavaScript監聽滾動事件控制顯示/隱藏
  - 使用`scrollTo`API實現平滑滾動
- **CSS類**：`.back-to-top`
- **圖標**：`fa-solid fa-arrow-up`

## 5. JavaScript功能詳解

### 5.1 導航欄互動
```javascript
// 導航欄互動相關代碼
const menuToggle = document.querySelector('.menu-toggle');
const navbarNav = document.querySelector('.navbar-nav');
const overlay = document.querySelector('.overlay');
const navLinks = document.querySelectorAll('.nav-link');

// 漢堡選單點擊事件
menuToggle.addEventListener('click', () => {
    menuToggle.classList.toggle('active');
    navbarNav.classList.toggle('active');
    overlay.classList.toggle('active');
    document.body.classList.toggle('no-scroll');
});

// 背景遮罩點擊事件
overlay.addEventListener('click', () => {
    menuToggle.classList.remove('active');
    navbarNav.classList.remove('active');
    overlay.classList.remove('active');
    document.body.classList.remove('no-scroll');
});

// 導航項目點擊事件
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        menuToggle.classList.remove('active');
        navbarNav.classList.remove('active');
        overlay.classList.remove('active');
        document.body.classList.remove('no-scroll');
    });
});
```

### 5.2 平滑滾動
```javascript
// 平滑滾動效果
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if(targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if(targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 70,
                behavior: 'smooth'
            });
        }
    });
});
```

### 5.3 回到頂部按鈕
```javascript
// 回到頂部按鈕
const backToTopButton = document.querySelector('.back-to-top');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        backToTopButton.classList.add('active');
    } else {
        backToTopButton.classList.remove('active');
    }
});

backToTopButton.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});
```

### 5.4 報名按鈕點擊追蹤
```javascript
// 報名按鈕點擊事件追蹤
const formButton = document.querySelector('.google-form-button');
if (formButton) {
    formButton.addEventListener('click', function() {
        console.log('使用者點擊了報名按鈕');
        
        // 這裡可以添加GA或其他分析代碼來追蹤點擊事件
        // 例如: gtag('event', 'click', {'event_category': 'registration', 'event_label': 'form_button'});
    });
}
```

### 5.5 動畫效果
```javascript
// 動畫效果
const animateElements = document.querySelectorAll('.animate');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, {
    threshold: 0.1
});

animateElements.forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(30px)';
    element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(element);
});
```

## 6. 響應式設計詳解

### 6.1 大螢幕設計 (992px以上)
- 導航欄水平展示所有項目
- 主視覺區左文右圖布局
- 特色和課程區域使用網格布局，同時顯示多個卡片
- 價格卡片水平排列

### 6.2 平板設計 (768px-991px)
- 導航欄轉為漢堡選單
- 點擊漢堡選單展開側邊導航
- 主視覺文字和圖片堆疊排列
- 網格布局調整，每行顯示2-3個卡片
- 報名按鈕擴大尺寸

### 6.3 手機設計 (767px以下)
- 簡化的漢堡選單導航
- 單列布局，所有內容垂直堆疊
- 網格布局調整為單列
- 縮小標題字體尺寸
- 頁尾區域改為單列布局

### 6.4 小型手機特殊處理 (480px以下)
- 進一步縮小標題和內容字體
- 減少元素間距
- 價格卡片寬度100%
- 簡化部分視覺元素

## 7. 優化和性能

### 7.1 圖片優化
- 使用適當尺寸的圖片，避免過大文件
- 設置`max-width: 100%`確保圖片響應式
- 提供適當的alt文字，提高無障礙性

### 7.2 CSS優化
- 使用CSS變量定義主要顏色，便於維護
- 有序組織CSS規則，按組件分類
- 適當使用媒體查詢實現響應式設計

### 7.3 JavaScript優化
- 使用事件委託減少事件監聽器數量
- 使用IntersectionObserver實現高效的滾動動畫
- 將腳本放在頁面底部，不阻塞渲染

### 7.4 字體和圖標優化
- 使用系統默認字體棧，減少外部資源
- 使用Font Awesome CDN加載圖標，啟用緩存

## 8. 可擴展性和維護

### 8.1 未來功能擴展
- 可添加的功能模塊：
  - 教師團隊介紹區塊
  - 營隊分享和評價區塊
  - 常見問題FAQ區塊
  - 更詳細的課程內容頁面
  - 圖庫/視頻展示區

### 8.2 代碼維護建議
- 遵循命名規范，保持類名的語義化
- 繼續使用模塊化結構，便於更新單個區塊
- 未來考慮將CSS和JS分離到獨立文件
- 考慮引入簡單的構建流程，如使用Gulp進行資源壓縮

### 8.3 最佳實踐
- 定期檢查和更新第三方庫版本
- 持續進行設備兼容性測試
- 確保表單提交和GA追蹤正常工作
- 優化圖片加載速度和SEO策略

## 9. 技術限制和解決方案

### 9.1 CSP限制
**問題**：內容安全政策(CSP)限制可能阻止Google表單iframe的加載

**解決方案**：
- 使用直接連結到Google表單而非嵌入iframe
- 添加清晰的按鈕和視覺引導
- 提供報名流程圖片幫助用戶理解

### 9.2 跨瀏覽器兼容性
**問題**：不同瀏覽器對CSS功能的支持可能不同

**解決方案**：
- 使用廣泛支持的CSS屬性
- 為新特性提供回退方案
- 測試主流瀏覽器：Chrome, Firefox, Safari, Edge

### 9.3 移動設備多樣性
**問題**：需要適應各種尺寸和方向的移動設備

**解決方案**：
- 使用流體布局而非固定寬度
- 設置適當的視口設置
- 使用多個響應式斷點
- 使用相對單位(rem, %)而非絕對單位(px)

## 10. 開發和部署流程

### 10.1 本地開發環境
- 使用任意代碼編輯器(VSCode, Sublime, Cursor等)
- 使用Live Server或類似工具進行本地預覽
- 在多種瀏覽器和設備模擬器中測試

### 10.2 版本控制
- 推薦使用Git進行版本控制
- 創建有意義的提交信息
- 考慮使用分支進行功能開發

### 10.3 部署建議
- 使用任何靜態網站托管服務(GitHub Pages, Netlify, Vercel等)
- 確保設置正確的MIME類型
- 考慮啟用HTTPS
- 添加適當的緩存控制和內容壓縮

## 11. 後續開發建議

### 11.1 短期優化
- 添加網站favicon
- 完善SEO元標籤
- 添加結構化數據(Schema.org)
- 實現真實的GA追蹤代碼

### 11.2 中期擴展
- 開發活動倒計時功能
- 添加營隊照片輪播
- 開發簡單的營隊日程表展示
- 考慮添加多語言支持

### 11.3 長期計劃
- 開發完整的營隊管理系統
- 添加會員登錄和個人資料管理
- 整合線上付款功能
- 開發營隊活動回顧/記錄功能

---

## 附錄A: CSS變量定義

```css
:root {
    --primary: #4b6cff;     /* 主色 - 藍色 */
    --secondary: #ff6b8b;   /* 次色 - 粉色 */
    --accent: #7c4dff;      /* 強調色 - 紫色 */
    --light: #f8f9fa;       /* 淺色背景 */
    --dark: #343a40;        /* 深色文字/背景 */
    --success: #28a745;     /* 功能色 - 成功綠 */
}
```

## 附錄B: 區塊ID列表

- `#about` - 營隊介紹區塊
- `#features` - 營隊特色區塊
- `#courses` - 課程規劃區塊
- `#pricing` - 費用資訊區塊
- `#notices` - 注意事項區塊
- `#registration` - 報名表單區塊

## 附錄C: 外部資源

- Font Awesome 6.4.0: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`
- Google表單連結: `https://forms.gle/3UFymH4M7dm5n7uPA`
- 主視覺圖片: `/images/generated-image.png`
- 營隊介紹圖片: `/images/core-image.png`
- 報名流程圖: `/images/steps.png`
- 課程圖片: `/images/2025/Week-1.png` 到 `/images/2025/Week-9.png`