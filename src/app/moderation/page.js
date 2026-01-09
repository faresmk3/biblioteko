// app/moderation/page.js
'use client';

import { useState, useEffect } from 'react';
import { oeuvresAPI } from '@/lib/api';
import { Container, Table, Button, Alert } from 'react-bootstrap';

export default function ModerationPage() {
  const [oeuvres, setOeuvres] = useState([]);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    chargerOeuvres();
  }, []);

  const chargerOeuvres = async () => {
    try {
      const data = await oeuvresAPI.getOeuvres();
      setOeuvres(data);
    } catch (err) {
      setMessage({ type: 'danger', text: 'Erreur' });
    }
  };

  const handleAction = async (action, id) => {
    try {
      if (action === 'traiter') await oeuvresAPI.traiter(id);
      if (action === 'valider') await oeuvresAPI.valider(id);
      setMessage({ type: 'success', text: 'Action effectuée' });
      chargerOeuvres();
    } catch (err) {
      setMessage({ type: 'danger', text: 'Erreur' });
    }
  };

  return (
    <Container className="mt-4">
      <h2>🔍 Modération</h2>
      {message && <Alert variant={message.type}>{message.text}</Alert>}
      <Table>
        <thead>
          <tr>
            <th>Titre</th>
            <th>État</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {oeuvres.map((o) => (
            <tr key={o.id}>
              <td>{o.titre}</td>
              <td>{o.etat}</td>
              <td>
                {o.etat === 'SOUMISE' && (
                  <Button size="sm" onClick={() => handleAction('traiter', o.id)}>
                    Traiter
                  </Button>
                )}
                {o.etat === 'EN_TRAITEMENT' && (
                  <Button size="sm" onClick={() => handleAction('valider', o.id)}>
                    Valider
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
}