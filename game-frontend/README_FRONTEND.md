# 🎮 Number Duel - Frontend (React)

React 19 tabanlı modern, responsive web arayüzü.

---

## 📋 Özellikler

- ✅ **JWT Authentication** - Login/Register sayfaları
- ✅ **Token Management** - Otomatik yenileme ve interceptors
- ✅ **Real-time Game** - WebSocket entegrasyonu
- ✅ **Lobby System** - Oda listesi, oluşturma, katılma
- ✅ **Game Board** - Canlı oyun ekranı
- ✅ **Responsive Design** - Bootstrap 5 ile mobil uyumlu
- ✅ **Error Handling** - Kullanıcı dostu hata mesajları

---

## 🚀 Kurulum

```bash
# Dependencies yükle
npm install

# Development server başlat
npm start

# Production build
npm run build
```

---

## 📁 Dizin Yapısı

```
src/
├── pages/
│   ├── Login.js         # Giriş sayfası
│   ├── Register.js      # Kayıt sayfası
│   ├── Lobby.js         # Oda listesi ve oluşturma
│   └── GameBoard.js     # Oyun ekranı (WebSocket)
│
├── utils/
│   └── api.js           # Axios interceptors ve API fonksiyonları
│
├── App.js               # Ana router component
├── index.js             # Entry point
└── index.css            # Global styles
```

---

## 🔌 API Entegrasyonu

### API Base URL
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';
```

### Authentication API
```javascript
import { authAPI } from './utils/api';

// Login
const response = await authAPI.login(username, password);

// Register
const response = await authAPI.register(userData);

// Get Profile
const response = await authAPI.getProfile();

// Get Balance
const response = await authAPI.getBalance();
```

### Game API
```javascript
import { gameAPI } from './utils/api';

// Get Rooms
const response = await gameAPI.getRooms();

// Create Room
const response = await gameAPI.createRoom({ name, bet_amount });

// Join Room
const response = await gameAPI.joinRoom(roomId);

// Get Transactions
const response = await gameAPI.getTransactions();
```

---

## 🌐 WebSocket Kullanımı

```javascript
import useWebSocket from 'react-use-websocket';

const { sendJsonMessage, lastMessage, readyState } = useWebSocket(
    `ws://127.0.0.1:8000/ws/game/${roomId}/`,
    {
        shouldReconnect: () => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
    }
);

// Mesaj gönder
sendJsonMessage({ action: 'guess', number: 50 });

// Mesaj al
useEffect(() => {
    if (lastMessage !== null) {
        const data = JSON.parse(lastMessage.data);
        console.log(data);
    }
}, [lastMessage]);
```

---

## 🎨 UI Components

### Bootstrap 5 Kullanımı

```javascript
import 'bootstrap/dist/css/bootstrap.min.css';

// Card
<div className="card">
    <div className="card-body">
        <h5 className="card-title">Başlık</h5>
        <p className="card-text">İçerik</p>
    </div>
</div>

// Button
<button className="btn btn-primary">Buton</button>

// Alert
<div className="alert alert-success">Başarılı!</div>
```

---

## 🔐 Token Yönetimi

### LocalStorage Kullanımı

```javascript
// Token kaydet
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);
localStorage.setItem('user_id', userId);

// Token oku
const token = localStorage.getItem('access_token');

// Token sil (logout)
localStorage.clear();
```

### Otomatik Token Yenileme

`utils/api.js` dosyasında axios interceptor kullanılarak token otomatik yenilenir:

```javascript
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Refresh token ile yeni access token al
            const newToken = await refreshAccessToken();
            // İsteği yeni token ile tekrar dene
        }
    }
);
```

---

## 📱 Sayfalar

### Login (/login)
- Kullanıcı girişi
- JWT token alımı
- Otomatik lobby'ye yönlendirme

### Register (/register)
- Yeni kullanıcı kaydı
- 1000 puan hediye
- Doğum tarihi validasyonu
- Şifre güçlendirme

### Lobby (/lobby)
- Aktif odaları listele
- Yeni oda oluştur
- Odaya katıl
- Bakiye gösterimi
- Otomatik yenileme (3 saniye)

### GameBoard (/game/:roomId)
- Real-time oyun ekranı
- Tahmin input'u
- Sıra göstergesi
- Oyun log'ları
- WebSocket bağlantı durumu

---

## 🐛 Hata Yönetimi

### API Hataları

```javascript
try {
    const response = await gameAPI.joinRoom(roomId);
} catch (err) {
    const errorMsg = err.response?.data?.error || 'Bir hata oluştu';
    alert(errorMsg);
}
```

### WebSocket Hataları

```javascript
const { readyState } = useWebSocket(url, {
    onError: (event) => {
        console.error('WebSocket error:', event);
    }
});
```

---

## 🎯 Environment Variables

`.env` dosyası oluştur:

```env
REACT_APP_API_URL=http://127.0.0.1:8000/api
REACT_APP_WS_URL=ws://127.0.0.1:8000/ws
```

Kullanımı:

```javascript
const apiUrl = process.env.REACT_APP_API_URL;
const wsUrl = process.env.REACT_APP_WS_URL;
```

---

## 🧪 Testing

```bash
# Test çalıştır
npm test

# Coverage raporu
npm test -- --coverage
```

---

## 📦 Production Build

```bash
# Build oluştur
npm run build

# Build dosyaları
ls build/
# static/  index.html  manifest.json  ...

# Nginx ile serve et
server {
    root /path/to/build;
    try_files $uri /index.html;
}
```

---

## 🔧 Geliştirme İpuçları

### Hot Reload
Development server otomatik olarak değişiklikleri algılar ve sayfayı yeniler.

### Console Logs
```javascript
// WebSocket mesajlarını logla
useEffect(() => {
    if (lastMessage) {
        console.log('WS Message:', JSON.parse(lastMessage.data));
    }
}, [lastMessage]);
```

### React DevTools
Chrome extension ile component state'lerini debug edebilirsin.

---

## 📚 Kullanılan Kütüphaneler

| Kütüphane | Versiyon | Kullanım Amacı |
|-----------|----------|----------------|
| react | 19.2.3 | UI framework |
| react-router-dom | 7.11.0 | Routing |
| axios | 1.13.2 | HTTP client |
| bootstrap | 5.3.8 | UI components |
| react-use-websocket | 4.13.0 | WebSocket hook |

---

## 🎨 Stil Yapısı

### Global Styles (index.css)
```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto';
}

.App {
  min-height: 100vh;
  background-color: #f5f5f5;
}
```

### Component Styles
Bootstrap utility class'ları kullanılır:

```jsx
<div className="container mt-5">
  <div className="row">
    <div className="col-md-6">
      <button className="btn btn-primary">Buton</button>
    </div>
  </div>
</div>
```

---

## 🚀 Performance Tips

1. **Lazy Loading**
```javascript
import { lazy, Suspense } from 'react';

const GameBoard = lazy(() => import('./pages/GameBoard'));

<Suspense fallback={<div>Loading...</div>}>
  <GameBoard />
</Suspense>
```

2. **Memoization**
```javascript
import { useMemo, useCallback } from 'react';

const expensiveValue = useMemo(() => computeValue(data), [data]);
const memoizedCallback = useCallback(() => handleClick(), []);
```

3. **Code Splitting**
React Router otomatik olarak route bazlı code splitting yapar.

---

## 📞 İletişim ve Destek

Sorularınız için:
- 📧 Email: frontend@numberduel.com
- 🐛 Issues: GitHub Issues
- 📚 Docs: `/README.md`

---

**Made with ❤️ using React & Bootstrap**

