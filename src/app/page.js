// app/page.js
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Container } from 'react-bootstrap';
import Link from 'next/link';
import { authAPI } from '@/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (authAPI.isAuthenticated()) {
      router.push('/catalogue');
    }
  }, [router]);

  return (
    <Container className="mt-5">
      <div className="text-center">
        <h1 className="display-4 mb-4">📚 Bienvenue sur Biblioteko</h1>
        <p className="lead mb-4">
          La bibliothèque numérique collaborative de CultureDiffusion
        </p>
        
        <div className="row mt-5">
          <div className="col-md-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">📖 Catalogue Libre</h5>
                <p className="card-text">
                  Accédez gratuitement aux œuvres du domaine public
                </p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">📤 Partage d'Œuvres</h5>
                <p className="card-text">
                  Numérisez et partagez vos documents avec la communauté
                </p>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">🤖 Conversion IA</h5>
                <p className="card-text">
                  Conversion automatique PDF → Markdown avec OCR multi-IA
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-5">
          <Link href="/register" className="btn btn-primary btn-lg me-3">
            ✨ Créer un compte
          </Link>
          <Link href="/login" className="btn btn-outline-primary btn-lg">
            🔐 Se connecter
          </Link>
        </div>
      </div>
    </Container>
  );
}