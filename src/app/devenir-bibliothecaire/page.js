// ============================================
// NOUVEAU FICHIER: src/app/devenir-bibliothecaire/page.js
// ============================================
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { demandesAPI } from '@/lib/api';
import { Form, Button, Alert, Card, Container, Badge } from 'react-bootstrap';

export default function DevenirBibliothecairePage() {
  const [motivation, setMotivation] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (motivation.length < 10) {
      setMessage({ 
        type: 'warning', 
        text: '⚠️ La motivation doit contenir au moins 10 caractères' 
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await demandesAPI.soumettre(motivation);
      
      if (response.success) {
        setMessage({ 
          type: 'success', 
          text: `✅ ${response.message}\n\n📋 Votre demande a été soumise avec succès !\n\n⏳ Un bibliothécaire l'examinera prochainement.` 
        });
        
        setMotivation('');
        
        // Redirection après 3 secondes
        setTimeout(() => {
          router.push('/mes-demandes');
        }, 3000);
      }
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ ${err.response?.data?.error || 'Erreur lors de la soumission'}` 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>🎓 Devenir Bibliothécaire</h2>
        <Badge bg="info">Demande de promotion</Badge>
      </div>

      <Alert variant="info" className="mb-4">
        <strong>📋 Processus de demande :</strong>
        <ol className="mb-0 mt-2">
          <li>Expliquez votre motivation (minimum 10 caractères)</li>
          <li>Soumettez votre demande</li>
          <li>Un bibliothécaire examinera votre demande</li>
          <li>Vous serez notifié de la décision</li>
        </ol>
      </Alert>

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

      <Card>
        <Card.Header className="bg-primary text-white">
          <h5 className="mb-0">📝 Formulaire de demande</h5>
        </Card.Header>
        <Card.Body>
          <Alert variant="light">
            <strong>💡 Qu'est-ce qu'un bibliothécaire ?</strong>
            <p className="mb-0 mt-2">
              En tant que bibliothécaire, vous pourrez :
            </p>
            <ul className="mb-0">
              <li>Modérer les œuvres soumises par les membres</li>
              <li>Valider ou rejeter les soumissions</li>
              <li>Contribuer à la qualité du catalogue</li>
              <li>Aider à gérer les demandes de promotion</li>
            </ul>
          </Alert>

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>
                Motivation <span className="text-danger">*</span>
              </Form.Label>
              <Form.Control
                as="textarea"
                rows={6}
                value={motivation}
                onChange={(e) => setMotivation(e.target.value)}
                placeholder="Expliquez pourquoi vous souhaitez devenir bibliothécaire...

Exemple :
- Votre expérience avec la plateforme
- Vos compétences en modération de contenu
- Votre disponibilité
- Votre motivation à contribuer"
                required
                disabled={loading}
              />
              <Form.Text className="text-muted">
                {motivation.length}/10 caractères minimum
                {motivation.length >= 10 && (
                  <Badge bg="success" className="ms-2">✓ Minimum atteint</Badge>
                )}
              </Form.Text>
            </Form.Group>

            <Alert variant="warning">
              ⚠️ Une fois soumise, votre demande ne pourra plus être modifiée. 
              Vous pourrez seulement l'annuler si elle est toujours en attente.
            </Alert>

            <div className="d-flex gap-2">
              <Button 
                variant="secondary"
                onClick={() => router.back()}
                disabled={loading}
              >
                ← Retour
              </Button>

              <Button 
                variant="primary" 
                type="submit"
                disabled={loading || motivation.length < 10}
                className="flex-grow-1"
              >
                {loading ? '⏳ Envoi en cours...' : '✅ Soumettre ma demande'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      <Card className="mt-4">
        <Card.Body>
          <h6>❓ Questions fréquentes</h6>
          <div className="mt-3">
            <strong>Combien de temps faut-il pour obtenir une réponse ?</strong>
            <p className="text-muted">En général, les demandes sont traitées sous 2-3 jours ouvrés.</p>

            <strong>Puis-je faire plusieurs demandes ?</strong>
            <p className="text-muted">Vous ne pouvez avoir qu'une seule demande en attente à la fois.</p>

            <strong>Que se passe-t-il si ma demande est refusée ?</strong>
            <p className="text-muted">Vous recevrez un motif et pourrez refaire une demande ultérieurement.</p>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}