import React from 'react';
import { Link } from 'react-router-dom';
import { Star } from 'lucide-react';

const MovieCard = ({ movie }) => {
  return (
    <Link to={`/movie/${movie.id}`} className="movie-card glass-card">
      <div className="movie-poster-container">
        <img 
          src={movie.poster_url || `https://via.placeholder.com/300x450/1e293b/ffffff?text=${encodeURIComponent(movie.clean_title)}`} 
          alt={movie.title} 
          className="movie-poster"
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null; 
            e.target.src = `https://via.placeholder.com/300x450/1e293b/ffffff?text=${encodeURIComponent(movie.clean_title)}`;
          }}
        />
        <div className="movie-overlay">
          <button className="btn btn-primary" style={{ width: '100%', marginTop: 'auto' }}>
            View Details
          </button>
        </div>
        <div className="movie-rating">
          <Star size={14} fill="#fbbf24" color="#fbbf24" />
          {movie.rating.toFixed(1)}
        </div>
      </div>
      <div className="movie-info">
        <h3 className="movie-title">{movie.clean_title}</h3>
        <div className="movie-meta">
          <span>{movie.year}</span>
          {movie.similarity_score && (
            <span style={{ color: 'var(--secondary)' }}>{movie.similarity_score}% Match</span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default MovieCard;
