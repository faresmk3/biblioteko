// ============================================
// FICHIER CORRIGÉ: src/app/moderation/demandes/page.js
// AVEC VÉRIFICATION D'AUTHENTIFICATION
// ============================================
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { demandesAPI, authAPI } from '@/lib/api';
import { 
  Container, Card, Table, Button, Alert, Badge, 
  Spinner, Row, Col, Modal, Form 
} from 'react-bootstrap';

export default function GestionDemandesPage() {
  const router = useRouter();
  const [demandes, setDemandes] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  
  // Modal de refus
  const [showRefusModal, setShowRefusModal] = useState(false);
  const [demandeSelectionnee, setDemandeSelectionnee] = useState(null);
  const [motifRefus, setMotifRefus] = useState('');

  // 🔒 VÉRIFICATION D'AUTHENTIFICATION AU MONTAGE
  useEffect(() => {
    const checkAuth = () => {
      // Vérifier si l'utilisateur est authentifié
      if (!authAPI.isAuthenticated()) {
        console.log('[Auth] Non authentifié, redirection vers /login');
        router.push('/login');
        return false;
      }

      // Vérifier si l'utilisateur est bibliothécaire
      const user = authAPI.getCurrentUser();
      const isBibliothecaire = user?.roles?.includes('Bibliothécaire');
      
      if (!isBibliothecaire) {
        console.log('[Auth] Pas bibliothécaire, redirection vers /');
        setMessage({
          type: 'danger',
          text: '⛔ Accès refusé. Cette page est réservée aux bibliothécaires.'
        });
        setTimeout(() => router.push('/'), 2000);
        return false;
      }

      console.log('[Auth] ✅ Authentification vérifiée');
      setAuthChecked(true);
      return true;
    };

    if (checkAuth()) {
      chargerDemandes();
    }
  }, [router]);

  const chargerDemandes = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const response = await demandesAPI.listerEnAttente();
      setDemandes(response.demandes || []);
      setStats(response.stats || {});

      if (response.demandes && response.demandes.length === 0) {
        setMessage({ 
          type: 'info', 
          text: '✅ Aucune demande en attente. Tout est à jour !' 
        });
      }
    } catch (err) {
      console.error('Erreur chargement demandes:', err);
      
      if (err.response?.status === 401) {
        // Token expiré
        authAPI.logout();
        router.push('/login');
        return;
      }
      
      if (err.response?.status === 403) {
        setMessage({ 
          type: 'danger', 
          text: '⛔ Accès refusé. Vous devez être bibliothécaire.' 
        });
      } else {
        setMessage({ 
          type: 'danger', 
          text: `❌ Erreur : ${err.response?.data?.error || err.message}` 
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApprouver = async (demande) => {
    if (!window.confirm(
      `⚠️ Promouvoir ${demande.nom_demandeur} en bibliothécaire ?\n\n` +
      `Cette action donnera à cette personne les permissions de modération.`
    )) {
      return;
    }

    setActionLoading(demande.id);

    try {
      const response = await demandesAPI.approuver(demande.id);
      
      setMessage({ 
        type: 'success', 
        text: `✅ ${response.message || 'Demande approuvée avec succès'}\n\n${demande.nom_demandeur} peut maintenant modérer les œuvres.` 
      });
      
      // Recharger la liste
      setTimeout(() => chargerDemandes(), 1000);
    } catch (err) {
      if (err.response?.status === 401) {
        authAPI.logout();
        router.push('/login');
        return;
      }
      
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || 'Impossible d\'approuver'}` 
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleRefuserClick = (demande) => {
    setDemandeSelectionnee(demande);
    setMotifRefus('');
    setShowRefusModal(true);
  };

  const handleRefuserConfirm = async () => {
    if (motifRefus.length < 5) {
      alert('⚠️ Le motif doit contenir au moins 5 caractères');
      return;
    }

    setActionLoading(demandeSelectionnee.id);

    try {
      const response = await demandesAPI.refuser(demandeSelectionnee.id, motifRefus);
      
      setMessage({ 
        type: 'warning', 
        text: `🚫 Demande de ${demandeSelectionnee.nom_demandeur} refusée.\n\nMotif : ${motifRefus}` 
      });
      
      // Fermer le modal et recharger
      setShowRefusModal(false);
      setDemandeSelectionnee(null);
      setMotifRefus('');
      
      setTimeout(() => chargerDemandes(), 1000);
    } catch (err) {
      if (err.response?.status === 401) {
        authAPI.logout();
        router.push('/login');
        return;
      }
      
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || 'Impossible de refuser'}` 
      });
    } finally {
      setActionLoading(null);
    }
  };

  // 🔒 NE PAS AFFICHER LA PAGE TANT QUE L'AUTH N'EST PAS VÉRIFIÉE
  if (!authChecked) {
    return (
      <Container className="mt-5">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Vérification...</span>
          </Spinner>
          <p className="mt-3 text-muted">Vérification des permissions...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      {/* En-tête */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>📋 Demandes de Promotion</h2>
          <p className="text-muted mb-0">
            Gérez les demandes de promotion en bibliothécaire
          </p>
        </div>
        <Button 
          variant="outline-primary" 
          size="sm"
          onClick={chargerDemandes}
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
          {message.text.split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </Alert>
      )}

      {/* Statistiques */}
      {stats && !loading && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted mb-2">En attente</h6>
                <h2 className="mb-0 text-warning">{stats.en_attente || 0}</h2>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted mb-2">Approuvées</h6>
                <h2 className="mb-0 text-success">{stats.approuvees || 0}</h2>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted mb-2">Refusées</h6>
                <h2 className="mb-0 text-danger">{stats.refusees || 0}</h2>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted mb-2">Délai moyen</h6>
                <h2 className="mb-0 text-info">
                  {stats.delai_moyen_jours ? stats.delai_moyen_jours.toFixed(1) : '0'} j
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
          <p className="mt-3 text-muted">Chargement des demandes...</p>
        </div>
      ) : demandes.length === 0 ? (
        /* État vide */
        <Card className="text-center py-5">
          <Card.Body>
            <div style={{ fontSize: '4rem' }}>✅</div>
            <h4 className="mt-3">Aucune demande en attente</h4>
            <p className="text-muted">
              Toutes les demandes ont été traitées !
            </p>
          </Card.Body>
        </Card>
      ) : (
        /* Tableau des demandes */
        <Card>
          <Card.Header className="bg-primary text-white">
            <h5 className="mb-0">Demandes en attente de traitement</h5>
          </Card.Header>
          <Card.Body className="p-0">
            <Table responsive hover className="mb-0">
              <thead className="table-light">
                <tr>
                  <th>Demandeur</th>
                  <th>Email</th>
                  <th style={{ minWidth: '250px' }}>Motivation</th>
                  <th>Date demande</th>
                  <th className="text-center">Délai</th>
                  <th className="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {demandes.map((demande) => (
                  <tr key={demande.id}>
                    <td>
                      <strong>{demande.nom_demandeur}</strong>
                    </td>
                    <td>
                      <small className="text-muted">{demande.email_demandeur}</small>
                    </td>
                    <td>
                      <div 
                        style={{ 
                          maxHeight: '60px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                        title={demande.motivation}
                      >
                        <small className="text-muted" style={{ fontStyle: 'italic' }}>
                          "{demande.motivation}"
                        </small>
                      </div>
                    </td>
                    <td>
                      <small>
                        {new Date(demande.date_demande).toLocaleDateString('fr-FR')}
                      </small>
                    </td>
                    <td className="text-center">
                      <Badge 
                        bg={
                          demande.delai_jours > 7 ? 'success' :
                          demande.delai_jours > 3 ? 'warning' :
                          'danger'
                        }
                      >
                        {demande.delai_jours} jour(s)
                      </Badge>
                    </td>
                    <td className="text-center">
                      <div className="d-flex gap-2 justify-content-center">
                        <Button 
                          size="sm" 
                          variant="success"
                          onClick={() => handleApprouver(demande)}
                          disabled={actionLoading === demande.id}
                          title="Approuver et promouvoir en bibliothécaire"
                        >
                          {actionLoading === demande.id ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            '✅ Approuver'
                          )}
                        </Button>

                        <Button 
                          size="sm" 
                          variant="danger"
                          onClick={() => handleRefuserClick(demande)}
                          disabled={actionLoading === demande.id}
                          title="Refuser cette demande"
                        >
                          ✗ Refuser
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

      {/* Modal de refus */}
      <Modal 
        show={showRefusModal} 
        onHide={() => setShowRefusModal(false)}
        centered
      >
        <Modal.Header closeButton className="bg-danger text-white">
          <Modal.Title>🚫 Refuser la demande</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {demandeSelectionnee && (
            <>
              <Alert variant="light">
                <strong>Demandeur :</strong> {demandeSelectionnee.nom_demandeur}<br/>
                <strong>Email :</strong> {demandeSelectionnee.email_demandeur}
              </Alert>

              <div className="mb-3 p-3 bg-light rounded">
                <strong>Motivation :</strong>
                <p className="mt-2 mb-0" style={{ fontStyle: 'italic' }}>
                  "{demandeSelectionnee.motivation}"
                </p>
              </div>

              <Form.Group>
                <Form.Label>
                  Motif du refus <span className="text-danger">*</span>
                </Form.Label>
                <Form.Control
                  as="textarea"
                  rows={4}
                  value={motifRefus}
                  onChange={(e) => setMotifRefus(e.target.value)}
                  placeholder="Expliquez pourquoi vous refusez cette demande...

Exemples :
- Manque d'expérience sur la plateforme
- Motivation insuffisante
- Besoin de plus de détails
- Autre raison..."
                  required
                />
                <Form.Text className="text-muted">
                  {motifRefus.length}/5 caractères minimum
                  {motifRefus.length >= 5 && (
                    <Badge bg="success" className="ms-2">✓ Minimum atteint</Badge>
                  )}
                </Form.Text>
              </Form.Group>

              <Alert variant="warning" className="mt-3 mb-0">
                ⚠️ L'utilisateur sera notifié du refus et recevra ce motif.
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowRefusModal(false)}
            disabled={actionLoading}
          >
            Annuler
          </Button>
          <Button 
            variant="danger" 
            onClick={handleRefuserConfirm}
            disabled={motifRefus.length < 5 || actionLoading}
          >
            {actionLoading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Refus en cours...
              </>
            ) : (
              'Confirmer le refus'
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Info supplémentaire */}
      {!loading && demandes.length > 0 && (
        <Alert variant="light" className="mt-4">
          <small>
            💡 <strong>Bon à savoir :</strong>
            <ul className="mb-0 mt-2">
              <li>L'approbation promeut automatiquement le membre en bibliothécaire</li>
              <li>Le refus nécessite un motif qui sera communiqué au demandeur</li>
              <li>Un délai de traitement moyen de 2-3 jours est recommandé</li>
            </ul>
          </small>
        </Alert>
      )}
    </Container>
  );
}