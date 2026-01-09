// lib/api.js
// Service API pour communiquer avec le backend Pyramid
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6543/api';

// Instance Axios configurée
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT automatiquement
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs globales
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTIFICATION
// ============================================

export const authAPI = {
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    if (typeof window !== 'undefined' && response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    if (typeof window !== 'undefined' && response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  getCurrentUser: () => {
    if (typeof window !== 'undefined') {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    }
    return null;
  },

  isAuthenticated: () => {
    if (typeof window !== 'undefined') {
      return !!localStorage.getItem('token');
    }
    return false;
  }
};

// ============================================
// ŒUVRES
// ============================================

export const oeuvresAPI = {
  getOeuvres: async () => {
    const response = await apiClient.get('/oeuvres');
    return response.data;
  },

  deposer: async (formData) => {
    const response = await apiClient.post('/oeuvres/depot', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  deposerPDF: async (formData) => {
    const response = await apiClient.post('/oeuvres/depot-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  convertirPDF: async (pdfFile) => {
    const formData = new FormData();
    formData.append('pdf', pdfFile);
    
    const response = await apiClient.post('/oeuvres/convertir-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  traiter: async (idOeuvre) => {
    const response = await apiClient.post(`/oeuvres/${idOeuvre}/traiter`);
    return response.data;
  },

  valider: async (idOeuvre, destination = 'fond_commun') => {
    const response = await apiClient.post(`/oeuvres/${idOeuvre}/valider`, { destination });
    return response.data;
  },

  rejeter: async (idOeuvre, motif) => {
    const response = await apiClient.post(`/oeuvres/${idOeuvre}/rejeter`, { motif });
    return response.data;
  },

  reconvertir: async (idOeuvre, params = {}) => {
    const response = await apiClient.post(`/oeuvres/${idOeuvre}/reconvertir`, params);
    return response.data;
  },

  deposerMarkdown: async (formData) => {
    const response = await apiClient.post('/oeuvres/deposer-md', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
};

// ============================================
// EMPRUNTS
// ============================================

export const empruntsAPI = {
  getMesEmprunts: async () => {
    const response = await apiClient.get('/emprunts/mes-emprunts');
    return response.data;
  },

  emprunter: async (idOeuvre, dureeJours = 14) => {
    const response = await apiClient.post('/emprunts/emprunter', {
      id_oeuvre: idOeuvre,
      duree_jours: dureeJours,
    });
    return response.data;
  },

  retourner: async (idEmprunt) => {
    const response = await apiClient.post(`/emprunts/${idEmprunt}/retourner`);
    return response.data;
  },

  renouveler: async (idEmprunt, joursSupplementaires = 7) => {
    const response = await apiClient.post(`/emprunts/${idEmprunt}/renouveler`, {
      jours: joursSupplementaires
    });
    return response.data;
  }
};

// ============================================
// CATALOGUE
// ============================================

export const catalogueAPI = {
  getFondCommun: async () => {
    const response = await apiClient.get('/catalogue/fond-commun');
    return response.data;
  },

  getSequestre: async () => {
    const response = await apiClient.get('/catalogue/sequestre');
    return response.data;
  },

  getStats: async () => {
    const response = await apiClient.get('/catalogue/stats');
    return response.data;
  }
};


// ============================================
// DEMANDES DE PROMOTION
// ============================================

export const demandesAPI = {
  // Pour les MEMBRES
  
  /**
   * Soumettre une demande de promotion
   * @param {string} motivation - Pourquoi devenir bibliothécaire (min 10 chars)
   */
  soumettre: async (motivation) => {
    const response = await apiClient.post('/demandes/soumettre', { motivation });
    return response.data;
  },

  /**
   * Consulter mes demandes
   */
  mesDemandes: async () => {
    const response = await apiClient.get('/demandes/mes-demandes');
    return response.data;
  },

  /**
   * Annuler ma demande en attente
   * @param {string} idDemande - ID de la demande
   */
  annuler: async (idDemande) => {
    const response = await apiClient.post(`/demandes/${idDemande}/annuler`);
    return response.data;
  },

  // Pour les BIBLIOTHÉCAIRES

  /**
   * Lister toutes les demandes en attente (bibliothécaires)
   */
  listerEnAttente: async () => {
    const response = await apiClient.get('/demandes/en-attente');
    return response.data;
  },

  /**
   * Approuver une demande (bibliothécaires)
   * @param {string} idDemande - ID de la demande
   */
  approuver: async (idDemande) => {
    const response = await apiClient.post(`/demandes/${idDemande}/approuver`);
    return response.data;
  },

  /**
   * Refuser une demande (bibliothécaires)
   * @param {string} idDemande - ID de la demande
   * @param {string} motif - Raison du refus (min 5 chars)
   */
  refuser: async (idDemande, motif) => {
    const response = await apiClient.post(`/demandes/${idDemande}/refuser`, { motif });
    return response.data;
  },

  /**
   * Historique complet (bibliothécaires)
   * @param {number} limit - Nombre max de résultats
   */
  historique: async (limit = 50) => {
    const response = await apiClient.get(`/demandes/historique?limit=${limit}`);
    return response.data;
  },

  /**
   * Statistiques (bibliothécaires)
   */
  statistiques: async () => {
    const response = await apiClient.get('/demandes/statistiques');
    return response.data;
  }
};


export default apiClient;