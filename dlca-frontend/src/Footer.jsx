import React from 'react';
import { ArrowUpRight, AtSign, Briefcase, Code2 } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="vanguard-footer">
      <div className="vanguard-container">
        
        
        <div className="vanguard-top">
          <h2 className="mega-title">
            Ready to <span className="italic-serif">transform</span><br/> your workflow?
          </h2>
          <button className="mega-cta-btn">
            Start for free <ArrowUpRight size={24} className="btn-icon" />
          </button>
        </div>

        <div className="vanguard-divider"></div>

        <div className="vanguard-bottom">
          <div className="brand-col">
            <h3 className="vanguard-logo"><span className="logo-dot"></span> COMPANY</h3>
            <p className="vanguard-copyright">
              © {new Date().getFullYear()} Company Name.<br/>
              Paving the way for a net-zero future.
            </p>
          </div>

          <div className="links-col">
            <span className="col-label">Platform</span>
            <a href="#features">Features</a>
            <a href="#lca">LCA Engine</a>
            <a href="#upload">IFC Upload</a>
            <a href="#pricing">Pricing</a>
          </div>

          <div className="links-col">
            <span className="col-label">Socials</span>
            <a href="#twitter" className="social-link">
              <AtSign size={15} /> Twitter
            </a>
            <a href="#linkedin" className="social-link">
              <Briefcase size={15} /> LinkedIn
            </a>
            <a href="#github" className="social-link">
              <Code2 size={15} /> GitHub
            </a>
          </div>
          
          <div className="links-col">
            <span className="col-label">Contact</span>
            <a href="mailto:hello@company.com" className="highlight-link">hello@company.com</a>
            <p className="address-text">
              123 Innovation Drive,<br/>
              Tech District, CA 94105
            </p>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;