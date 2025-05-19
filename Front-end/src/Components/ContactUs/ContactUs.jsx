import React from 'react';
import './ContactUs.css'; 
import { FaPhone, FaEnvelope } from 'react-icons/fa';

const ContactUs = () => {
  const handleSubmit = (e) => {
    e.preventDefault();
    
    alert('Message is sent successfully');
  };

  return (
    <div className="contact-container">
      <div className="breadcrumb">
  Home / <span className="breadcrumb-contact">Contact</span>
</div>



      
      <div className="contact-sections">
        
        <div className="contact-info">
          <div className="contact-item">
            <FaPhone className="contact-icon" />
            <div>
              <h2>Call To Us</h2>
              <p>We are available 24/7, 7 days a week.</p>
              <p>Phone: +880181112222</p>
            </div>
          </div>

          <div className="contact-item">
            <FaEnvelope className="contact-icon" />
            <div>
              <h2>Write To Us</h2>
              <p>Fill out our form and we will contact you within 24 hours.</p>
              <p>Emails: customer@exclusive.com</p>
              <p>Emails: support@exclusive.com</p>
            </div>
          </div>
        </div>
        
        
        <div className="contact-form">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <input type="text" placeholder="Your Name *" required />
              <input type="email" placeholder="Your Email *" required />
              <input type="tel" placeholder="Your Phone *" required />
            </div>
            
            <textarea placeholder="Your Message" rows="5" required></textarea>
            
            <button type="submit" className="send-button">Send Message</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ContactUs;