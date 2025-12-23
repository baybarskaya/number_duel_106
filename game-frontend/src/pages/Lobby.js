import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { gameAPI, authAPI } from '../utils/api';

const Lobby = () => {
    const [rooms, setRooms] = useState([]);
    const [balance, setBalance] = useState(0);
    const [username, setUsername] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newRoom, setNewRoom] = useState({
        name: '',
        bet_amount: 10
    });
    const [error, setError] = useState('');
    const [leaderboard, setLeaderboard] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        // Kullanıcı bilgilerini yükle
        const storedUsername = localStorage.getItem('username');
        const storedBalance = localStorage.getItem('balance');
        
        if (!storedUsername) {
            navigate('/login');
            return;
        }

        setUsername(storedUsername);
        setBalance(parseFloat(storedBalance) || 0);

        // Bakiyeyi API'den güncelle
        loadBalance();
        
        // Odaları ve leaderboard'ı yükle
        loadRooms();
        loadLeaderboard();

        // Her 3 saniyede bir odaları ve leaderboard'ı yenile
        const interval = setInterval(() => {
            loadRooms();
            loadLeaderboard();
        }, 3000);
        return () => clearInterval(interval);
    }, [navigate]);

    const loadBalance = async () => {
        try {
            const response = await authAPI.getBalance();
            setBalance(response.data.balance);
            localStorage.setItem('balance', response.data.balance);
        } catch (err) {
            console.error('Bakiye yüklenemedi:', err);
        }
    };

    const loadRooms = async () => {
        try {
            const response = await gameAPI.getRooms();
            setRooms(response.data);
        } catch (err) {
            console.error('Odalar yüklenemedi:', err);
        }
    };

    const loadLeaderboard = async () => {
        try {
            const response = await gameAPI.getLeaderboard();
            setLeaderboard(response.data);
        } catch (err) {
            console.error('Leaderboard yüklenemedi:', err);
        }
    };

    const handleCreateRoom = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await gameAPI.createRoom(newRoom);
            setShowCreateModal(false);
            setNewRoom({ name: '', bet_amount: 10 });
            
            // Oda oluşturulduktan sonra creator otomatik olarak oyun sayfasına gitsin
            const roomId = response.data.id;
            navigate(`/game/${roomId}`);
        } catch (err) {
            setError(err.response?.data?.bet_amount?.[0] || 'Oda oluşturulamadı!');
        }
    };

    const handleJoinRoom = async (roomId) => {
        try {
            await gameAPI.joinRoom(roomId);
            navigate(`/game/${roomId}`);
        } catch (err) {
            alert(err.response?.data?.error || 'Odaya katılamazsın!');
        }
    };

    const handleLogout = () => {
        localStorage.clear();
        navigate('/login');
    };

    return (
        <div className="container mt-4">
            {/* Header */}
            <div className="row mb-4">
                <div className="col-md-8">
                    <h2>🎮 Oyun Lobisi</h2>
                    <p className="text-muted">Aktif odaları görüntüle veya yeni oda oluştur</p>
                </div>
                <div className="col-md-4 text-end">
                    <div className="card">
                        <div className="card-body">
                            <h5>{username}</h5>
                            <p className="mb-2">
                                <strong>💰 {balance.toFixed(2)} Puan</strong>
                            </p>
                            <button 
                                className="btn btn-sm btn-info me-2"
                                onClick={() => navigate('/profile')}
                            >
                                👤 Profil
                            </button>
                            <button 
                                className="btn btn-sm btn-outline-danger"
                                onClick={handleLogout}
                            >
                                Çıkış Yap
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* İstatistikler ve Oda Oluştur */}
            <div className="row mb-3">
                <div className="col-md-8">
                    <div className="d-flex gap-3">
                        <div className="alert alert-success mb-0 py-2 px-3">
                            <strong>{rooms.filter(r => r.status === 'OPEN').length}</strong> oda bekliyor
                        </div>
                        <div className="alert alert-warning mb-0 py-2 px-3">
                            <strong>{rooms.filter(r => r.status === 'FULL').length}</strong> oyun devam ediyor
                        </div>
                    </div>
                </div>
                <div className="col-md-4 text-end">
                    <button 
                        className="btn btn-primary"
                        onClick={() => setShowCreateModal(true)}
                    >
                        + Yeni Oda Kur
                    </button>
                </div>
            </div>

            {/* Odalar ve Leaderboard */}
            <div className="row">
                {/* Sol Taraf - Odalar */}
                <div className="col-md-8">
                {rooms.length === 0 ? (
                    <div className="col-12">
                        <div className="alert alert-info">
                            Henüz aktif oda yok. İlk odayı sen oluştur!
                        </div>
                    </div>
                ) : (
                    rooms.map(room => {
                        const isMyRoom = room.creator_name === username;
                        const isFull = room.status === 'FULL';
                        const isOpen = room.status === 'OPEN';
                        
                        return (
                            <div className="col-md-4 mb-3" key={room.id}>
                                <div className={`card shadow-sm ${
                                    isMyRoom ? 'border-primary' : 
                                    isFull ? 'border-warning' : 
                                    'border-success'
                                }`}>
                                    <div className="card-body">
                                        <h5 className="card-title">
                                            {room.name}
                                            {isMyRoom && <span className="badge bg-primary ms-2">Senin Odan</span>}
                                            {isFull && <span className="badge bg-warning text-dark ms-2">Oynanıyor</span>}
                                            {isOpen && <span className="badge bg-success ms-2">Bekliyor</span>}
                                        </h5>
                                        <p className="mb-1">
                                            <strong>Bahis:</strong> {room.bet_amount} Puan
                                        </p>
                                        <p className="mb-1">
                                            <strong>Kuran:</strong> {room.creator_name}
                                        </p>
                                        <p className="mb-3">
                                            <strong>Oyuncular:</strong> {room.player_count}/2
                                            {isFull && <span className="text-success ms-2">🟢 Canlı</span>}
                                        </p>
                                        
                                        {/* Butonlar */}
                                        {isMyRoom ? (
                                            <button 
                                                onClick={() => navigate(`/game/${room.id}`)} 
                                                className="btn btn-primary w-100"
                                            >
                                                Odaya Gir
                                            </button>
                                        ) : isFull ? (
                                            <button 
                                                className="btn btn-secondary w-100" 
                                                disabled
                                            >
                                                Dolu (Oynanıyor)
                                            </button>
                                        ) : (
                                            <button 
                                                onClick={() => handleJoinRoom(room.id)} 
                                                className="btn btn-success w-100"
                                            >
                                                Katıl
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
                </div>
                
                {/* Sağ Taraf - Leaderboard */}
                <div className="col-md-4">
                    <div className="card shadow">
                        <div className="card-header bg-warning text-dark">
                            <h5 className="mb-0">🏆 Liderlik Tablosu</h5>
                            <small className="text-muted">En çok kazanan 10 oyuncu</small>
                        </div>
                        <div className="card-body p-0">
                            <div className="table-responsive" style={{maxHeight: '500px', overflowY: 'auto'}}>
                                {leaderboard.length === 0 ? (
                                    <div className="text-center p-4">
                                        <p className="text-muted">
                                            Henüz oyun oynayan kimse yok.
                                        </p>
                                    </div>
                                ) : (
                                    <table className="table table-sm table-hover mb-0">
                                        <thead className="sticky-top bg-light">
                                            <tr>
                                                <th style={{width: '40px'}}>#</th>
                                                <th>Oyuncu</th>
                                                <th style={{width: '80px'}}>Bakiye</th>
                                                <th style={{width: '60px'}}>W/T</th>
                                                <th style={{width: '50px'}}>%</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {leaderboard.map((player) => {
                                                const isMe = player.username === username;
                                                
                                                return (
                                                    <tr 
                                                        key={player.rank}
                                                        className={isMe ? 'table-primary' : ''}
                                                    >
                                                        <td>
                                                            {player.rank === 1 && '🥇'}
                                                            {player.rank === 2 && '🥈'}
                                                            {player.rank === 3 && '🥉'}
                                                            {player.rank > 3 && player.rank}
                                                        </td>
                                                        <td>
                                                            <strong>{player.username}</strong>
                                                            {isMe && <span className="badge bg-primary ms-1">Sen</span>}
                                                        </td>
                                                        <td className="text-end">
                                                            <small>{player.balance.toFixed(0)}</small>
                                                        </td>
                                                        <td className="text-center">
                                                            <small className="text-success">{player.total_wins}</small>
                                                            /
                                                            <small className="text-muted">{player.total_games}</small>
                                                        </td>
                                                        <td className="text-end">
                                                            <small className={
                                                                player.win_rate >= 60 ? 'text-success fw-bold' :
                                                                player.win_rate >= 40 ? 'text-warning' :
                                                                'text-danger'
                                                            }>
                                                                {player.win_rate}%
                                                            </small>
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Oda Oluştur Modal */}
            {showCreateModal && (
                <div className="modal show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Yeni Oda Oluştur</h5>
                                <button 
                                    type="button" 
                                    className="btn-close"
                                    onClick={() => setShowCreateModal(false)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                {error && (
                                    <div className="alert alert-danger">{error}</div>
                                )}
                                <form onSubmit={handleCreateRoom}>
                                    <div className="mb-3">
                                        <label className="form-label">Oda Adı</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={newRoom.name}
                                            onChange={(e) => setNewRoom({...newRoom, name: e.target.value})}
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Bahis Miktarı</label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            value={newRoom.bet_amount}
                                            onChange={(e) => setNewRoom({...newRoom, bet_amount: e.target.value})}
                                            min="10"
                                            max="1000"
                                            step="5"
                                            required
                                        />
                                        <small className="text-muted">Min: 10, Max: 1000</small>
                                    </div>
                                    <button type="submit" className="btn btn-primary w-100">
                                        Oluştur
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Lobby;