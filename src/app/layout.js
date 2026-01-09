// app/layout.js
'use client';

import 'bootstrap/dist/css/bootstrap.min.css'
import './globals.css'


import { usePathname, useRouter } from 'next/navigation';
import { Navbar as BSNavbar, Nav, Container, Button } from 'react-bootstrap';
import Link from 'next/link';
import { authAPI } from '@/lib/api';
import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css';
import { useEffect, useState } from 'react';

function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    setIsAuthenticated(authAPI.isAuthenticated());
    setUser(authAPI.getCurrentUser());
  }, [pathname]);

  const handleLogout = () => {
    authAPI.logout();
    router.push('/login');
  };

  const isBibliothecaire = user?.roles?.includes('Bibliothécaire');

  return (
    <BSNavbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container>
        <BSNavbar.Brand as={Link} href="/">
          📚 Biblioteko
        </BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            {isAuthenticated && (
              <>
                <Nav.Link as={Link} href="/catalogue">
                  Catalogue
                </Nav.Link>
                <Nav.Link as={Link} href="/depot">
                  Déposer une œuvre
                </Nav.Link>
                <Nav.Link as={Link} href="/emprunts">
                  Mes Emprunts
                </Nav.Link>
                {isBibliothecaire && (
                  <Nav.Link as={Link} href="/moderation">
                    🔍 Modération
                  </Nav.Link>
                )}
              </>
            )}
          </Nav>
          <Nav>
            {isAuthenticated ? (
              <>
                <BSNavbar.Text className="me-3">
                  👤 {user?.prenom} {user?.nom}
                </BSNavbar.Text>
                <Button variant="outline-light" size="sm" onClick={handleLogout}>
                  Déconnexion
                </Button>
              </>
            ) : (
              <>
                <Nav.Link as={Link} href="/login">
                  Connexion
                </Nav.Link>
                <Nav.Link as={Link} href="/register">
                  Inscription
                </Nav.Link>
              </>
            )}
          </Nav>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>
        <Navbar />
        <main>{children}</main>
        <footer className="bg-light text-center py-4 mt-5">
          <Container>
            <p className="text-muted mb-0">
              © 2026 CultureDiffusion - Biblioteko | Projet pédagogique AUP
            </p>
          </Container>
        </footer>
      </body>
    </html>
  );
}