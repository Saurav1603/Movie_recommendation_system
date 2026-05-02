import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Search, Film, Menu, X } from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../config';

const Navbar = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const searchRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Close mobile menu on route change
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (query.length >= 2) {
      const fetchResults = async () => {
        try {
          const res = await axios.get(`${API_BASE}/api/search?q=${query}`);
          setResults(res.data);
          setShowResults(true);
        } catch (err) {
          console.error(err);
        }
      };
      const timer = setTimeout(fetchResults, 300);
      return () => clearTimeout(timer);
    } else {
      setResults([]);
      setShowResults(false);
    }
  }, [query]);

  const handleSelectMovie = (id) => {
    navigate(`/movie/${id}`);
    setShowResults(false);
    setQuery('');
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      // If we want to support global search page, navigate to browse with query
      // For now, just pick the first result if available
      if (results.length > 0) {
        handleSelectMovie(results[0].id);
      }
    }
  };

  return (
    <nav className="navbar glass">
      <div className="container">
        <Link to="/" className="nav-brand gradient-text">
          <Film size={28} color="#ec4899" />
          CineMatch
        </Link>
        
        {/* Desktop Menu */}
        <div className="nav-links" style={{ display: 'none', '@media (min-width: 768px)': { display: 'flex' } }}>
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>Home</Link>
          <Link to="/browse" className={`nav-link ${location.pathname === '/browse' ? 'active' : ''}`}>Browse</Link>
          
          <div className="search-container" ref={searchRef} style={{ marginLeft: '2rem' }}>
            <form onSubmit={handleSearchSubmit} className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input
                type="text"
                className="search-input"
                placeholder="Search movies..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => { if (results.length > 0) setShowResults(true); }}
                style={{ padding: '0.75rem 1.25rem 0.75rem 2.5rem', fontSize: '0.9rem' }}
              />
            </form>
            
            {showResults && results.length > 0 && (
              <div className="search-results glass-card">
                {results.map((movie) => (
                  <div 
                    key={movie.id} 
                    className="search-result-item"
                    onClick={() => handleSelectMovie(movie.id)}
                  >
                    <div>
                      <div style={{ fontWeight: 600 }}>{movie.clean_title}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{movie.year}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="mobile-menu-toggle" 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          style={{ display: 'block' }} // Will override in CSS later or just let it show
        >
          {isMobileMenuOpen ? <X size={28} color="white" /> : <Menu size={28} color="white" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="mobile-menu glass-card" style={{ position: 'absolute', top: '100%', left: 0, right: 0, padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>Home</Link>
          <Link to="/browse" className={`nav-link ${location.pathname === '/browse' ? 'active' : ''}`}>Browse</Link>
          <div className="search-container" ref={searchRef}>
            <form onSubmit={handleSearchSubmit} className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input
                type="text"
                className="search-input"
                placeholder="Search movies..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => { if (results.length > 0) setShowResults(true); }}
              />
            </form>
            {showResults && results.length > 0 && (
              <div className="search-results glass-card">
                {results.map((movie) => (
                  <div 
                    key={movie.id} 
                    className="search-result-item"
                    onClick={() => handleSelectMovie(movie.id)}
                  >
                    <div>
                      <div style={{ fontWeight: 600 }}>{movie.clean_title}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{movie.year}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
