# 🚀 Kurulum Kılavuzu (Setup Guide)

Bu doküman, Number Duel projesini sıfırdan kurmak ve çalıştırmak için adım adım talimatları içerir.

---

## 📋 Ön Gereksinimler

Sisteminizde aşağıdaki yazılımların kurulu olduğundan emin olun:

- **Python:** 3.12 veya üzeri
- **Node.js:** 18 veya üzeri
- **PostgreSQL:** 15 veya üzeri
- **pip:** Python paket yöneticisi
- **npm:** Node paket yöneticisi

---

## 1️⃣ Proje Klasörüne Giriş

```bash
cd /Users/system/Desktop/number_duel_106
```

---

## 2️⃣ Backend Kurulumu (Django)

### Adım 1: Virtual Environment Oluştur

```bash
python3 -m venv venv
source venv/bin/activate  # MacOS/Linux
# Windows: venv\Scripts\activate
```

### Adım 2: Python Paketlerini Yükle

```bash
pip install -r requirements.txt
```

### Adım 3: PostgreSQL Veritabanını Hazırla

PostgreSQL'e bağlan:

```bash
psql -U postgres
```

Veritabanı ve kullanıcı oluştur:

```sql
CREATE DATABASE numberduel106_db;
CREATE USER erkancode WITH PASSWORD '1201';
ALTER ROLE erkancode SET client_encoding TO 'utf8';
ALTER ROLE erkancode SET default_transaction_isolation TO 'read committed';
ALTER ROLE erkancode SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE numberduel106_db TO erkancode;
\q
```

### Adım 4: Migration İşlemlerini Çalıştır

```bash
python manage.py makemigrations
python manage.py migrate
```

### Adım 5: Superuser Oluştur (Admin için)

```bash
python manage.py createsuperuser
# Kullanıcı adı, email ve şifre girin
```

### Adım 6: Global Settings Oluştur (Opsiyonel)

Django shell açın:

```bash
python manage.py shell
```

Shell içinde:

```python
from game.models import GlobalSettings
GlobalSettings.objects.create(min_bet=10, max_bet=1000, bet_step=5)
exit()
```

### Adım 7: Backend Sunucusunu Başlat

```bash
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

✅ Backend şu adreste çalışıyor: **http://127.0.0.1:8000**

---

## 3️⃣ Frontend Kurulumu (React)

Yeni bir terminal penceresi açın.

### Adım 1: Frontend Dizinine Git

```bash
cd /Users/system/Desktop/number_duel_106/game-frontend
```

### Adım 2: Node Paketlerini Yükle

```bash
npm install
```

### Adım 3: Development Server'ı Başlat

```bash
npm start
```

✅ Frontend şu adreste çalışıyor: **http://localhost:3000**

Tarayıcı otomatik açılacak. Açılmazsa manuel olarak yukarıdaki adresi ziyaret edin.

---

## 4️⃣ İlk Kullanım

### 1. Kullanıcı Kaydı

1. **http://localhost:3000** adresine git
2. **Kayıt Ol** butonuna tıkla
3. Formu doldur:
   - Kullanıcı adı
   - E-posta
   - Doğum tarihi
   - Şifre (min 8 karakter)
4. Kayıt ol - Otomatik 1000 puan hediye alacaksın!

### 2. Oda Oluştur

1. Lobby'de **"+ Yeni Oda Kur"** butonuna tıkla
2. Oda adı ve bahis miktarını gir
3. Oda oluşturuldu!

### 3. Oyun Oyna

1. İkinci bir kullanıcı ile (başka bir tarayıcı/incognito modunda) giriş yap
2. Lobby'de aktif odayı gör
3. **"Katıl"** butonuna tıkla
4. Oyun başladı! Sırayla 1-100 arası tahmin yapın

---

## 5️⃣ Admin Panel

Admin paneline erişim:

1. **http://127.0.0.1:8000/admin** adresine git
2. Superuser bilgilerinle giriş yap

Admin panelinden yapabileceklerin:

- ✅ GlobalSettings'i düzenle (min/max bet)
- ✅ Kullanıcıların bakiyelerini düzenle
- ✅ Oyun odalarını görüntüle
- ✅ Transaction geçmişini incele
- ✅ GameSession loglarını kontrol et

---

## 6️⃣ API Test Etme (Opsiyonel)

### cURL ile Test

**Register:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "birth_date": "1995-01-01"
  }'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Get Rooms (Token gerekli):**
```bash
curl -X GET http://127.0.0.1:8000/api/game/rooms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 7️⃣ Sorun Giderme

### Backend çalışmıyor

**Hata:** `ImportError: No module named 'django'`  
**Çözüm:** Virtual environment'ı aktif ettiğinizden emin olun
```bash
source venv/bin/activate
```

**Hata:** `FATAL: database "numberduel106_db" does not exist`  
**Çözüm:** PostgreSQL veritabanını oluşturun (Adım 3)

**Hata:** `Error: That port is already in use`  
**Çözüm:** Başka bir port kullanın
```bash
daphne -b 0.0.0.0 -p 8001 core.asgi:application
```

### Frontend çalışmıyor

**Hata:** `npm ERR! Cannot find module`  
**Çözüm:** Node modüllerini tekrar yükleyin
```bash
rm -rf node_modules package-lock.json
npm install
```

**Hata:** CORS hatası alıyorum  
**Çözüm:** Backend'in çalıştığından ve CORS ayarlarının doğru olduğundan emin olun

### WebSocket bağlanamıyor

**Hata:** `WebSocket connection to 'ws://...' failed`  
**Çözüm:** 
1. Daphne'nin çalıştığından emin olun (manage.py runserver ÇALIŞMAZ!)
2. Browser console'da hatayı kontrol edin
3. core/asgi.py dosyasını kontrol edin

---

## 8️⃣ Production Deployment

### Gunicorn (HTTP) + Daphne (WebSocket)

```bash
# HTTP requests için
gunicorn core.wsgi:application --bind 0.0.0.0:8000

# WebSocket requests için (ayrı bir port)
daphne -b 0.0.0.0 -p 8001 core.asgi:application
```

### Nginx Reverse Proxy

```nginx
upstream django_http {
    server 127.0.0.1:8000;
}

upstream django_ws {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://django_http;
    }

    location /admin {
        proxy_pass http://django_http;
    }

    location /ws {
        proxy_pass http://django_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        root /path/to/react/build;
        try_files $uri /index.html;
    }
}
```

### Redis (Production Channel Layer)

```bash
pip install channels-redis
```

settings.py'yi güncelle:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

---

## 9️⃣ Yararlı Komutlar

### Django

```bash
# Migration oluştur
python manage.py makemigrations

# Migration uygula
python manage.py migrate

# Shell aç
python manage.py shell

# Static dosyaları topla
python manage.py collectstatic

# Test çalıştır
python manage.py test
```

### React

```bash
# Development başlat
npm start

# Production build
npm run build

# Test çalıştır
npm test
```

---

## 🎉 Tebrikler!

Projeniz başarıyla kuruldu ve çalışıyor! 

Herhangi bir sorun yaşarsanız:
- README.md dosyasını kontrol edin
- GitHub Issues'a bakın
- Django ve Channels dokümantasyonunu inceleyin

**İyi oyunlar! 🎮**

