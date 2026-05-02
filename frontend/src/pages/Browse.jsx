import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Filter } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { API_BASE } from '../config';

const Browse = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [filters, setFilters] = useState({
    genre: searchParams.get('genre') || '',
    sort_by: searchParams.get('sort_by') || 'popularity',
    min_rating: searchParams.get('min_rating') || '0',
    year_from: searchParams.get('year_from') || '',
    year_to: searchParams.get('year_to') || '',
    runtime: searchParams.get('runtime') || '',
  });

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/genres`);
        setGenres(res.data);
      } catch (err) {
        console.error("Error fetching genres:", err);
      }
    };
    fetchGenres();
  }, []);

  useEffect(() => {
    const fetchMovies = async () => {
      setLoading(true);
      try {
        // Build query string
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
          if (value && value !== '0') {
            params.append(key, value);
          }
        });
        
        // Update URL
        setSearchParams(params);
        
        const res = await axios.get(`${API_BASE}/api/browse?${params.toString()}`);
        setMovies(res.data);
      } catch (err) {
        console.error("Error fetching filtered movies:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchMovies();
  }, [filters, setSearchParams]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleReset = () => {
    setFilters({
      genre: '',
      sort_by: 'popularity',
      min_rating: '0',
      year_from: '',
      year_to: '',
      runtime: '',
    });
  };

  return (
    <div className="container">
      <div className="section-header" style={{ marginTop: '2rem' }}>
        <h1 className="section-title">Browse Movies</h1>
      </div>

      <div className="filters-bar glass-card">
        <div className="filter-group">
          <label>Genre</label>
          <select className="input-field" name="genre" value={filters.genre} onChange={handleChange}>
            <option value="">All Genres</option>
            {genres.map(g => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </div>
        
        <div className="filter-group">
          <label>Sort By</label>
          <select className="input-field" name="sort_by" value={filters.sort_by} onChange={handleChange}>
            <option value="popularity">Most Popular</option>
            <option value="rating">Highest Rated</option>
            <option value="year_desc">Newest First</option>
            <option value="year_asc">Oldest First</option>
            <option value="title">A-Z</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Min Rating</label>
          <select className="input-field" name="min_rating" value={filters.min_rating} onChange={handleChange}>
            <option value="0">Any Rating</option>
            <option value="5">5+ Stars</option>
            <option value="6">6+ Stars</option>
            <option value="7">7+ Stars</option>
            <option value="8">8+ Stars</option>
            <option value="9">9+ Stars</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Release Year</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="number" 
              className="input-field" 
              placeholder="From" 
              name="year_from" 
              value={filters.year_from} 
              onChange={handleChange}
              min="1900" max="2026"
            />
            <input 
              type="number" 
              className="input-field" 
              placeholder="To" 
              name="year_to" 
              value={filters.year_to} 
              onChange={handleChange}
              min="1900" max="2026"
            />
          </div>
        </div>

        <div className="filter-group" style={{ flex: 'none', display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-end' }}>
          <button className="btn btn-outline" onClick={handleReset} style={{ padding: '0.75rem 1.25rem' }}>
            <Filter size={16} />
            Reset
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0' }}>
          <div className="spinner"></div>
        </div>
      ) : movies.length > 0 ? (
        <div className="grid-movies">
          {movies.map(movie => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '4rem', textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>No movies found</h3>
          <p style={{ color: 'var(--text-muted)' }}>Try adjusting your filters to find what you're looking for.</p>
          <button className="btn btn-primary" onClick={handleReset} style={{ marginTop: '2rem' }}>
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
};

export default Browse;
