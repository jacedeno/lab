# Sam Valentin - Portfolio Website

A professional Flask-based portfolio website showcasing skills, projects, and contact information.

## Features

- **Responsive Design**: Mobile-friendly layout that works on all devices
- **Modern UI**: Clean, professional design with smooth animations
- **Portfolio Showcase**: Filterable project gallery with detailed descriptions
- **Contact Form**: Interactive contact form with validation
- **About Section**: Detailed background, experience, and skills
- **Social Integration**: Links to social media profiles

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Styling**: Custom CSS with CSS Grid and Flexbox

## Project Structure

```
portfolio/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/
│   └── css/
│       └── style.css     # Custom styles
│   └── img/              # Images (add your own)
│       ├── profile.jpg   # Profile photo
│       ├── about-me.jpg  # About page image
│       ├── project1.jpg  # Project screenshots
│       ├── project2.jpg
│       ├── project3.jpg
│       ├── project4.jpg
│       ├── project5.jpg
│       └── project6.jpg
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── about.html        # About page
    ├── portfolio.html    # Portfolio page
    └── contact.html      # Contact page
```

## Setup Instructions

### 1. Clone or Download
Download the project files to your local machine.

### 2. Install Dependencies
```bash
# Navigate to the portfolio directory
cd portfolio

# Install Flask and dependencies
pip install -r requirements.txt
```

### 3. Add Images
Create an `img` folder inside the `static` directory and add the following images:
- `profile.jpg` - Your profile photo (300x300px recommended)
- `about-me.jpg` - Image for about page (400x300px recommended)
- `project1.jpg` to `project6.jpg` - Screenshots of your projects (600x400px recommended)

### 4. Customize Content
Edit the HTML templates to include your own information:
- Update personal information in `templates/index.html`
- Modify experience and education in `templates/about.html`
- Replace project details in `templates/portfolio.html`
- Update contact information in `templates/contact.html`

### 5. Run the Application
```bash
# Start the Flask development server
python app.py
```

The website will be available at `http://localhost:5000`

## Customization

### Personal Information
Update the following files with your information:
- **Name**: Update "Sam Valentin" throughout the templates
- **Contact**: Update email, phone, location in `contact.html`
- **Social Links**: Update social media URLs in `base.html` and `contact.html`
- **Bio**: Update the description and experience in `index.html` and `about.html`

### Projects
In `templates/portfolio.html`, replace the sample projects with your own:
- Update project titles, descriptions, and technologies
- Replace placeholder links with actual project URLs
- Update project categories for filtering

### Styling
Modify `static/css/style.css` to customize:
- Color scheme (update CSS variables at the top)
- Fonts and typography
- Layout and spacing
- Animations and effects

### Skills and Experience
In `templates/about.html`, update:
- Work experience timeline
- Education and certifications
- Technical skills and proficiency levels

## Deployment

### Local Development
The app runs in debug mode by default for development.

### Production Deployment
For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Set up environment variables for sensitive data
4. Use a reverse proxy like Nginx

### Platform Deployment
This Flask app can be easily deployed to:
- Heroku
- PythonAnywhere
- DigitalOcean
- AWS Elastic Beanstalk
- Google Cloud Platform

## Features to Add

Consider adding these features to enhance your portfolio:
- Blog section for technical articles
- Admin panel for content management
- Database integration for dynamic content
- Email functionality for contact form
- Analytics integration
- Dark mode toggle
- Multi-language support

## Browser Support

This website supports all modern browsers:
- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## License

This project is open source and available under the MIT License.

## Contact

For questions or suggestions about this portfolio template, feel free to reach out!
