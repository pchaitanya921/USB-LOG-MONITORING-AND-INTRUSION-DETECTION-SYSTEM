import { useEffect, useRef } from 'react';
import ParticleBackgroundUtil from '../utils/particleBackground';

const ParticleBackground = ({ id = 'particle-bg', options = {} }) => {
  const particleRef = useRef(null);
  
  useEffect(() => {
    // Initialize particle background
    const particleBackground = new ParticleBackgroundUtil(id, options);
    particleRef.current = particleBackground;
    
    // Cleanup on unmount
    return () => {
      if (particleRef.current) {
        particleRef.current.destroy();
      }
    };
  }, [id, options]);
  
  return (
    <div 
      id={id} 
      className="particle-container"
      style={{ 
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: -1,
        overflow: 'hidden'
      }}
    />
  );
};

export default ParticleBackground;
