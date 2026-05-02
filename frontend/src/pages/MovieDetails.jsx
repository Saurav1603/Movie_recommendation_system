import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Star, Calendar, Users, ThumbsUp, ArrowLeft } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { API_BASE } from '../config';

const MovieDetails = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch movie details
        const detailsRes = await axios.get(`${API_BASE}/api/movie/${id}`);
        setMovie(detailsRes.data);
        
        // Fetch recommendations
        const recsRes = await axios.get(`${API_BASE}/api/recommend/${id}`);
        if (recsRes.data && !recsRes.data.error) {
          setRecommendations(recsRes.data.recommendations);
        }
      } catch (err) {
        console.error("Error fetching details:", err);
        setError("Could not load movie details.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchDetails();
    window.scrollTo(0, 0);
  }, [id]);

  if (loading) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner"></div>
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="container" style={{ paddingTop: '4rem', textAlign: 'center' }}>
        <h2>{error || "Movie not found"}</h2>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '2rem' }}>
          Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <Link to={-1} className="btn btn-outline" style={{ display: 'inline-flex', padding: '0.5rem 1rem' }}>
          <ArrowLeft size={16} /> Back
        </Link>
      </div>

      <div className="movie-details-hero glass-card" style={{ padding: '2rem' }}>
        <div>
          <img 
            src={movie.poster_url || `https://via.placeholder.com/400x600/1e293b/ffffff?text=${encodeURIComponent(movie.clean_title)}`} 
            alt={movie.title}
            className="movie-details-poster"
            onError={(e) => {
              e.target.onerror = null; 
              e.target.src = `https://via.placeholder.com/400x600/1e293b/ffffff?text=${encodeURIComponent(movie.clean_title)}`;
            }}
          />
        </div>
        
        <div className="movie-details-info">
          <h1>{movie.clean_title}</h1>
          
          <div className="movie-details-meta">
            <div className="rating">
              <Star fill="#fbbf24" /> {movie.rating.toFixed(1)}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Calendar size={18} /> {movie.year}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Users size={18} /> {movie.vote_count.toLocaleString()} votes
            </div>
          </div>
          
          <div className="genres-wrap">
            {movie.genres.map(g => (
              <Link key={g} to={`/browse?genre=${encodeURIComponent(g)}`} className="badge">
                {g}
              </Link>
            ))}
          </div>
          
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>Overview</h3>
            <p className="overview">{movie.overview}</p>
          </div>
        </div>
      </div>

      {recommendations.length > 0 && (
        <section className="section" style={{ marginTop: '4rem' }}>
          <div className="section-header">
            <h2 className="section-title">
              <ThumbsUp size={28} style={{ display: 'inline', marginRight: '0.75rem', verticalAlign: 'middle', color: 'var(--secondary)' }} />
              More Like This
            </h2>
          </div>
          <div className="grid-movies">
            {recommendations.slice(0, 10).map(rec => (
              <MovieCard key={rec.id} movie={rec} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default MovieDetails;
