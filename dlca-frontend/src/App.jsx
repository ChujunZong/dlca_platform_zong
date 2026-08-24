
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HeroSection from './HeroSection';
import SectionTwo from './SectionTwo';
import SectionThree from './SectionThree';
import BuildingForm from './BuildingForm';
import IfcUpload from './IfcUpload'; 
import WhyChooseUs from './WhyChooseUs'; 
import HowItWorks from './HowItWorks';
import Neo4jGraphPanel from './Neo4jGraphPanel';
import Footer from './Footer';

const LandingPage = () => {
  const [showUploads, setShowUploads] = useState(false);

  const handleModelUploadClick = () => {
    setShowUploads(true);
    setTimeout(() => {
      document.getElementById('model-analysis-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div id="main-scroll-container" style={{ 
      height: '100vh',          
      width: '100%', 
      overflowY: 'scroll',      
      scrollSnapType: 'y mandatory', 
      scrollBehavior: 'smooth'  
    }}>
      
      <div style={{ scrollSnapAlign: 'start', height: '100vh', width: '100%' }}>
        <HeroSection />
      </div>

      <div id="section-two" style={{ scrollSnapAlign: 'start', height: '100vh', width: '100%' }}>
        <SectionTwo />
      </div>

      <div style={{ scrollSnapAlign: 'start', width: '100%' }}>
        <WhyChooseUs />
      </div>
      <HowItWorks />

      <div style={{ scrollSnapAlign: 'start', height: '100vh', width: '100%' }}>
        <SectionThree onModelUploadClick={handleModelUploadClick} />
      </div>
      
      {showUploads && (
        <div 
          id="model-analysis-section" 
          style={{ scrollSnapAlign: 'start', minHeight: '100vh', width: '100%', position: 'relative' }}
        >
          <IfcUpload />
        </div>
      )}


      {/*  Neo4j panel */}
      <section style={{ 
        scrollSnapAlign: 'start', 
        width: '100%', 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f0fdf4' 
      }}>
        <Neo4jGraphPanel />
      </section>


      <div style={{ scrollSnapAlign: 'end', width: '100%' }}>
        <Footer />
      </div>
    </div>
  );
};

const ToolPage = () => <BuildingForm />;

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/tool" element={<ToolPage />} />
      </Routes>
    </Router>
  );
}

export default App;