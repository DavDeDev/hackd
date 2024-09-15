import React from 'react';

const Match = () => {
  const matches = [
    { name: 'David', role: '3rd Year Software Engineer', skills: 'Java, Python, React', photo: 'https://via.placeholder.com/150' },
    { name: 'David', role: '3rd Year Software Engineer', skills: 'Java, Python, React', photo: 'https://via.placeholder.com/150' },
    { name: 'David', role: '3rd Year Software Engineer', skills: 'Java, Python, React', photo: 'https://via.placeholder.com/150' },
    { name: 'David', role: '3rd Year Software Engineer', skills: 'Java, Python, React', photo: 'https://via.placeholder.com/150' },
    { name: 'David', role: '3rd Year Software Engineer', skills: 'Java, Python, React', photo: 'https://via.placeholder.com/150' }
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f6f1e7', padding: '2rem' }}>
      {/* Header Section */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-[#707853] mb-4">Let’s find your match!</h1>
        <div className="flex justify-center items-center mb-6">
          <img src="https://via.placeholder.com/150x150" alt="Pie Chart" className="w-60 h-60 rounded-full mr-8 shadow-lg transition-transform duration-300 hover:scale-105" />
          <div className="text-[#7f5747] text-lg font-bold bg-white p-4 rounded-lg shadow-md">
            <p>Python - 71.7%</p>
            <p>JavaScript - 22.9%</p>
            <p>Other - 2.7%</p>
          </div>
        </div>
      </div>

      {/* Middle Section - Brown Bar and White Box */}
      <div className="relative mb-10">
        <div className="bg-[#a57d57] h-4 w-full absolute top-0"></div>
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <p className="text-lg text-gray-700">
            Here are the 5 people attending <span className="text-[#fc823e] font-bold">Hack The North</span> that we think you should meet. Take the next step and reach out!
          </p>
        </div>
      </div>

      {/* Profiles Section - 3 on top, 2 on bottom */}
      <div className="grid grid-cols-3 gap-16 justify-items-center mb-8">
        {matches.slice(0, 3).map((match, index) => (
          <div
            key={index}
            className="relative bg-white p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300 transform hover:scale-105 text-center w-80"
          >
            <img
              src={match.photo}
              alt={match.name}
              className="w-24 h-24 mx-auto rounded-full mb-4"
            />
            <h2 className="text-xl font-bold mb-2">{match.name}</h2>
            <p className="text-gray-700">{match.role}</p>
            <p className="text-gray-700">{match.skills}</p>
            <a href="#" className="text-[#fc823e] mt-2 block">Contact</a>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-16 justify-items-center">
        {matches.slice(3).map((match, index) => (
          <div
            key={index}
            className="relative bg-white p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300 transform hover:scale-105 text-center w-80"
          >
            <img
              src={match.photo}
              alt={match.name}
              className="w-24 h-24 mx-auto rounded-full mb-4"
            />
            <h2 className="text-xl font-bold mb-2">{match.name}</h2>
            <p className="text-gray-700">{match.role}</p>
            <p className="text-gray-700">{match.skills}</p>
            <a href="#" className="text-[#fc823e] mt-2 block">Contact</a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Match;
