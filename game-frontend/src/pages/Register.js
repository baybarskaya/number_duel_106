import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        birth_date: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');

        // Şifre eşleşme kontrolü
        if (formData.password !== formData.password2) {
            setError('Şifreler eşleşmiyor!');
            return;
        }

        // Şifre uzunluk kontrolü
        if (formData.password.length < 8) {
            setError('Şifre en az 8 karakter olmalı!');
            return;
        }

        setLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/auth/register/', {
                username: formData.username,
                email: formData.email,
                password: formData.password,
                birth_date: formData.birth_date
            });

            // Token'ları localStorage'a kaydet
            localStorage.setItem('access_token', response.data.tokens.access);
            localStorage.setItem('refresh_token', response.data.tokens.refresh);
            localStorage.setItem('user_id', String(response.data.user.id)); // String olarak kaydet
            localStorage.setItem('username', response.data.user.username);
            localStorage.setItem('balance', response.data.user.balance);
            
            console.log('Kayıt başarılı - User ID:', response.data.user.id, typeof response.data.user.id);

            // Lobby'ye yönlendir
            navigate('/lobby');
        } catch (err) {
            const errorMsg = err.response?.data?.username?.[0] 
                || err.response?.data?.error 
                || 'Kayıt başarısız!';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card shadow">
                        <div className="card-body p-5">
                            <h2 className="text-center mb-4">🎮 Sayı Düellosu</h2>
                            <h5 className="text-center text-muted mb-4">Kayıt Ol</h5>
                            
                            {error && (
                                <div className="alert alert-danger" role="alert">
                                    {error}
                                </div>
                            )}

                            <div className="alert alert-info" role="alert">
                                <small>
                                    ✨ Yeni üyelere 1000 puan hediye!
                                </small>
                            </div>

                            <form onSubmit={handleRegister}>
                                <div className="mb-3">
                                    <label className="form-label">Kullanıcı Adı</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="username"
                                        value={formData.username}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">E-posta</label>
                                    <input
                                        type="email"
                                        className="form-control"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Doğum Tarihi</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        name="birth_date"
                                        value={formData.birth_date}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Şifre</label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleChange}
                                        required
                                    />
                                    <small className="text-muted">En az 8 karakter</small>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Şifre (Tekrar)</label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        name="password2"
                                        value={formData.password2}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <button 
                                    type="submit" 
                                    className="btn btn-success w-100"
                                    disabled={loading}
                                >
                                    {loading ? 'Kayıt yapılıyor...' : 'Kayıt Ol'}
                                </button>
                            </form>

                            <hr className="my-4" />

                            <p className="text-center mb-0">
                                Zaten hesabın var mı? 
                                <Link to="/login" className="ms-2 text-decoration-none">
                                    Giriş Yap
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;

