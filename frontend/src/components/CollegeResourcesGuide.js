import React from 'react';
import './CollegeResourcesGuide.css';

const CollegeResourcesGuide = ({ onGoBack }) => {
  const resources = [
    {
      title: "Official SAT & College Planning (College Board)",
      link: "https://www.collegeboard.org/",
      description: "Official site for SAT registration, sending scores, and utilizing BigFuture for college planning, search, and career exploration."
    },
    {
      title: "Common Application",
      link: "https://www.commonapp.org/",
      description: "A standardized undergraduate college application accepted by over 1,000 member colleges and universities."
    },
    {
      title: "FAFSA (Federal Student Aid)",
      link: "https://studentaid.gov/",
      description: "The Free Application for Federal Student Aid (FAFSA) is used to apply for federal student aid, such as grants, loans, and work-study."
    },
    {
      title: "Khan Academy Official SAT Practice",
      link: "https://www.khanacademy.org/test-prep/sat",
      description: "Offers free, personalized SAT practice resources, including practice tests, instructional videos, and study plans, in partnership with the College Board."
    },
    {
      title: "Niche.com",
      link: "https://www.niche.com/",
      description: "Provides comprehensive profiles on every college and K-12 school in America, including rankings, student reviews, and scholarship information."
    },
    {
      title: "The Princeton Review",
      link: "https://www.princetonreview.com/",
      description: "Offers test preparation services, tutoring, college admissions counseling, and detailed college rankings and search tools."
    },
    {
      title: "Fastweb",
      link: "https://www.fastweb.com/",
      description: "A popular online resource for finding scholarships to help pay for school, with a database of over 1.5 million scholarships."
    },
    {
      title: "Scholarships.com",
      link: "https://www.scholarships.com/",
      description: "A free scholarship search engine with a large database of college scholarships from various sources."
    },
     {
      title: "Cappex",
      link: "https://www.cappex.com/",
      description: "Offers college and scholarship search tools, college reviews, and tools to help students estimate their chances of admission."
    },
    {
      title: "Unigo",
      link: "https://www.unigo.com/",
      description: "Provides college reviews, scholarship search, and advice for students navigating the college application process."
    }
  ];

  return (
    <div className="college-resources-guide-container">
      <div className="guide-header">
        <h1>College Application Resources</h1>
        <button onClick={onGoBack} className="back-button">Back</button>
      </div>
      <p className="resources-intro">
        Navigating the college application process can be complex. Below is a curated list of external resources
        to help you with planning, applications, financial aid, and test preparation.
      </p>

      <div className="resources-list">
        {resources.map((resource, index) => (
          <div key={index} className="resource-item">
            <h3>
              <a href={resource.link} target="_blank" rel="noopener noreferrer">
                {resource.title}
              </a>
            </h3>
            <p>{resource.description}</p>
            <a href={resource.link} target="_blank" rel="noopener noreferrer" className="resource-link">
              Visit Site <span className="external-link-icon">↗</span>
            </a>
          </div>
        ))}
      </div>

      <div className="guide-footer">
        <button onClick={onGoBack} className="back-button large-back-button">Back to Dashboard</button>
      </div>
    </div>
  );
};

export default CollegeResourcesGuide;
