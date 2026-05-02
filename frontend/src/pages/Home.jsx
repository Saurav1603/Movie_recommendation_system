import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Search, Compass, TrendingUp, Star } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { API_BASE } from '../config';

const Home = () => {
  const [popular, setPopular] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [popRes, topRes] = await Promise.all([
          axios.get(`${API_BASE}/api/popular?limit=10`),
          axios.get(`${API_BASE}/api/top-rated?limit=6`)
        ]);
        setPopular(popRes.data);
        setTopRated(topRes.data);
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
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
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (results.length > 0) {
      handleSelectMovie(results[0].id);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="container">
      {/* Hero Section */}
      <section className="hero">
        <h1 className="gradient-text">Discover Your Next Favorite Movie</h1>
        <p>AI-powered recommendations based on what you love to watch.</p>
        
        <div className="search-container">
          <form onSubmit={handleSearchSubmit} className="search-input-wrapper">
            <Search className="search-icon" size={24} />
            <input
              type="text"
              className="search-input"
              placeholder="Search for a movie title..."
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
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{movie.year}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/browse" className="btn btn-primary">
            <Compass size={20} />
            Browse Catalog
          </Link>
        </div>
      </section>

      {/* Popular Movies Section */}
      <section className="section">
        <div className="section-header">
          <h2 className="section-title">
            <TrendingUp size={28} style={{ display: 'inline', marginRight: '0.75rem', verticalAlign: 'middle', color: 'var(--primary)' }} />
            Popular Right Now
          </h2>
          <Link to="/browse?sort_by=popularity" className="btn btn-outline" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
            View All
          </Link>
        </div>
        <div className="grid-movies">
          {popular.map(movie => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      </section>

      {/* Top Rated Section */}
      <section className="section" style={{ marginBottom: '6rem' }}>
        <div className="section-header">
          <h2 className="section-title">
            <Star size={28} style={{ display: 'inline', marginRight: '0.75rem', verticalAlign: 'middle', color: '#fbbf24' }} />
            Highest Rated
          </h2>
          <Link to="/browse?sort_by=rating" className="btn btn-outline" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
            View All
          </Link>
        </div>
        <div className="grid-movies">
          {topRated.map(movie => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
