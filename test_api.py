#!/usr/bin/env python
"""
Number Duel - API Test Script
Bu script backend API'lerini test eder.

Kullanım:
    python test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_register():
    """Kullanıcı kaydı testi"""
    print_section("TEST 1: KULLANICI KAYDI")
    
    timestamp = datetime.now().strftime("%H%M%S")
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "testpass123",
        "birth_date": "1995-05-15"
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print("✅ Kayıt başarılı!")
        result = response.json()
        print(f"   Kullanıcı: {result['user']['username']}")
        print(f"   Bakiye: {result['user']['balance']}")
        print(f"   Token alındı: {result['tokens']['access'][:30]}...")
        return result['tokens']['access'], result['user']['id']
    else:
        print(f"❌ Kayıt başarısız: {response.status_code}")
        print(f"   Hata: {response.text}")
        return None, None

def test_login():
    """Kullanıcı girişi testi"""
    print_section("TEST 2: KULLANICI GİRİŞİ")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "admin",  # Var olan bir kullanıcı
        "password": "admin123"
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Giriş başarılı!")
        result = response.json()
        print(f"   Kullanıcı: {result['user']['username']}")
        print(f"   Bakiye: {result['user']['balance']}")
        return result['tokens']['access']
    else:
        print(f"⚠️  Giriş yapılamadı (admin kullanıcısı yok olabilir)")
        print(f"   Status: {response.status_code}")
        return None

def test_profile(token):
    """Profil bilgisi testi"""
    print_section("TEST 3: PROFİL BİLGİSİ")
    
    url = f"{BASE_URL}/auth/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Profil bilgisi alındı!")
        result = response.json()
        print(f"   ID: {result['id']}")
        print(f"   Username: {result['username']}")
        print(f"   Balance: {result['balance']}")
        print(f"   Email: {result.get('email', 'N/A')}")
    else:
        print(f"❌ Profil alınamadı: {response.status_code}")

def test_rooms(token):
    """Oda listesi testi"""
    print_section("TEST 4: ODA LİSTESİ")
    
    url = f"{BASE_URL}/game/rooms/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Oda listesi alındı!")
        rooms = response.json()
        print(f"   Aktif oda sayısı: {len(rooms)}")
        if rooms:
            for room in rooms[:3]:  # İlk 3 odayı göster
                print(f"   - {room['name']} (Bahis: {room['bet_amount']})")
    else:
        print(f"❌ Oda listesi alınamadı: {response.status_code}")

def test_create_room(token):
    """Oda oluşturma testi"""
    print_section("TEST 5: ODA OLUŞTURMA")
    
    url = f"{BASE_URL}/game/rooms/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": f"Test Room {datetime.now().strftime('%H:%M:%S')}",
        "bet_amount": 25.00
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Oda oluşturuldu!")
        room = response.json()
        print(f"   ID: {room['id']}")
        print(f"   İsim: {room['name']}")
        print(f"   Bahis: {room['bet_amount']}")
        print(f"   Durum: {room['status']}")
        return room['id']
    else:
        print(f"❌ Oda oluşturulamadı: {response.status_code}")
        print(f"   Hata: {response.text}")
        return None

def test_transactions(token):
    """Transaction geçmişi testi"""
    print_section("TEST 6: HESAP HAREKETLERİ")
    
    url = f"{BASE_URL}/game/transactions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Transaction listesi alındı!")
        transactions = response.json()
        print(f"   Toplam transaction: {len(transactions)}")
        if transactions:
            for tx in transactions[:3]:  # İlk 3'ü göster
                print(f"   - {tx['description']}: {tx['amount']}")
    else:
        print(f"❌ Transaction listesi alınamadı: {response.status_code}")

def main():
    print("\n" + "🎮 Number Duel - API Test Suite")
    print("Backend URL:", BASE_URL)
    
    try:
        # Test 1 & 2: Register veya Login
        token, user_id = test_register()
        
        if not token:
            token = test_login()
        
        if not token:
            print("\n❌ Token alınamadı, testler durduruluyor.")
            return
        
        # Test 3: Profile
        test_profile(token)
        
        # Test 4: Rooms list
        test_rooms(token)
        
        # Test 5: Create room
        room_id = test_create_room(token)
        
        # Test 6: Transactions
        test_transactions(token)
        
        print_section("TEST SONUÇLARI")
        print("✅ API testleri tamamlandı!")
        print("\n💡 WebSocket testini manuel olarak yapın:")
        print("   1. Frontend'i başlatın: npm start")
        print("   2. İki farklı kullanıcıyla giriş yapın")
        print("   3. Bir oda oluşturun ve katılın")
        print("   4. Tahmin yaparak oyunu test edin")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ BAĞLANTI HATASI!")
        print("Backend çalışmıyor olabilir. Şunu deneyin:")
        print("   daphne -b 0.0.0.0 -p 8000 core.asgi:application")
    except Exception as e:
        print(f"\n❌ BEKLENMEDİK HATA: {str(e)}")

if __name__ == "__main__":
    main()

