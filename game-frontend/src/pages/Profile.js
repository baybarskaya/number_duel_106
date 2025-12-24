import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, gameAPI } from '../utils/api';

const Profile = () => {
    const [profile, setProfile] = useState(null);
    const [transactions, setTransactions] = useState([]);
    const [filter, setFilter] = useState('all');
    const navigate = useNavigate();

    useEffect(() => {
        loadProfile();
        loadTransactions();
    }, []);

    const loadProfile = async () => {
        try {
            const response = await authAPI.getProfile();
            setProfile(response.data);
        } catch (err) {
            console.error('Profil yüklenemedi:', err);
            if (err.response?.status === 401) {
                navigate('/login');
            }
        }
    };

    const loadTransactions = async () => {
        try {
            const response = await gameAPI.getTransactions();
            setTransactions(response.data);
        } catch (err) {
            console.error('Transaction geçmişi yüklenemedi:', err);
        }
    };

    const filteredTransactions = transactions.filter(tx => {
        if (filter === 'win') return tx.amount > 0;
        if (filter === 'loss') return tx.amount < 0;
        return true; // 'all'
    });

    if (!profile) {
        return (
            <div className="container mt-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Yükleniyor...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="container mt-4">
            <div className="row mb-4">
                <div className="col-md-12">
                    <button className="btn btn-secondary mb-3" onClick={() => navigate('/lobby')}>
                        ← Lobiye Dön
                    </button>
                </div>
            </div>

            <div className="row">
                <div className="col-md-4">
                    <div className="card shadow">
                        <div className="card-header bg-primary text-white">
                            <h5 className="mb-0">👤 Profil</h5>
                        </div>
                        <div className="card-body">
                            <h3 className="text-center mb-3">{profile.username}</h3>
                            
                            <div className="mb-3 text-center">
                                <strong>💰 Bakiye:</strong>
                                <h4 className="text-success mb-0">{parseFloat(profile.balance).toFixed(2)} Puan</h4>
                            </div>
                            
                            <hr />
                            
                            <div className="mb-2">
                                <strong>📧 E-posta:</strong>
                                <p className="mb-0">{profile.email || 'Belirtilmemiş'}</p>
                            </div>
                            
                            <div className="mb-3">
                                <strong>🎂 Doğum Tarihi:</strong>
                                <p className="mb-0">{profile.birth_date || 'Belirtilmemiş'}</p>
                            </div>
                            
                            <hr />
                            
                            <h6 className="text-muted mb-3">📊 Oyun İstatistikleri</h6>
                            
                            <div className="row text-center mb-2">
                                <div className="col-4">
                                    <div className="border rounded p-2">
                                        <h5 className="mb-0">{profile.total_games}</h5>
                                        <small className="text-muted">Toplam</small>
                                    </div>
                                </div>
                                <div className="col-4">
                                    <div className="border rounded p-2 bg-success bg-opacity-10">
                                        <h5 className="mb-0 text-success">{profile.total_wins}</h5>
                                        <small className="text-muted">Kazanma</small>
                                    </div>
                                </div>
                                <div className="col-4">
                                    <div className="border rounded p-2 bg-danger bg-opacity-10">
                                        <h5 className="mb-0 text-danger">{profile.total_games - profile.total_wins}</h5>
                                        <small className="text-muted">Kayıp</small>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="text-center p-3 bg-light rounded">
                                <strong>Kazanma Oranı:</strong>
                                <h3 className={`mb-0 ${
                                    profile.win_rate >= 60 ? 'text-success' :
                                    profile.win_rate >= 40 ? 'text-warning' :
                                    'text-danger'
                                }`}>
                                    {profile.win_rate}%
                                </h3>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="col-md-8">
                    <div className="card shadow">
                        <div className="card-header bg-info text-white">
                            <h5 className="mb-0">📜 Hesap Hareketleri</h5>
                        </div>
                        <div className="card-body">
                            <div className="btn-group mb-3" role="group">
                                <button 
                                    className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
                                    onClick={() => setFilter('all')}
                                >
                                    Tümü ({transactions.length})
                                </button>
                                <button 
                                    className={`btn ${filter === 'win' ? 'btn-success' : 'btn-outline-success'}`}
                                    onClick={() => setFilter('win')}
                                >
                                    Kazançlar ({transactions.filter(t => t.amount > 0).length})
                                </button>
                                <button 
                                    className={`btn ${filter === 'loss' ? 'btn-danger' : 'btn-outline-danger'}`}
                                    onClick={() => setFilter('loss')}
                                >
                                    Kayıplar ({transactions.filter(t => t.amount < 0).length})
                                </button>
                            </div>

                            <div style={{maxHeight: '500px', overflowY: 'auto'}}>
                                {filteredTransactions.length === 0 ? (
                                    <div className="alert alert-info">
                                        {filter === 'all' ? 'Henüz işlem geçmişi yok.' :
                                         filter === 'win' ? 'Henüz kazanç kaydı yok.' :
                                         'Henüz kayıp kaydı yok.'}
                                    </div>
                                ) : (
                                    <table className="table table-hover">
                                        <thead className="table-light sticky-top">
                                            <tr>
                                                <th style={{width: '150px'}}>Tarih</th>
                                                <th>Açıklama</th>
                                                <th className="text-end" style={{width: '120px'}}>Miktar</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {filteredTransactions.map((tx) => (
                                                <tr key={tx.id}>
                                                    <td>
                                                        <small>{new Date(tx.created_at).toLocaleString('tr-TR', {
                                                            day: '2-digit',
                                                            month: '2-digit',
                                                            year: 'numeric',
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}</small>
                                                    </td>
                                                    <td>
                                                        <small>{tx.description}</small>
                                                    </td>
                                                    <td className={`text-end fw-bold ${
                                                        tx.amount > 0 ? 'text-success' : 'text-danger'
                                                    }`}>
                                                        {tx.amount > 0 ? '+' : ''}{parseFloat(tx.amount).toFixed(2)}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;

