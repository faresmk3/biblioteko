// ============================================
// NOUVEAU FICHIER: src/app/mes-demandes/page.js
// ============================================
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { demandesAPI } from '@/lib/api';
import { Container, Card, Button, Alert, Badge, Spinner, Row, Col } from 'react-bootstrap';

export default function MesDemandesPage() {
  const [demandes, setDemandes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const router = useRouter();

  useEffect(() => {
    chargerDemandes();
  }, []);

  const chargerDemandes = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const response = await demandesAPI.mesDemandes();
      setDemandes(response.demandes || []);

      if (response.demandes && response.demandes.length === 0) {
        setMessage({ 
          type: 'info', 
          text: '📋 Vous n\'avez fait aucune demande de promotion.' 
        });
      }
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || 'Impossible de charger les demandes'}` 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAnnuler = async (idDemande) => {
    if (!window.confirm('⚠️ Êtes-vous sûr de vouloir annuler cette demande ?')) {
      return;
    }

    setActionLoading(idDemande);

    try {
      const response = await demandesAPI.annuler(idDemande);
      setMessage({ 
        type: 'success', 
        text: '✅ Demande annulée avec succès' 
      });
      
      setTimeout(() => chargerDemandes(), 500);
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ ${err.response?.data?.error || 'Impossible d\'annuler'}` 
      });
    } finally {
      setActionLoading(null);
    }
  };

  const getStatutBadge = (statut) => {
    const badges = {
      'en_attente': { bg: 'warning', text: 'dark', icon: '⏳', label: 'En attente' },
      'approuvee': { bg: 'success', text: 'white', icon: '✅', label: 'Approuvée' },
      'refusee': { bg: 'danger', text: 'white', icon: '❌', label: 'Refusée' },
      'annulee': { bg: 'secondary', text: 'white', icon: '🚫', label: 'Annulée' }
    };

    const badge = badges[statut] || badges['en_attente'];
    
    return (
      <Badge bg={badge.bg} text={badge.text}>
        {badge.icon} {badge.label}
      </Badge>
    );
  };

  const getCardClass = (statut) => {
    const classes = {
      'en_attente': 'border-warning',
      'approuvee': 'border-success',
      'refusee': 'border-danger',
      'annulee': 'border-secondary'
    };
    return classes[statut] || '';
  };

  return (
    <Container className="mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>📋 Mes demandes de promotion</h2>
        <div className="d-flex gap-2">
          <Button 
            variant="outline-primary" 
            size="sm"
            onClick={chargerDemandes}
            disabled={loading}
          >
            {loading ? <Spinner animation="border" size="sm" /> : '🔄 Actualiser'}
          </Button>
          <Button 
            variant="primary" 
            size="sm"
            onClick={() => router.push('/devenir-bibliothecaire')}
          >
            ➕ Nouvelle demande
          </Button>
        </div>
      </div>

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

      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Chargement...</span>
          </Spinner>
          <p className="mt-3 text-muted">Chargement de vos demandes...</p>
        </div>
      ) : demandes.length === 0 ? (
        <Card className="text-center py-5">
          <Card.Body>
            <div style={{ fontSize: '4rem' }}>🎓</div>
            <h4 className="mt-3">Aucune demande</h4>
            <p className="text-muted">
              Vous n'avez pas encore fait de demande pour devenir bibliothécaire.
            </p>
            <Button 
              variant="primary" 
              onClick={() => router.push('/devenir-bibliothecaire')}
              className="mt-3"
            >
              ➕ Faire une demande
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {demandes.map((demande) => (
            <Col key={demande.id} md={12} className="mb-4">
              <Card className={`${getCardClass(demande.statut)} border-3`}>
                <Card.Header className="bg-light">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      {getStatutBadge(demande.statut)}
                      <small className="text-muted ms-3">
                        ID: {demande.id}
                      </small>
                    </div>
                    <small className="text-muted">
                      📅 Soumise le {new Date(demande.date_demande).toLocaleDateString('fr-FR')}
                    </small>
                  </div>
                </Card.Header>

                <Card.Body>
                  <h6 className="text-muted mb-2">Motivation :</h6>
                  <Card.Text 
                    className="mb-3 p-3 bg-light rounded" 
                    style={{ 
                      borderLeft: '4px solid #0d6efd',
                      fontStyle: 'italic' 
                    }}
                  >
                    "{demande.motivation}"
                  </Card.Text>

                  {demande.statut === 'en_attente' && (
                    <Alert variant="info" className="mb-0">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          ⏳ <strong>En attente de traitement</strong>
                          <div className="small mt-1">
                            Délai : {demande.delai_jours} jour(s)
                          </div>
                        </div>
                        <Button 
                          variant="outline-danger" 
                          size="sm"
                          onClick={() => handleAnnuler(demande.id)}
                          disabled={actionLoading === demande.id}
                        >
                          {actionLoading === demande.id ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            '🚫 Annuler'
                          )}
                        </Button>
                      </div>
                    </Alert>
                  )}

                  {demande.statut === 'approuvee' && (
                    <Alert variant="success" className="mb-0">
                      <strong>✅ Demande approuvée !</strong>
                      <div className="small mt-1">
                        Vous êtes maintenant bibliothécaire. 
                        Vous pouvez accéder à la modération depuis le menu.
                      </div>
                      {demande.date_reponse && (
                        <div className="small mt-2 text-muted">
                          Traitée le {new Date(demande.date_reponse).toLocaleDateString('fr-FR')}
                          {demande.traite_par && ` par ${demande.traite_par}`}
                        </div>
                      )}
                    </Alert>
                  )}

                  {demande.statut === 'refusee' && (
                    <Alert variant="danger" className="mb-0">
                      <strong>❌ Demande refusée</strong>
                      {demande.motif_refus && (
                        <div className="mt-2">
                          <strong>Motif :</strong> {demande.motif_refus}
                        </div>
                      )}
                      {demande.date_reponse && (
                        <div className="small mt-2 text-muted">
                          Traitée le {new Date(demande.date_reponse).toLocaleDateString('fr-FR')}
                          {demande.traite_par && ` par ${demande.traite_par}`}
                        </div>
                      )}
                      <div className="mt-3">
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          onClick={() => router.push('/devenir-bibliothecaire')}
                        >
                          ➕ Faire une nouvelle demande
                        </Button>
                      </div>
                    </Alert>
                  )}

                  {demande.statut === 'annulee' && (
                    <Alert variant="secondary" className="mb-0">
                      <strong>🚫 Demande annulée</strong>
                      <div className="small mt-1">
                        Vous avez annulé cette demande.
                      </div>
                      {demande.date_reponse && (
                        <div className="small mt-2 text-muted">
                          Annulée le {new Date(demande.date_reponse).toLocaleDateString('fr-FR')}
                        </div>
                      )}
                    </Alert>
                  )}
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {!loading && demandes.length > 0 && (
        <Alert variant="light" className="mt-4">
          <small>
            💡 <strong>Bon à savoir :</strong> 
            Vous pouvez suivre l'état de vos demandes en temps réel. 
            Les demandes approuvées vous donnent immédiatement accès aux fonctionnalités de modération.
          </small>
        </Alert>
      )}
    </Container>
  );
}