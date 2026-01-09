// app/depot/page.js
'use client';

import { useState } from 'react';
import { oeuvresAPI, authAPI } from '@/lib/api';
import { Form, Button, Alert, Card, Container } from 'react-bootstrap';

export default function DepotPage() {
  const [formData, setFormData] = useState({
    titre: '',
    auteur: ''
  });
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setMessage({ type: 'danger', text: 'Seuls les fichiers PDF sont acceptés' });
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setMessage({ type: 'danger', text: 'Le fichier est trop volumineux (max 50 MB)' });
        return;
      }
      setPdfFile(file);
      setMessage(null);
    }
  };

  const handlePreview = async () => {
    if (!pdfFile) {
      setMessage({ type: 'warning', text: 'Veuillez sélectionner un PDF' });
      return;
    }

    setLoading(true);
    setMessage({ type: 'info', text: 'Conversion en cours...' });

    try {
      const response = await oeuvresAPI.convertirPDF(pdfFile);
      
      if (response.success) {
        setPreview(response.contenu_md);
        setMessage({ type: 'success', text: 'Prévisualisation générée !' });
      }
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: err.response?.data?.error || 'Erreur lors de la conversion' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: 'info', text: 'Dépôt en cours...' });

    const data = new FormData();
    data.append('titre', formData.titre);
    data.append('auteur', formData.auteur);
    data.append('pdf', pdfFile);
    data.append('soumisPar', authAPI.getCurrentUser()?.email || 'membre@test.fr');

    try {
      const response = await oeuvresAPI.deposerPDF(data);
      
      if (response.success) {
        setMessage({ 
          type: 'success', 
          text: `✅ ${response.message}\n\nL'œuvre sera examinée par un bibliothécaire.` 
        });
        
        setFormData({ titre: '', auteur: '' });
        setPdfFile(null);
        setPreview(null);
        document.getElementById('pdfInput').value = '';
      }
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: err.response?.data?.error || 'Erreur lors du dépôt' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-4">
      <h2>📤 Déposer une Œuvre</h2>
      <p className="text-muted">
        Partagez vos œuvres numérisées avec la communauté. 
        Les fichiers PDF seront automatiquement convertis en Markdown.
      </p>

      {message && (
        <Alert 
          variant={message.type} 
          dismissible 
          onClose={() => setMessage(null)}
        >
          {message.text.split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Titre de l'œuvre *</Form.Label>
              <Form.Control
                type="text"
                name="titre"
                placeholder="Les Misérables"
                value={formData.titre}
                onChange={handleChange}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Auteur</Form.Label>
              <Form.Control
                type="text"
                name="auteur"
                placeholder="Victor Hugo"
                value={formData.auteur}
                onChange={handleChange}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Fichier PDF *</Form.Label>
              <Form.Control
                id="pdfInput"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                required
              />
              <Form.Text className="text-muted">
                Maximum 50 MB • Le PDF sera converti en Markdown avec OCR
              </Form.Text>
            </Form.Group>

            {pdfFile && (
              <Alert variant="info">
                📄 Fichier sélectionné : <strong>{pdfFile.name}</strong> ({(pdfFile.size / 1024 / 1024).toFixed(2)} MB)
              </Alert>
            )}

            <div className="d-flex gap-2">
              <Button 
                variant="outline-primary" 
                onClick={handlePreview}
                disabled={!pdfFile || loading}
              >
                👁️ Prévisualiser
              </Button>

              <Button 
                variant="primary" 
                type="submit"
                disabled={!pdfFile || loading}
              >
                {loading ? '⏳ Traitement...' : '✅ Déposer l\'œuvre'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      {preview && (
        <Card>
          <Card.Header className="bg-light">
            <h5 className="mb-0">📝 Prévisualisation du Markdown</h5>
          </Card.Header>
          <Card.Body>
            <div 
              dangerouslySetInnerHTML={{ __html: preview }}
              style={{ 
                maxHeight: '500px', 
                overflow: 'auto',
                border: '1px solid #dee2e6',
                padding: '15px',
                borderRadius: '5px'
              }}
            />
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}