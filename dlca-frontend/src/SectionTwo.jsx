import React, { useState, useEffect } from 'react';
import './SectionTwo.css';

import img1 from './assets/img1.jpg';
import img2 from './assets/img2.jpg';
import img3 from './assets/img3.jpg';


const TypewriterText = ({ text, speed = 30, isActive, onComplete }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    // 如果还没轮到这一行（未激活），就不执行任何操作
    if (!isActive) return;

    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText(text.substring(0, i + 1));
      i++;
      
      if (i >= text.length) {
        clearInterval(interval);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, text, speed]); // 依赖项里监听 isActive 的变化

  return <>{displayedText}</>;
};

const SectionTwo = () => {
  const [typingStep, setTypingStep] = useState(1);

  return (
    <section className="s2-container">
      <div className="s2-ambient-bg">
        <div className="s2-blob blob-sustain"></div>
        <div className="s2-blob blob-tech"></div>
      </div>

      <div className="s2-content-wrapper">
        
        <div className="s2-visual-gallery">
          <img src={img1} className="s2-glass-img s2-img-main" alt="Sustainable Building Main" />
          <img src={img2} className="s2-glass-img s2-img-sub-1" alt="Sustainable Details" />
          <img src={img3} className="s2-glass-img s2-img-sub-2" alt="Green Architecture" />
        </div>

        <div className="s2-text-panel">
          <h2 className="s2-editorial-title">
            <span className="s2-title-sans">The New Standard of</span><br/>
            <span className="s2-title-serif gradient-green">Sustainable Design.</span>
          </h2>
          
          <div className="s2-desc-box">
            <p className="s2-highlight">
              <TypewriterText 
                text="We bridge the gap between complex Dynamic Lifecycle Assessment and intuitive design. Data meets aesthetics." 
                isActive={typingStep >= 1}
                onComplete={() => setTypingStep(2)}
              />
            </p>
            
            
            <p>
              <TypewriterText 
                text="Real-time carbon analysis integrated into your workflow. Transform static numbers into actionable insights instantly." 
                isActive={typingStep >= 2}
                onComplete={() => setTypingStep(3)}
              />
            </p>
            
            
            <p>
              <TypewriterText 
                text="Empowering architects to build with purpose. Paving the way for a resilient, net-zero future." 
                isActive={typingStep >= 3}
              />
            </p>
          </div>
        </div>

      </div>
    </section>
  );
};

export default SectionTwo;