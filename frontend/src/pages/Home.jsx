import React from 'react';
import Hero from '../Components/Hero';
import Features from '../Components/Features';
import HowItWorks from '../Components/HowItWorks';
import Stats from '../Components/Stats';
import CTA from '../Components/CTA';
import Footer from '../Components/Footer';

const Home = () => (
  <div className="min-h-screen bg-[#F7F3EE] pt-14">
    <Hero />
    <Features />
    <HowItWorks />
    <Stats />
    <CTA />
    <Footer />
  </div>
);

export default Home;
