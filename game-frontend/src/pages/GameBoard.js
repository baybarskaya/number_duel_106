import React, { useState, useEffect, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { useParams, useNavigate } from 'react-router-dom';

const GameBoard = () => {
    const { roomId } = useParams();
    const navigate = useNavigate();
    const [guess, setGuess] = useState("");
    const [logs, setLogs] = useState([]);
    const [turn, setTurn] = useState(null);
    const [turnName, setTurnName] = useState('');
    const [gameStarted, setGameStarted] = useState(false);
    const [gameEnded, setGameEnded] = useState(false);
    const [myUserId, setMyUserId] = useState(null);
    const [guessCount, setGuessCount] = useState(0);
    const [disconnectWarning, setDisconnectWarning] = useState(false);
    const [playerBalances, setPlayerBalances] = useState({
        myBalance: null,
        myStartBalance: null,
        betAmount: null
    });
    const logsEndRef = useRef(null);
    const token = localStorage.getItem('access_token');
    const wsUrl = `ws://127.0.0.1:8000/ws/game/${roomId}/?token=${token}`;
    
    const { sendJsonMessage, lastMessage, readyState } = useWebSocket(
        wsUrl,
        {
            shouldReconnect: (closeEvent) => {
                console.log('WebSocket koptu, yeniden bağlanılıyor...', closeEvent);
                return true;
            },
            reconnectAttempts: 20,
            reconnectInterval: (attemptNumber) => {
                return Math.min(1000 * Math.pow(2, attemptNumber), 10000);
            },
            onOpen: () => {
                console.log('✅ WebSocket bağlantısı kuruldu!');
                setDisconnectWarning(false);
            },
            onClose: () => {
                console.log('⚠️ WebSocket bağlantısı kapatıldı!');
                if (gameStarted && !gameEnded) {
                    setDisconnectWarning(true);
                }
            },
            onError: (event) => {
                console.error('WebSocket hatası:', event);
            },
            share: false,
            retryOnError: true,
        }
    );

    useEffect(() => {
        const userId = parseInt(localStorage.getItem('user_id'));
        const username = localStorage.getItem('username');
        
        if (!userId) {
            navigate('/login');
            return;
        }
        
        setMyUserId(userId);
    
    }, [navigate]);

    useEffect(() => {
        if (lastMessage !== null) {
            const data = JSON.parse(lastMessage.data);
            console.log('📨 WebSocket mesajı:', data);
            if (data.error) {
                
                setLogs(prev => [...prev, {
                    text: `⚠️ ${data.error}`,
                    event: 'ERROR',
                    timestamp: new Date().toLocaleTimeString()
                }]);
                
                scrollToBottom();
                return;
            }

            if (data.message) {
                setLogs(prev => [...prev, {
                    text: data.message,
                    guess: data.last_guess,
                    guesserName: data.guesser_name,
                    guesserId: data.guesser_id,
                    event: data.event,
                    timestamp: new Date().toLocaleTimeString()
                }]);
                
                if (data.event === 'CONTINUE') {
                    setGuessCount(prev => prev + 1);
                }
            }
            if (data.turn !== undefined && data.turn !== null) {
                const turnId = parseInt(data.turn);
            
                
                setTurn(turnId);
            }
            
            if (data.turn_name) {
                setTurnName(data.turn_name);
            }

            if (data.event === 'START') {
                setGameStarted(true);
                setGuessCount(0);
                
                if (data.balances) {
                    const creatorInfo = data.balances.creator;
                    const player2Info = data.balances.player2;
                    const myBalanceInfo = (creatorInfo.user_id === myUserId) 
                        ? creatorInfo 
                        : player2Info;
                    
                    console.log('💰 Bakiye bilgisi yüklendi:', {
                        myUserId,
                        creatorId: creatorInfo.user_id,
                        player2Id: player2Info.user_id,
                        selected: myBalanceInfo
                    });
                    
                    if (myBalanceInfo) {
                        setPlayerBalances({
                            myBalance: myBalanceInfo.current,
                            myStartBalance: myBalanceInfo.start,
                            betAmount: myBalanceInfo.bet
                        });
                    }
                }
            }

            if (data.event === 'WINNER') {
                console.log('🏆 Oyun bitti!', {
                    reason: data.reason,
                    winnerId: data.winner_id,
                    myUserId: myUserId,
                    iAmWinner: data.winner_id === myUserId,
                    gameEnded: gameEnded
                });
                
                if (gameEnded) {
                    return;
                }
                
                setGameEnded(true);
                setDisconnectWarning(false);
            
                const iAmWinner = data.winner_id === myUserId;
                const isManualLeave = data.reason === 'manual_leave';
                const isDisconnect = data.reason === 'disconnect';
                
                if (isManualLeave) {
                    if (iAmWinner) {
                        setTimeout(() => {
                            alert('🏆 Rakibiniz oyunu terketti!\n\nSiz kazandınız ve bahsi aldınız. 💰');
                            navigate('/lobby');
                        }, 500);
                    } else {
                        // Ben manuel leave oldum ve kaybettim
                        alert('❌ Oyundan ayrıldığınız için oyunu kaybettiniz.');
                        navigate('/lobby');
                    }
                } else if (isDisconnect) {
                    if (iAmWinner) {
                        setTimeout(() => {
                            alert('🎉 Rakibiniz 30 saniye bağlantısız kaldı!\n\nSiz kazandınız ve bahsi aldınız. 💰');
                            navigate('/lobby');
                        }, 500);
                    } else {
                        alert('❌ 30 saniye bağlantısız kaldınız ve oyunu kaybettiniz.');
                        navigate('/lobby');
                    }
                } else {
                    const winMessage = iAmWinner 
                        ? '🎉 Tebrikler! Doğru sayıyı buldunuz ve bahsi kazandınız! 💰' 
                        : '😔 Rakibiniz doğru sayıyı buldu. Oyunu kaybettiniz.';
                    
                    setTimeout(() => {
                        alert(winMessage);
                        navigate('/lobby');
                    }, 1500);
                }
            }

            scrollToBottom();
        }
    }, [lastMessage, navigate, myUserId]);

    const scrollToBottom = () => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const makeGuess = () => {
        const guessNum = parseInt(guess);
        
        if (!guessNum || guessNum < 1 || guessNum > 100) {
            alert('Lütfen 1-100 arası bir sayı girin!');
            return;
        }

        if (readyState !== ReadyState.OPEN) {
            alert('Bağlantı kuruluyor, lütfen bekleyin...');
            return;
        }
        
        try {
            sendJsonMessage({ 
                action: 'guess', 
                number: guessNum 
            });
        setGuess("");
        } catch (error) {
            console.error('Tahmin gönderme hatası:', error);
            alert('Tahmin gönderilemedi, lütfen tekrar deneyin!');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            makeGuess();
        }
    };

    const handleLeaveLobby = () => {
        if (gameStarted && !gameEnded) {
            // Oyun devam ediyor - uyarı ver
            if (window.confirm('⚠️ Oyun devam ediyor! Ayrılırsan oyunu kaybedersin ve bahisini alamazsın. Emin misin?')) {
               
                try {
                    sendJsonMessage({ action: 'leave_game' });
                } catch (error) {
                    console.error('Leave mesajı gönderilemedi:', error);
                }
                
                setGameEnded(true); 
                navigate('/lobby');
            }
        } else {
            navigate('/lobby');
        }
    };

    const connectionStatus = {
        [ReadyState.CONNECTING]: '🔄 Bağlanıyor...',
        [ReadyState.OPEN]: '🟢 Bağlı',
        [ReadyState.CLOSING]: '🔴 Kesiliyor...',
        [ReadyState.CLOSED]: '🔴 Bağlantı kesildi',
        [ReadyState.UNINSTANTIATED]: '⚪ Başlatılmadı',
    }[readyState];
    
    const isConnected = readyState === ReadyState.OPEN;

    const isMyTurn = turn === myUserId;

    return (
        <div className="container mt-4">
            {disconnectWarning && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>⚠️ UYARI:</strong> Bağlantınız kesildi! 30 saniye içinde geri dönmezseniz oyunu kaybedersiniz!
                    <button 
                        type="button" 
                        className="btn-close" 
                        onClick={() => setDisconnectWarning(false)}
                    ></button>
                </div>
            )}

            <div className="card mb-4">
                <div className="card-body">
                    <div className="row align-items-center">
                        <div className="col-md-3">
                            <h4>🎮 Oda #{roomId}</h4>
                        </div>
                        <div className="col-md-3">
                            {playerBalances.myBalance !== null && (
                                <div className="alert alert-info mb-0 py-2">
                                    <small><strong>💰 Bakiye:</strong></small><br />
                                    <strong>{playerBalances.myBalance.toFixed(2)}</strong>
                                    <span className="text-danger ms-1">
                                        (-{playerBalances.betAmount.toFixed(2)})
                                    </span>
                                </div>
                            )}
                        </div>
                        <div className="col-md-3 text-center">
                            {gameStarted && !gameEnded && (
                                <div className={`alert ${isMyTurn ? 'alert-success' : 'alert-warning'} mb-0`}>
                                    <strong>
                                        {isMyTurn ? '🎯 Sıra Sende!' : `⏳ Sıra: ${turnName}`}
                                    </strong>
                                    <br />
                                    <small>{guessCount} tahmin yapıldı</small>
                                </div>
                            )}
                            {!gameStarted && !gameEnded && (
                                <div className="alert alert-info mb-0">
                                    <strong>⏳ Rakip bekleniyor...</strong>
                                    <br />
                                    <small>İkinci oyuncu katıldığında oyun başlayacak</small>
                                </div>
                            )}
                            {gameEnded && (
                                <div className="alert alert-success mb-0">
                                    🎉 Oyun Bitti!
                                    <br />
                                    <small>{guessCount} tahminde bulunuldu</small>
                                </div>
                            )}
                        </div>
                        <div className="col-md-3 text-end">
                            <div className={`badge ${isConnected ? 'bg-success' : 'bg-danger'} mb-2`}>
                                {connectionStatus}
                            </div>
                            <br />
                            <button 
                                className="btn btn-sm btn-secondary"
                                onClick={handleLeaveLobby}
                            >
                                Lobiye Dön
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row">
                {/* Oyun Alanı */}
                <div className="col-md-8">
                    <div className="card">
                        <div className="card-body text-center p-5">
                            <h5 className="mb-4">1-100 Arası Sayıyı Tahmin Et</h5>
                            
                            <div className="input-group input-group-lg mb-3">
            <input 
                type="number" 
                                    className="form-control text-center" 
                value={guess} 
                onChange={(e) => setGuess(e.target.value)} 
                                    onKeyPress={handleKeyPress}
                                    placeholder="Sayı gir..."
                                    min="1"
                                    max="100"
                                    disabled={!gameStarted || gameEnded || !isMyTurn}
            />
                                <button 
                                    onClick={makeGuess} 
                                    className="btn btn-warning"
                                    disabled={!gameStarted || gameEnded || !isMyTurn || !isConnected}
                                >
                                    {!isConnected ? '⏳ Bağlanıyor...' : 'Tahmin Et'}
                                </button>
                            </div>

                            {!isMyTurn && gameStarted && !gameEnded && (
                                <p className="text-muted">
                                    <em>Rakibinin hamlesini bekle...</em>
                                </p>
                            )}
                            
                            {!gameStarted && !gameEnded && (
                                <div className="alert alert-warning">
                                    <strong>🕐 Bekleme Odasındasın</strong>
                                    <p className="mb-0 mt-2">
                                        Başka bir oyuncu katıldığında oyun otomatik başlayacak.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Log Paneli */}
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header bg-dark text-white">
                            <strong>📜 Oyun Geçmişi</strong>
                            {gameStarted && (
                                <span className="badge bg-light text-dark float-end">
                                    {guessCount} tahmin
                                </span>
                            )}
                        </div>
                        <div 
                            className="card-body p-2" 
                            style={{
                                height: '400px', 
                                overflowY: 'scroll',
                                backgroundColor: '#f8f9fa'
                            }}
                        >
                            {logs.length === 0 ? (
                                <div className="text-center mt-5">
                                    <p className="text-muted">
                                        <em>Oyun başladığında burada hamleleri göreceksin.</em>
                                    </p>
                                </div>
                            ) : (
                                logs.map((log, i) => {
                                    const isMyGuess = log.guesserId === myUserId;
                                    
                                    return (
                                        <div 
                                            key={i} 
                                            className={`alert ${
                                                log.event === 'WINNER' ? 'alert-success' :
                                                log.event === 'START' ? 'alert-info' :
                                                log.event === 'ERROR' ? 'alert-danger' :
                                                isMyGuess ? 'alert-primary' : 'alert-warning'
                                            } py-2 px-3 mb-2 small`}
                                            style={{ 
                                                borderLeft: 
                                                    log.event === 'ERROR' ? '4px solid #dc3545' :
                                                    isMyGuess ? '4px solid #0d6efd' : '4px solid #ffc107'
                                            }}
                                        >
                                            <div className="d-flex justify-content-between align-items-start">
                                                <div style={{ flex: 1 }}>
                                                    {log.text}
                                                </div>
                                                {log.timestamp && (
                                                    <small className="text-muted ms-2" style={{ fontSize: '0.7rem' }}>
                                                        {log.timestamp}
                                                    </small>
                                                )}
                                            </div>
                                            {log.event === 'CONTINUE' && (
                                                <div className="mt-1">
                                                    <span className={`badge ${isMyGuess ? 'bg-primary' : 'bg-warning'}`}>
                                                        {isMyGuess ? 'Sen' : 'Rakip'}
                                                    </span>
                                                </div>
                                            )}
                                            {log.event === 'ERROR' && (
                                                <div className="mt-1">
                                                    <span className="badge bg-danger">Hata</span>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                            <div ref={logsEndRef} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GameBoard;