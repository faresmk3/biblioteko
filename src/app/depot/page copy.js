// app/depot/page.js
'use client';

import { useState } from 'react';
import { oeuvresAPI, authAPI } from '@/lib/api';
import { Form, Button, Alert, Card, Container, Tabs, Tab, Badge } from 'react-bootstrap';

export default function DepotPage() {
  // Étape 1 : Informations de base
  const [formData, setFormData] = useState({
    titre: '',
    auteur: ''
  });
  
  // Étape 2 : PDF et conversion
  const [pdfFile, setPdfFile] = useState(null);
  const [markdownContent, setMarkdownContent] = useState('');
  const [isConverted, setIsConverted] = useState(false);
  
  // États UI
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);

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
        setMessage({ type: 'danger', text: '❌ Seuls les fichiers PDF sont acceptés' });
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setMessage({ type: 'danger', text: '❌ Le fichier est trop volumineux (max 50 MB)' });
        return;
      }
      setPdfFile(file);
      setIsConverted(false);
      setMarkdownContent('');
      setMessage({ type: 'info', text: '📄 PDF sélectionné. Cliquez sur "Convertir en Markdown"' });
    }
  };

  // ÉTAPE 2 : Conversion PDF → Markdown
  const handleConvert = async () => {
    if (!pdfFile) {
      setMessage({ type: 'warning', text: '⚠️ Veuillez d\'abord sélectionner un PDF' });
      return;
    }

    setLoading(true);
    setMessage({ type: 'info', text: '🔄 Conversion PDF → Markdown en cours... (30-60 secondes)' });

    try {
      const response = await oeuvresAPI.convertirPDF(pdfFile);
      
      if (response.success) {
        setMarkdownContent(response.contenu_md);
        setIsConverted(true);
        setCurrentStep(2);
        setMessage({ 
          type: 'success', 
          text: '✅ Conversion réussie ! Vous pouvez éditer le Markdown avant soumission.' 
        });
      }
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || err.message}` 
      });
    } finally {
      setLoading(false);
    }
  };

  // ÉTAPE 3 : Soumission du Markdown
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!markdownContent || !isConverted) {
      setMessage({ type: 'warning', text: '⚠️ Convertissez d\'abord le PDF' });
      return;
    }

    if (!formData.titre.trim()) {
      setMessage({ type: 'warning', text: '⚠️ Le titre est obligatoire' });
      return;
    }

    setLoading(true);
    setMessage({ type: 'info', text: '📤 Soumission en cours...' });

    const data = new FormData();
    data.append('titre', formData.titre);
    data.append('auteur', formData.auteur || 'Auteur inconnu');
    data.append('contenu_markdown', markdownContent);
    data.append('soumisPar', authAPI.getCurrentUser()?.email || 'membre@test.fr');

    try {
      const response = await oeuvresAPI.deposerMarkdown(data);
      
      if (response.success) {
        setMessage({ 
          type: 'success', 
          text: `✅ ${response.message}\n\n📚 "${formData.titre}" soumise avec succès !\n\n⏳ Un bibliothécaire l'examinera.` 
        });
        
        // Réinitialisation
        setFormData({ titre: '', auteur: '' });
        setPdfFile(null);
        setMarkdownContent('');
        setIsConverted(false);
        setCurrentStep(1);
        document.getElementById('pdfInput').value = '';
      }
    } catch (err) {
      setMessage({ 
        type: 'danger', 
        text: `❌ Erreur : ${err.response?.data?.error || 'Impossible de soumettre'}` 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>📤 Déposer une Œuvre</h2>
        <Badge bg="primary">Étape {currentStep}/3</Badge>
      </div>

      <Alert variant="info" className="mb-4">
        <strong>📋 Workflow :</strong>
        <ol className="mb-0 mt-2">
          <li>Sélectionnez un PDF</li>
          <li>Convertissez en Markdown (OCR automatique)</li>
          <li>Éditez si nécessaire</li>
          <li>Soumettez le Markdown (le PDF ne sera pas conservé)</li>
        </ol>
      </Alert>

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

      {/* ÉTAPE 1 : Upload PDF */}
      <Card className="mb-4">
        <Card.Header className="bg-primary text-white">
          <h5 className="mb-0">1️⃣ Informations et Upload PDF</h5>
        </Card.Header>
        <Card.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Titre *</Form.Label>
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
              <Form.Label>Fichier PDF source *</Form.Label>
              <Form.Control
                id="pdfInput"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                required
              />
              <Form.Text className="text-muted">
                Max 50 MB • Sera converti puis supprimé
              </Form.Text>
            </Form.Group>

            {pdfFile && (
              <Alert variant="success">
                ✅ <strong>{pdfFile.name}</strong> ({(pdfFile.size / 1024 / 1024).toFixed(2)} MB)
              </Alert>
            )}

            <Button 
              variant="primary" 
              onClick={handleConvert}
              disabled={!pdfFile || loading || isConverted}
              className="w-100"
            >
              {loading ? '⏳ Conversion...' : isConverted ? '✅ Converti' : '🔄 Convertir en Markdown'}
            </Button>
          </Form>
        </Card.Body>
      </Card>

      {/* ÉTAPE 2 : Édition Markdown */}
      {isConverted && (
        <Card className="mb-4">
          <Card.Header className="bg-success text-white">
            <h5 className="mb-0">2️⃣ Édition du Markdown</h5>
          </Card.Header>
          <Card.Body>
            <Tabs defaultActiveKey="edit" className="mb-3">
              <Tab eventKey="edit" title="✏️ Éditer">
                <Form.Group>
                  <Form.Label>Contenu Markdown</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={15}
                    value={markdownContent}
                    onChange={(e) => setMarkdownContent(e.target.value)}
                    style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
                  />
                  <Form.Text className="text-muted">
                    Corrigez les erreurs OCR si nécessaire
                  </Form.Text>
                </Form.Group>
              </Tab>

              <Tab eventKey="preview" title="👁️ Prévisualisation">
                <div 
                  dangerouslySetInnerHTML={{ __html: markdownContent }}
                  style={{ 
                    maxHeight: '500px', 
                    overflow: 'auto',
                    border: '1px solid #dee2e6',
                    padding: '20px',
                    borderRadius: '5px',
                    backgroundColor: '#f8f9fa'
                  }}
                />
              </Tab>
            </Tabs>

            <Alert variant="warning">
              ⚠️ Seul le Markdown sera enregistré. Le PDF ne sera pas conservé.
            </Alert>
          </Card.Body>
        </Card>
      )}

      {/* ÉTAPE 3 : Soumission */}
      {isConverted && (
        <Card className="mb-4">
          <Card.Header className="bg-info text-white">
            <h5 className="mb-0">3️⃣ Soumission</h5>
          </Card.Header>
          <Card.Body>
            <p>
              L'œuvre sera ajoutée à la file de modération.
            </p>

            <div className="d-flex gap-2">
              <Button 
                variant="secondary" 
                onClick={() => {
                  setIsConverted(false);
                  setMarkdownContent('');
                  setCurrentStep(1);
                }}
              >
                ↩️ Recommencer
              </Button>

              <Button 
                variant="success" 
                onClick={handleSubmit}
                disabled={loading || !markdownContent}
                className="flex-grow-1"
              >
                {loading ? '⏳ Soumission...' : '✅ Soumettre (Markdown)'}
              </Button>
            </div>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}