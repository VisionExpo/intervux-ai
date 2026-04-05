import React from 'react';

export default function TrustedBrands() {
  const brands = [
    { name: 'Acme Corp', logo: 'https://cdn.worldvectorlogo.com/logos/acme-3.svg' },
    { name: 'Global Inc', logo: 'https://cdn.worldvectorlogo.com/logos/circle.svg' },
    { name: 'Tech Solutions', logo: 'https://cdn.worldvectorlogo.com/logos/edge-3.svg' },
    { name: 'Innovate LLC', logo: 'https://cdn.worldvectorlogo.com/logos/velocity-2.svg' },
    { name: 'Future Enterprises', logo: 'https://cdn.worldvectorlogo.com/logos/infinite.svg' },
  ];

  return (
    <section className="py-12 border-y border-outline-variant/20 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-sm font-medium text-on-surface-variant mb-8 uppercase tracking-wider">
          Trusted by innovative companies worldwide
        </p>
        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-60 grayscale transition-all hover:grayscale-0 sm:grayscale">
          {brands.map((brand, index) => (
            <div key={index} className="flex items-center justify-center p-4 hover:opacity-100 transition-opacity">
              <img src={brand.logo} alt={brand.name} className="h-8 md:h-10 w-auto object-contain" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
