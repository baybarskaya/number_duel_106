import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
                username,
                password
            });

            // Token'ları localStorage'a kaydet
            localStorage.setItem('access_token', response.data.tokens.access);
            localStorage.setItem('refresh_token', response.data.tokens.refresh);
            localStorage.setItem('user_id', String(response.data.user.id)); // String olarak kaydet
            localStorage.setItem('username', response.data.user.username);
            localStorage.setItem('balance', response.data.user.balance);
            
            console.log('Login başarılı - User ID:', response.data.user.id, typeof response.data.user.id);

            // Lobby'ye yönlendir
            navigate('/lobby');
        } catch (err) {
            setError(err.response?.data?.error || 'Giriş başarısız!');
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
                            <h5 className="text-center text-muted mb-4">Giriş Yap</h5>
                            
                            {error && (
                                <div className="alert alert-danger" role="alert">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleLogin}>
                                <div className="mb-3">
                                    <label className="form-label">Kullanıcı Adı</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Şifre</label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>

                                <button 
                                    type="submit" 
                                    className="btn btn-primary w-100"
                                    disabled={loading}
                                >
                                    {loading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
                                </button>
                            </form>

                            <hr className="my-4" />

                            <p className="text-center mb-0">
                                Hesabın yok mu? 
                                <Link to="/register" className="ms-2 text-decoration-none">
                                    Kayıt Ol
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;

