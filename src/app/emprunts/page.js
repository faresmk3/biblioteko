// app/emprunts/page.js
'use client';

import { useState, useEffect } from 'react';
import { empruntsAPI, authAPI } from '@/lib/api';
import { Container, Table, Button, Alert, Card, Badge, Spinner, Row, Col } from 'react-bootstrap';

export default function EmpruntsPage() {
  const [emprunts, setEmprunts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    chargerEmprunts();
  }, []);

  const chargerEmprunts = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      const data = await empruntsAPI.getMesEmprunts();
      setEmprunts(data.emprunts || []);
      
      if (data.emprunts && data.emprunts.length === 0) {
        setMessage({ 
          type: 'info', 
          text: '📚 Vous n\'avez aucun emprunt en cours. Consultez le catalogue pour emprunter des œuvres !' 
        });
      }
    } catch (err) {
      console.error('Erreur chargement emprunts:', err);
      
      if (err.response?.status === 401) {
        setMessage({ 
          type: 'danger', 
          text: '🔒 Vous devez être connecté pour voir vos emprunts.' 
        });
      } else if (err.response?.status === 403) {
        setMessage({ 
          type: 'danger', 
          text: '⛔ Vous n\'avez pas les permissions nécessaires.' 
        });
      } else {
        setMessage({ 
          type: 'danger', 
          text: `❌ Erreur lors du chargement : ${err.response?.data?.error || err.message}` 
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetour = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir retourner cette œuvre ?')) {
      return;
    }

    setActionLoading(id);
    
    try {
      const result = await empruntsAPI.retourner(id);
      setMessage({ 
        type: 'success', 
        text: `✅ ${result.message || 'Œuvre retournée avec succès'}` 
      });
      
      // Recharger la liste
      setTimeout(() => chargerEmprunts(), 500);
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || 'Impossible de retourner l\'œuvre'}` 
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleRenouveler = async (id) => {
    setActionLoading(id);
    
    try {
      const result = await empruntsAPI.renouveler(id, 7);
      setMessage({ 
        type: 'success', 
        text: `✅ ${result.message || 'Emprunt prolongé de 7 jours'}` 
      });
      
      // Recharger la liste
      setTimeout(() => chargerEmprunts(), 500);
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || 'Impossible de renouveler'}` 
      });
    } finally {
      setActionLoading(null);
    }
  };

  const getStatutBadge = (emprunt) => {
    const joursRestants = emprunt.jours_restants || 0;
    const expire = emprunt.est_expire || false;

    if (expire) {
      return <Badge bg="danger">⏰ Expiré</Badge>;
    } else if (joursRestants <= 2) {
      return <Badge bg="warning" text="dark">⚠️ Bientôt expiré</Badge>;
    } else if (joursRestants <= 7) {
      return <Badge bg="info">🕒 {joursRestants}j restants</Badge>;
    } else {
      return <Badge bg="success">✅ {joursRestants}j restants</Badge>;
    }
  };

  return (
    <Container className="mt-4">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>📚 Mes Emprunts</h2>
        <Button 
          variant="outline-primary" 
          size="sm"
          onClick={chargerEmprunts}
          disabled={loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : '🔄 Actualiser'}
        </Button>
      </div>

      {/* Messages */}
      {message && (
        <Alert 
          variant={message.type} 
          dismissible 
          onClose={() => setMessage(null)}
          className="mb-4"
        >
          {message.text}
        </Alert>
      )}

      {/* Statistiques */}
      {!loading && emprunts.length > 0 && (
        <Row className="mb-4">
          <Col md={4}>
            <Card className="text-center">
              <Card.Body>
                <h5 className="text-muted mb-2">Total Emprunts</h5>
                <h2 className="mb-0">{emprunts.length}</h2>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="text-center">
              <Card.Body>
                <h5 className="text-muted mb-2">Expirés</h5>
                <h2 className="mb-0 text-danger">
                  {emprunts.filter(e => e.est_expire).length}
                </h2>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="text-center">
              <Card.Body>
                <h5 className="text-muted mb-2">Bientôt expirés</h5>
                <h2 className="mb-0 text-warning">
                  {emprunts.filter(e => !e.est_expire && e.jours_restants <= 3).length}
                </h2>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Loading */}
      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Chargement...</span>
          </Spinner>
          <p className="mt-3 text-muted">Chargement de vos emprunts...</p>
        </div>
      ) : emprunts.length === 0 ? (
        /* État vide */
        <Card className="text-center py-5">
          <Card.Body>
            <div style={{ fontSize: '4rem' }}>📚</div>
            <h4 className="mt-3">Aucun emprunt en cours</h4>
            <p className="text-muted">
              Vous n'avez pas encore emprunté d'œuvres.
            </p>
            <Button 
              variant="primary" 
              href="/catalogue"
              className="mt-3"
            >
              📖 Parcourir le Catalogue
            </Button>
          </Card.Body>
        </Card>
      ) : (
        /* Tableau des emprunts */
        <Card>
          <Card.Body className="p-0">
            <Table responsive hover className="mb-0">
              <thead className="table-light">
                <tr>
                  <th>Œuvre</th>
                  <th>Date Début</th>
                  <th>Date Fin</th>
                  <th className="text-center">Statut</th>
                  <th className="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {emprunts.map((emprunt) => (
                  <tr key={emprunt.id}>
                    <td>
                      <div>
                        <strong>{emprunt.oeuvre}</strong>
                      </div>
                      <small className="text-muted">ID: {emprunt.id}</small>
                    </td>
                    <td>
                      {emprunt.date_debut ? 
                        new Date(emprunt.date_debut).toLocaleDateString('fr-FR') 
                        : 'N/A'}
                    </td>
                    <td>
                      {emprunt.date_fin ? 
                        new Date(emprunt.date_fin).toLocaleDateString('fr-FR') 
                        : 'N/A'}
                    </td>
                    <td className="text-center">
                      {getStatutBadge(emprunt)}
                    </td>
                    <td className="text-center">
                      <div className="d-flex gap-2 justify-content-center">
                        {/* Bouton Renouveler (désactivé si expiré) */}
                        <Button 
                          size="sm" 
                          variant="outline-primary"
                          onClick={() => handleRenouveler(emprunt.id)}
                          disabled={
                            actionLoading === emprunt.id || 
                            emprunt.est_expire
                          }
                          title={emprunt.est_expire ? 
                            "Impossible de renouveler un emprunt expiré" : 
                            "Prolonger de 7 jours"}
                        >
                          {actionLoading === emprunt.id ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            '🔄 Renouveler'
                          )}
                        </Button>

                        {/* Bouton Retourner */}
                        <Button 
                          size="sm" 
                          variant="outline-danger"
                          onClick={() => handleRetour(emprunt.id)}
                          disabled={actionLoading === emprunt.id}
                        >
                          {actionLoading === emprunt.id ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            '↩️ Retourner'
                          )}
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}

      {/* Info supplémentaire */}
      {!loading && emprunts.length > 0 && (
        <Alert variant="light" className="mt-4">
          <small>
            💡 <strong>Astuce :</strong> Vous pouvez renouveler un emprunt avant qu'il n'expire. 
            Les œuvres expirées doivent être retournées.
          </small>
        </Alert>
      )}
    </Container>
  );
}