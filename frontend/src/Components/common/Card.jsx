import React from 'react';

const Card = ({ children, className = '', hover = false }) => (
  <div className={`bg-white rounded-2xl border border-[#E8E1D8] p-6 ${hover ? 'hover:shadow-md hover:border-transparent transition-all' : ''} ${className}`}>
    {children}
  </div>
);

export default Card;
