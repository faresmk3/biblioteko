// app/catalogue/page.js
'use client';

import { useState, useEffect } from 'react';
import { catalogueAPI, empruntsAPI } from '@/lib/api';
import { Container, Card, Row, Col, Button, Badge, Alert } from 'react-bootstrap';

export default function CataloguePage() {
  const [oeuvres, setOeuvres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    chargerCatalogue();
  }, []);

  const chargerCatalogue = async () => {
    setLoading(true);
    try {
      const data = await catalogueAPI.getFondCommun();
      setOeuvres(data.oeuvres || []);
    } catch (err) {
      setMessage({ type: 'danger', text: 'Erreur de chargement' });
    } finally {
      setLoading(false);
    }
  };

  const handleEmprunter = async (idOeuvre, titre) => {
    if (!window.confirm(`Emprunter "${titre}" ?`)) return;
    try {
      await empruntsAPI.emprunter(idOeuvre, 14);
      setMessage({ type: 'success', text: '✅ Emprunt réussi' });
    } catch (err) {
      setMessage({ type: 'danger', text: 'Erreur' });
    }
  };

  return (
    <Container className="mt-4">
      <h2>📖 Catalogue</h2>
      {message && <Alert variant={message.type}>{message.text}</Alert>}
      <Row>
        {oeuvres.map((o) => (
          <Col key={o.id} md={4} className="mb-4">
            <Card>
              <Card.Body>
                <h5>{o.titre}</h5>
                <p>{o.auteur}</p>
                <Button onClick={() => handleEmprunter(o.id, o.titre)}>
                  Emprunter
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}