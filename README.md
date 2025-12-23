# 🎮 Sayı Düellosu (Number Duel)

Gerçek zamanlı (real-time) çevrimiçi tahmin oyunu. İki oyuncu bir araya gelir, bahis yapar ve 1-100 arası gizli bir sayıyı tahmin etmeye çalışır.

---

## 📋 Proje Özeti

**Number Duel**, WebSocket teknolojisi kullanarak anlık oyun deneyimi sunan, Django ve React tabanlı bir web uygulamasıdır.

### Temel Özellikler

- ✅ **JWT Token Tabanlı Kimlik Doğrulama**
- ✅ **Gerçek Zamanlı WebSocket İletişimi** (Django Channels)
- ✅ **Bakiye ve Bahis Sistemi**
- ✅ **Transaction Geçmişi** (Hesap hareketleri)
- ✅ **Admin Panel** (GlobalSettings yönetimi)
- ✅ **Responsive Bootstrap 5 Arayüzü**
- ✅ **PostgreSQL Veritabanı**

---

## 🏗️ Mimari ve Teknoloji Yığını

### Backend
- **Framework:** Django 6.0
- **API:** Django REST Framework (DRF)
- **Auth:** SimpleJWT (Token-based)
- **Real-time:** Django Channels (WebSocket)
- **ASGI Server:** Daphne
- **Veritabanı:** PostgreSQL
- **Channel Layer:** InMemoryChannelLayer

### Frontend
- **Framework:** React 18
- **UI:** Bootstrap 5
- **HTTP Client:** Axios
- **WebSocket:** react-use-websocket
- **Routing:** React Router v7


## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler
- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

### 1️⃣ Backend Kurulumu

```bash
# Virtual environment oluştur
cd /Users/system/Desktop/number_duel_106
python3 -m venv venv
source venv/bin/activate

# Paketleri yükle
pip install -r requirements.txt

# PostgreSQL veritabanını oluştur
psql -U postgres
CREATE DATABASE numberduel106_db;

# Migrate işlemleri
python manage.py makemigrations
python manage.py migrate

# Superuser oluştur (Admin paneli için)
python manage.py createsuperuser

# Daphne ASGI sunucusunu başlat
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

### 2️⃣ Frontend Kurulumu

```bash
# Frontend dizinine git
cd game-frontend

# Paketleri yükle
npm install

# Development server'ı başlat
npm start
```

Frontend: [http://localhost:3000](http://localhost:3000)  
Backend API: [http://localhost:8000/api](http://localhost:8000/api)  
Admin Panel: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 🎯 API Endpoints

### Authentication (`/api/auth/`)
- `POST /auth/register/` - Yeni kullanıcı kaydı
- `POST /auth/login/` - Kullanıcı girişi (JWT token döner)
- `GET /auth/profile/` - Kullanıcı profili (Auth gerekli)
- `GET /auth/balance/` - Güncel bakiye (Auth gerekli)

### Game (`/api/game/`)
- `GET /game/rooms/` - Aktif odaları listele
- `POST /game/rooms/` - Yeni oda oluştur
- `POST /game/rooms/{id}/join/` - Odaya katıl
- `GET /game/transactions/` - Hesap hareketleri

### WebSocket
- `ws://localhost:8000/ws/game/{room_id}/` - Oyun WebSocket bağlantısı

---

## 🎲 Oyun Akışı

1. **Oda Kurulumu**
   - Kullanıcı bakiye kontrolünden geçer
   - Oda `OPEN` statüsünde açılır

2. **Eşleşme**
   - İkinci oyuncu katılır
   - Bakiyeler kilitlenir
   - Oda `FULL` olur ve WebSocket tetiklenir

3. **Oyun Başlangıcı**
   - Sistem 1-100 arası gizli sayı üretir
   - Yazı-tura ile başlayan oyuncu belirlenir

4. **Tahmin Döngüsü**
   - Sıradaki oyuncu tahminde bulunur
   - Sistem "UP" / "DOWN" / "WIN" döner
   - WebSocket ile tüm odaya yayınlanır

5. **Final**
   - Doğru tahmin yapıldığında bakiye transferi gerçekleşir
   - Oda `FINISHED` olur
   - Transaction kayıtları oluşturulur

---

## 🔧 Ayarlar ve Yapılandırma

### Django Settings (`core/settings.py`)

#### Veritabanı
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'numberduel106_db',
        'USER': 'erkancode',
        'PASSWORD': '1201',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

#### JWT Token Süresi
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

#### CORS (React için)
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

#### Channels Layer
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
```

> **AWS Geçişi için:** `InMemoryChannelLayer` yerine Redis kullanabilirsiniz:
> ```python
> CHANNEL_LAYERS = {
>     "default": {
>         "BACKEND": "channels_redis.core.RedisChannelLayer",
>         "CONFIG": {
>             "hosts": [("your-elasticache-url", 6379)],
>         },
>     },
> }
> ```

---

## 🛡️ Güvenlik Özellikleri

- ✅ **JWT Token Authentication** (Access + Refresh tokens)
- ✅ **CSRF Protection** (Django middleware)
- ✅ **SQL Injection Prevention** (ORM kullanımı)
- ✅ **Race Condition Protection** (`select_for_update()`)
- ✅ **Password Hashing** (Django's PBKDF2)
- ✅ **CORS Policy** (Sadece frontend origin'ine izin)

---

## 📱 Admin Panel Özellikleri

Django Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

1. **Global Settings** - Bahis limitlerini düzenle
2. **User Management** - Kullanıcıları yönet, bakiye düzenle
3. **Room Management** - Oyun odalarını görüntüle
4. **Transaction History** - Tüm bakiye hareketlerini izle
5. **Game Sessions** - Oyun geçmişini ve tahmin loglarını incele

---

## 📦 Production Deployment (AWS Hazırlığı)

### 1. Environment Variables
```bash
# .env dosyası oluştur
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://your-elasticache-url:6379
```

### 2. Static Files
```bash
python manage.py collectstatic
```

### 3. Gunicorn + Daphne Setup
```bash
pip install gunicorn
gunicorn core.wsgi:application  # HTTP requests
daphne core.asgi:application    # WebSocket requests
```

### 4. Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;  # React
    }

    location /api {
        proxy_pass http://localhost:8000;  # Django API
    }

    location /ws {
        proxy_pass http://localhost:8000;  # WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```


## 📚 Proje Yapısı

```
number_duel_106/
├── accounts/                 # Kullanıcı yönetimi
│   ├── models.py            # CustomUser modeli
│   ├── views.py             # Auth API views
│   ├── serilazers.py        # User serializers
│   └── urls.py              # Auth endpoints
├── game/                     # Oyun mantığı
│   ├── models.py            # Room, Transaction, GameSession
│   ├── views.py             # Room API views
│   ├── consumers.py         # WebSocket consumer
│   ├── routing.py           # WebSocket routing
│   ├── serializers.py       # Game serializers
│   ├── admin.py             # Admin panel config
│   └── urls.py              # Game endpoints
├── core/                     # Ana proje ayarları
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── asgi.py              # ASGI config (Channels)
│   └── wsgi.py              # WSGI config
├── game-frontend/            # React frontend
│   ├── public/
│   └── src/
│       ├── pages/           # Login, Register, Lobby, GameBoard
│       ├── utils/           # API interceptors
│       ├── App.js           # Ana component
│       └── index.js         # Entry point
├── manage.py                # Django CLI
├── requirements.txt         # Python dependencies
└── README.md                # Bu dosya
```


## 📞 İletişim

Sorularınız için:
- 📧 **Email:** erkankaya.work@gmail.com

