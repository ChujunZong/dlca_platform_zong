import React, { useState, useEffect } from 'react';
import './HeroSection.css';

const HeroSection = () => {
  const [isScrolled, setIsScrolled] = useState(false);


  useEffect(() => {
    
    const scrollContainer = document.getElementById('main-scroll-container');
    
    if (!scrollContainer) return; 

    const handleScroll = (e) => {
      setIsScrolled(e.target.scrollTop > 100);
    };

    scrollContainer.addEventListener('scroll', handleScroll);
    
    return () => scrollContainer.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="hero">
      
      {/* =========================================
          Hero Dynamic Background
          ========================================= */}
      <div className="hero-background-orbs">
        <div className="orb orb-1"></div> 
        <div className="orb orb-2"></div> 
        <div className="noise-overlay"></div> 
      </div>


      {/* =========================================
          navibar 
          ========================================= */}
      
      
      <div className="fixed-brand">
        <div className="brand-dot"></div>
        <span className="brand-text">COMPANY</span>
      </div>

      
      <div className="fixed-contact">
        <button className="contact-btn">
          Contact Us
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>
        </button>
      </div>

      
      <nav className={`dynamic-nav ${isScrolled ? 'scrolled' : ''}`}>
        <div className="menu-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </div>
        <div className="nav-links">
          <a href="#about" className="nav-item">About</a>
          <a href="#features" className="nav-item">Features</a>
          <a href="#explore" className="nav-item">Explore</a>
        </div>
      </nav>


      {/* =========================================
           content
          ========================================= */}
      <div className="hero__content">
        <h1 className="hero__title">
          <span className="hero__line">Empowering</span>
          <span className="hero__line">Sustainable</span>
          <span className="hero__line">Progress</span>
        </h1>
        
        <div className="hero__explore">
          Explore more
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M7 13l5 5 5-5M7 6l5 5 5-5"/>
          </svg>
        </div>
      </div>

    </div>
  );
};

export default HeroSection;