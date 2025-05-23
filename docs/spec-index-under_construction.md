# 網站施工中頁面規格文件

## 頁面概述
這是一個臨時的「網站施工中」頁面，用於在網站改版期間向訪客展示。頁面採用簡潔的設計風格，提供基本的聯絡資訊和社群媒體連結。

## 技術規格

### 基本設定
- 文件類型：HTML5
- 語言：繁體中文 (zh-TW)
- 字體：微軟正黑體
- 響應式設計：支援所有裝置尺寸

### 外部資源
- Font Awesome 6.4.0 (CDN)
  ```html
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  ```

### 顏色方案
```css
:root {
    --primary: #4b6cff;    /* 品牌主色 */
    --secondary: #ff6b8b;  /* 次要色 */
    --accent: #7c4dff;     /* 強調色 */
    --light: #f8f9fa;      /* 淺色背景 */
    --dark: #343a40;       /* 深色文字 */
}
```

### 背景設計
- 使用漸層背景
```css
background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
```

### 主要元件規格

#### 1. 施工圖示
- 使用 Font Awesome 的 `fa-tools` 圖示
- 尺寸：120px x 120px（桌面版）
- 尺寸：100px x 100px（行動版）
- 顏色：品牌主色 (#4b6cff)

#### 2. 標題文字
- 主標題：「網站施工中」
- 副標題：「我們正在為您打造更好的體驗」
- 說明文字：「請稍後再來拜訪，或透過以下社群媒體與我們聯繫。」

#### 3. 社群媒體連結
- 圖示尺寸：50px x 50px
- 圖示間距：1rem
- 懸停效果：
  - 背景色：rgba(75, 108, 255, 0.1)
  - 上浮動畫：translateY(-3px)
  - 品牌顏色：
    - Facebook: #1877f2
    - Instagram: #000
    - LINE: #00B900

#### 4. LINE ID 顯示
- 位置：社群媒體連結下方
- 樣式：上方有分隔線
- 連結：https://lin.ee/UehPUuy
- 顏色：LINE 品牌綠色 (#00B900)

### 響應式設計斷點
```css
@media (max-width: 768px) {
    /* 容器調整 */
    .construction-container {
        margin: 1rem;
        padding: 1.5rem;
    }
    
    /* 文字大小調整 */
    .construction-title {
        font-size: 2rem;
    }
    .construction-subtitle {
        font-size: 1.1rem;
    }
    .construction-text {
        font-size: 1rem;
    }
    
    /* 圖示大小調整 */
    .construction-icon {
        width: 100px;
        height: 100px;
    }
}
```

### 動畫效果
- 無特殊動畫效果
- 僅保留社群媒體圖示的懸停動畫

### 效能考量
- 使用 CDN 載入 Font Awesome
- 最小化 CSS 內嵌
- 無 JavaScript 依賴

### 無障礙設計
- 所有圖片都有 alt 文字
- 社群媒體連結有適當的 target="_blank" 屬性
- 顏色對比度符合 WCAG 標準

## 維護注意事項
1. 定期檢查社群媒體連結是否有效
2. 確保 Font Awesome CDN 連結保持最新
3. 監控頁面載入效能
4. 定期更新施工狀態資訊 